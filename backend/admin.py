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
    username='Stony Brook University',
    password='17549'
)
db_api.create_user(
    username='Purdue University',
    password='52211'
)
db_api.create_user(
    username='University of Washington',
    password='39125'
)
db_api.create_user(
    username='University of Pennsylvania',
    password='66104'
)
db_api.create_user(
    username='University of Pittsburgh',
    password='39890'
)
db_api.create_user(
    username='Carnegie Mellon University',
    password='7707'
)
db_api.create_user(
    username='California Polytechnic State University',
    password='30995'
)
db_api.create_user(
    username='Oregon State University',
    password='30995'
)
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
    system_type='normal',
    image=img_file_to_str('assets/figs/vase.png'),
    category='工作'
)

db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Hello',
    content='How are you!',
    system_type='normal',
    image=img_file_to_str('assets/figs/vase.png'),
    category='工作'
)

db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Test Email 3',
    content='Just for testing xxxxx, too.',
    system_type='normal',
    image=img_file_to_str('assets/figs/gun.png'),
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
db_api.send_email(
    sender='Stony Brook University',
    receiver='andy',
    title='Congratulations on Your Admission to Stony Brook CS',
    content='Dear Andy,\n\nCongratulations! We are pleased to inform you that you have been admitted to the Computer Science undergraduate program at Stony Brook University for the upcoming academic year.\n\nWelcome to the Seawolf family!\n\nSincerely,\nOffice of Admissions,\nStony Brook University.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='Purdue University',
    receiver='andy',
    title='Admission Offer from Purdue University',
    content='Dear Andy,\n\nCongratulations! We are excited to inform you that you have been admitted to the Data Science undergraduate program at Purdue University for the upcoming academic year.\n\nWelcome to the Boilermaker community!\n\nSincerely,\nOffice of Admissions,\nPurdue University.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='University of Washington',
    receiver='andy',
    title='Application Decision from University of Washington',
    content='Dear Andy,\n\nThank you for your interest in the Computer Science program at the University of Washington. After careful review, we regret to inform you that we are unable to offer you admission at this time.\n\nWe appreciate your efforts and wish you success in your future endeavors.\n\nSincerely,\nOffice of Admissions,\nUniversity of Washington.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='University of Pennsylvania',
    receiver='andy',
    title='Admission Decision from University of Pennsylvania',
    content='Dear Andy,\n\nThank you for your interest in the Computer Science program at the University of Pennsylvania. After thorough consideration, we regret to inform you that we are unable to offer you admission at this time.\n\nWe appreciate your hard work and wish you the best in your future academic endeavors.\n\nSincerely,\nOffice of Admissions,\nUniversity of Pennsylvania.',
    system_type='normal',
    image=None
)

db_api.send_email(
    sender='University of Pittsburgh',
    receiver='cindy',
    title='PhD Admission and Full Scholarship Award from University of Pittsburgh',
    content='Dear Cindy,\n\nCongratulations! We are pleased to offer you admission to the Electrical Engineering PhD program at the University of Pittsburgh. In addition, you have been awarded a full scholarship covering your tuition and stipend.\n\nWelcome to the Panther research community!\n\nSincerely,\nGraduate Admissions Office,\nUniversity of Pittsburgh.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='Carnegie Mellon University',
    receiver='cindy',
    title='PhD Admission and Full Funding from Carnegie Mellon University',
    content='Dear Cindy,\n\nCongratulations! We are excited to offer you admission to the Electrical and Computer Engineering PhD program at Carnegie Mellon University. You have also been awarded full funding covering tuition and living stipend.\n\nWelcome to the CMU community!\n\nSincerely,\nGraduate Admissions Office,\nCarnegie Mellon University.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='California Polytechnic State University',
    receiver='cindy',
    title='PhD Admission and Full Ride Scholarship at Cal Poly',
    content='Dear Cindy,\n\nCongratulations! We are delighted to offer you admission to the Electrical Engineering PhD program at California Polytechnic State University. You have been awarded a full ride scholarship covering tuition and living expenses.\n\nWelcome to the Cal Poly community!\n\nSincerely,\nGraduate Admissions Office,\nCalifornia Polytechnic State University.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='Oregon State University',
    receiver='andy',
    title='PhD Admission with Full Funding and RA Position at Oregon State University',
    content='Dear Cindy,\n\nCongratulations! We are pleased to offer you admission to the Electrical Engineering PhD program at Oregon State University. You have also been awarded full funding along with a Research Assistantship position.\n\nWelcome to the Beaver community!\n\nSincerely,\nGraduate Admissions Office,\nOregon State University.',
    system_type='normal',
    image=None
)

db_api.send_email(
    sender='Stony Brook University',
    receiver='ben',
    title='Join Stony Brook University Your Future Starts Here!',
    content='Explore world-class programs and vibrant campus life at Stony Brook University! Apply now for Fall 2025 and receive exclusive application fee waivers. Don’t wait—secure your spot today and become a Seawolf!',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='Purdue University',
    receiver='ben',
    title='Boost Your Skills This Summer at Purdue University!',
    content='Enroll in Purdue University Summer School and accelerate your academic progress! Choose from a variety of courses with flexible schedules and expert instructors. Register now to secure your spot and get early bird discounts!',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='University of Washington',
    receiver='ben',
    title='Get Ahead with University of Washington Summer School!',
    content='Take advantage of University of Washington Summer School courses to earn credits faster and explore new subjects. Flexible online and in-person options available. Register today and jumpstart your academic journey!',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='University of Pennsylvania',
    receiver='ben',
    title='Congratulations on Your Admission to Wharton School!',
    content='Dear Ben, congratulations! We are thrilled to offer you admission to the Wharton School at the University of Pennsylvania for the upcoming academic year. Welcome to the Penn community! Sincerely, Office of Admissions, University of Pennsylvania.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='University of Pittsburgh',
    receiver='andy',
    title='Admission and Scholarship Award from University of Pittsburgh',
    content='Dear Andy, congratulations! We are pleased to offer you admission to the Computer Science undergraduate program at the University of Pittsburgh. Additionally, you have been awarded a scholarship covering 50 precent  of your tuition fees. Welcome to the Panther family! Sincerely, Office of Admissions, University of Pittsburgh.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='Carnegie Mellon University',
    receiver='andy',
    title='Decision on Your Transfer Request to CMU Qatar',
    content='Dear Andy, congratulations on your admission to Carnegie Mellon University. However, after careful review, we regret to inform you that your request to transfer to the Qatar campus cannot be approved at this time. We look forward to welcoming you to the Pittsburgh campus. Sincerely, Office of Admissions, Carnegie Mellon University.',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='California Polytechnic State University',
    receiver='andy',
    title='Unlock Your Future at Cal Poly Apply Now!',
    content='Discover endless opportunities at California Polytechnic State University! Limited spots available for Fall 2025 enrollment. Apply today and jumpstart your career with our top-ranked programs. Don not miss out  visit our website now!',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='Oregon State University',
    receiver='andy',
    title='Start Your Journey with Oregon State Pathway Programs!',
    content='Looking to boost your chances for university admission? Oregon State University’s Pathway programs offer personalized support and guaranteed progression. Enroll now and take the fast track to your dream degree! Limited spots available  act fast!',
    system_type='normal',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Meeting Schedule Update',
    content='The meeting has been moved to 3 PM. Let me know if that works.',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Thinking About Subscribing to Netflix',
    content='''Hey, have you tried Netflix recently? I'm thinking about subscribing this month, but not sure if it's worth it. Let me know what you think!''',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='You Should Totally Consider UT Austin CS',
    content='''Hey andy, I’ve been looking into CS programs lately, and UT Austin really stands out. Their faculty is strong, tons of research opportunities, and the tech scene in Austin is booming. If you’re still deciding where to apply, I think it’s definitely worth checking out!''',
    system_type='spam',
    image=None
)
db_api.send_email(
    sender='ben',
    receiver='andy',
    title='Berkeley EECS is Next-Level',
    content='''Hey andy, if you are aiming high, you should really look into Berkeley's EECS program. It’s super competitive, but the professors are top-tier and the alumni network is insane. Plus, being right next to Silicon Valley opens up tons of internship and startup opportunities.''',
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
