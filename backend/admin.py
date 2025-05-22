import base64

import db_api


def img_file_to_str(img_path: str) -> str:
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return [encoded_string]

db_api.delete_user_table()
db_api.create_user_table()
db_api.delete_email_table()
db_api.create_email_table()
db_api.delete_draft_table()
db_api.create_draft_table()
db_api.delete_image_table()
db_api.create_image_table()

db_api.create_user(
    username='andy',
    password='12345'
)
db_api.create_user(
    username='ben',
    password='23456'
)
db_api.create_user(
    username='cindy',
    password='34567'
)

db_api.create_category(
    username='andy',
    category='工作',
    color='#FF0000'
)

db_api.create_category(
    username='andy',
    category='學校',
    color='#00FF00'
)

db_api.create_category(
    username='andy',
    category='居家',
    color='#0000FF'
)

db_api.create_category(
    username='andy',
    category='測試',
    color='#ABCDEF'
)

db_api.send_email(
    sender='andy',
    receiver='ben',
    title='Test Email',
    content='Just for testing',
    system_type='spam',
    image=img_file_to_str('assets/figs/cat.png')
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 2',
    content='Just for testing, too.',
    system_type='spam',
    image=img_file_to_str('assets/figs/vase.png'),
    category='工作'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 3',
    content='Just for testing xxxxx, too.',
    system_type='normal',
    image=img_file_to_str('assets/figs/forest.png'),
    category='學校'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 4',
    content='I would like to invite you to the conference next Wednesday held in Vancouver.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 5',
    content='Just for testing sdafsdaf, too.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 666',
    content='Just for testing, too. \n\n WWW',
    system_type='normal',
    image=None
)


db_api.send_draft(
    sender='andy',
    receiver='ben',
    title='Test Email 66666',
    content='Hahahaahahahah',
    image=None
)

db_api.send_draft(
    sender='andy',
    receiver='cindy',
    title='Test for draft',
    content='hohohohoho',
    image=None
)
