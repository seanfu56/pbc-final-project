import db_api

db_api.delete_user_table()
db_api.create_user_table()
db_api.create_user(
    username='andy',
    password='12345'
)
db_api.create_user(
    username='ben',
    password='23456'
)
db_api.delete_email_table()
db_api.create_email_table()
db_api.send_email(
    sender='andy',
    receiver='ben',
    title='Test Email',
    content='Just for testing'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 2',
    content='Just for testing, too.'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 3',
    content='Just for testing xxxxx, too.'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 4',
    content='Just for testing ooooo, too.'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 5',
    content='Just for testing sdafsdaf, too.'
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 666',
    content='Just for testing, too. \n\n WWW'
)