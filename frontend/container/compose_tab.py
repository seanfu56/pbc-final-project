from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox, QLineEdit, QTextEdit, QPushButton, QMessageBox
import requests
from datetime import datetime

class ComposeTab(QWidget):
    def __init__(self, sender_username):
        super().__init__()
        layout = QVBoxLayout()

        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("收件人帳號")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("信件標題")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("信件內容")

        send_button = QPushButton("寄出")
        send_button.clicked.connect(lambda: self.send_email(sender_username))

        layout.addWidget(QLabel("\ud83d\udce4 寄信"))
        layout.addWidget(self.receiver_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.content_input)
        layout.addWidget(send_button)

        self.setLayout(layout)

    def send_email(self, sender):
        r = requests.post("http://localhost:8080/send", data={
            "sender": sender,
            "receiver": self.receiver_input.text(),
            "title": self.title_input.text(),
            "content": self.content_input.toPlainText()
        })
        if r.status_code == 200 and r.json().get("status") == "ok":
            QMessageBox.information(self, "成功", "信件已寄出！")
            self.receiver_input.clear()
            self.title_input.clear()
            self.content_input.clear()
        else:
            QMessageBox.warning(self, "失敗", "寄信失敗，請檢查輸入")
