import sqlite3
import bcrypt
import uuid
import json
from typing import List, Union
from datetime import datetime

def delete_user_table():
    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS users")
    conn.commit()
    conn.close()

def create_user_table():
    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            sends TEXT,
            receives TEXT,
            drafts TEXT
        )
    ''')
    conn.commit()
    conn.close()

def create_user(username: str, password: str):
    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("Username already exists.")
    else:
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        cursor.execute("INSERT INTO users (username, password, sends, receives, drafts) VALUES (?, ?, ?, ?, ?)", (username, hashed_pw, json.dumps([]), json.dumps([]), json.dumps([])))
        conn.commit()
        print("Account created successfully.")

    conn.close()

def login(username: str, input_password: str):

    success = False

    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))

    result = cursor.fetchone()

    if result:
        correct_password = result[0]
        if bcrypt.checkpw(input_password.encode(), correct_password):
            print("Login success")
            success = True
        else:
            print("Wrong password")
    else:
        print("Login failed")

    conn.close()

    return success

def delete_email_table():
    conn = sqlite3.connect('assets/emails.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS emails")
    conn.commit()
    conn.close()

def create_email_table():
    conn = sqlite3.connect('assets/emails.db')
    cursor = conn.cursor()
    '''
    system type: normal / spam
    user type: normal / junk
    '''
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            uid TEXT UNIQUE NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL,
            system_type TEXT NOT NULL,
            user_type TEXT NOT NULL,
            images TEXT
        )
    ''')
    conn.commit()
    conn.close()    

def user_exist(username: str):
    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    exist = cursor.fetchone()

    conn.close()

    if exist:
        return True
    else:
        return False
    
def process_image(images: Union[None, List[str]], email_uid: str):

    if images is None:
        return json.dumps([])
    
    else:

        uid_list = []

        conn = sqlite3.connect('assets/images.db')
        cursor = conn.cursor()

        for image in images:

            uid = str(uuid.uuid4())

            cursor.execute('''
                INSERT INTO images (uid, email_uid, img_str)
                VALUES (?, ?, ?)
                ''', (uid, email_uid, image))
            
            uid_list.append(uid)

        conn.commit()
        conn.close()

        return json.dumps(uid_list)

        

def send_email(sender: str, receiver: str, title: str, content: str, system_type: str, image: Union[None, List[str]]):

    if user_exist(sender) and user_exist(receiver):

        user_type = 'normal'

        uid = str(uuid.uuid4())
        timestamp = float(datetime.now().timestamp())

        image_uid = process_image(image, uid)

        conn = sqlite3.connect('assets/emails.db')
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO emails (uid, sender, receiver, title, content, timestamp, system_type, user_type, images)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (uid, sender, receiver, title, content, timestamp, system_type, user_type, image_uid))
        
        conn.commit()
        conn.close()

        conn_sender = sqlite3.connect('assets/users.db')
        cursor_sender = conn_sender.cursor()

        cursor_sender.execute("SELECT sends FROM users WHERE username = ?", (sender,))
        send_list = cursor_sender.fetchone()
        email_id_list = json.loads(send_list[0])

        email_id_list.append(uid)

        send_list_update = json.dumps(email_id_list)

        cursor_sender.execute("UPDATE users SET sends = ? WHERE username = ?", (send_list_update, sender))

        conn_sender.commit()
        conn_sender.close()

        conn_receiver = sqlite3.connect('assets/users.db')
        cursor_receiver = conn_receiver.cursor()

        cursor_receiver.execute("SELECT receives FROM users WHERE username = ?", (receiver,))
        receive_list = cursor_receiver.fetchone()
        email_id_list = json.loads(receive_list[0])
        
        email_id_list.append(uid)

        receive_list_update = json.dumps(email_id_list)

        cursor_receiver.execute("UPDATE users SET receives = ? WHERE username = ?", (receive_list_update, receiver))

        conn_receiver.commit()
        conn_receiver.close()

        print("email sent!")

        return True
    
    else:

        return False 

def fetch_all_email(mode: str, username: str):

    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()
    
    if mode == 'send':
        cursor.execute("SELECT sends FROM users WHERE username = ?", (username,))
    else:
        cursor.execute("SELECT receives FROM users WHERE username = ?", (username,))

    result = cursor.fetchone()

    conn.close()

    if result:

        uid_list = json.loads(result[0])

        conn_email = sqlite3.connect('assets/emails.db')

        cursor_email = conn_email.cursor()

        email_list = []

        for uid in uid_list:
            cursor_email.execute("SELECT * FROM emails WHERE uid = ?", (uid,))
            email = cursor_email.fetchone()
            email_list.append(email)

        return email_list
    
    else:
        return None
    
def change_email_user_type(mode: str, id: str):
    conn = sqlite3.connect('assets/emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emails WHERE uid = ?', (id, ))

    email_user_type = cursor.fetchone()

    print("CHANGE EMAIL USER TYPE", email_user_type)

    if email_user_type is not None:
        if mode == 'trash':
            cursor.execute('UPDATE emails SET user_type = ? WHERE uid = ?', ('trash', id))
            print("PUT A EMAIL INTO TRASH CAN")

    conn.commit()
    conn.close()
    
def delete_draft_table():
    conn = sqlite3.connect('assets/drafts.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS drafts')
    conn.commit()
    conn.close()

def create_draft_table():
    conn = sqlite3.connect('assets/drafts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drafts (
            uid TEXT UNIQUE NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL,
            images TEXT
        )
    ''')
    conn.commit()
    conn.close()


def send_draft(sender: str, receiver: str, title: str, content: str, image: Union[ None, str, List[str]]):

    uid = str(uuid.uuid4())
    timestamp = float(datetime.now().timestamp())

    conn = sqlite3.connect('assets/drafts.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO drafts (uid, sender, receiver, title, content, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (uid, sender, receiver, title, content, timestamp,))
    
    conn.commit()
    conn.close()

    conn_sender = sqlite3.connect('assets/users.db')
    cursor_sender = conn_sender.cursor()

    cursor_sender.execute("SELECT drafts FROM users WHERE username = ?", (sender,))
    send_list = cursor_sender.fetchone()
    email_id_list = json.loads(send_list[0])

    email_id_list.append(uid)

    send_list_update = json.dumps(email_id_list)

    cursor_sender.execute("UPDATE users SET drafts = ? WHERE username = ?", (send_list_update, sender))

    conn_sender.commit()
    conn_sender.close()

    print("email draft stored!")

    return True

def fetch_all_draft(username: str):

    conn = sqlite3.connect('assets/users.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT drafts FROM users WHERE username = ?", (username,))

    result = cursor.fetchone()

    conn.close()

    print("fetch_all_draft: ", result)

    if result:

        uid_list = json.loads(result[0])

        conn_email = sqlite3.connect('assets/drafts.db')

        cursor_email = conn_email.cursor()

        email_list = []

        for uid in uid_list:
            cursor_email.execute("SELECT * FROM drafts WHERE uid = ?", (uid,))
            email = cursor_email.fetchone()
            email_list.append(email)

        return email_list
    
    else:
        return None
    
def delete_image_table():
    conn = sqlite3.connect('assets/images.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS images")
    conn.commit()
    conn.close()

def create_image_table():
    conn = sqlite3.connect('assets/images.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            uid TEXT UNIQUE NOT NULL,
            email_uid TEXT NOT NULL,
            img_str TEXT NOT NULL 
        )
    ''')
    conn.commit()
    conn.close()

def get_image(uid):

    conn = sqlite3.connect('assets/images.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM images WHERE uid = ?', (uid, ))

    image = cursor.fetchone()

    conn.close()

    return image

