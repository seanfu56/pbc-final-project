from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox, QDialog, QPushButton, QTextEdit
from datetime import datetime
import requests

class SentTab(QWidget):
    def __init__(self, username):
        super().__init__()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        email_layout = QVBoxLayout()
        content.setLayout(email_layout)

        r = requests.post("http://localhost:8080/fetch", data={"username": username, "mode": "send"})
        if r.status_code == 200 and r.json().get("status") == "ok":
            for email in r.json().get("emails", []):
                box = QGroupBox()
                box_layout = QVBoxLayout()
                box_layout.addWidget(QLabel(f"To: {email['receiver']}"))
                box_layout.addWidget(QLabel(f"Title: {email['title']}"))
                box_layout.addWidget(QLabel(f"Content: {email['content']}"))
                ts = float(email['timestamp'])
                box_layout.addWidget(QLabel(f"Time: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))
                box.mousePressEvent = lambda e, mail=email: self.show_full_email(mail)
                box.setLayout(box_layout)
                email_layout.addWidget(box)
        else:
            email_layout.addWidget(QLabel("\u2757 無法載入寄件備份"))

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)


    def show_full_email(self, email):
        dlg = QDialog(self)
        dlg.setWindowTitle("📧 信件內容")
        dlg.resize(500, 400)

        layout = QVBoxLayout()

        layout.addWidget(QLabel(f"🧑‍💼 收件者: {email['receiver']}"))
        layout.addWidget(QLabel(f"📝 標題: {email['title']}"))

        ts = float(email['timestamp'])
        layout.addWidget(QLabel(f"🕒 時間: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))

        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        content_edit.setText(email['content'])
        layout.addWidget(content_edit)

        # 加上退出按鈕
        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)
        dlg.exec_()