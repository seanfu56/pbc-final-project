import sqlite3
import bcrypt
import uuid
import json
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
            receives TEXT
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
        cursor.execute("INSERT INTO users (username, password, sends, receives) VALUES (?, ?, ?, ?)", (username, hashed_pw, json.dumps([]), json.dumps([])))
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            uid TEXT UNIQUE NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()    

def send_email(sender: str, receiver: str, title: str, content: str):

    uid = str(uuid.uuid4())
    timestamp = float(datetime.now().timestamp())

    conn = sqlite3.connect('assets/emails.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO emails (uid, sender, receiver, title, content, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (uid, sender, receiver, title, content, timestamp))
    
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

def fetch_all_email(mode: str, username: str):
    pass