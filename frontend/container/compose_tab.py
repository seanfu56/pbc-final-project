from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QFileDialog, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
import base64
import requests
from datetime import datetime

class ComposeTab(QWidget):
    def __init__(self, sender_username):
        super().__init__()
        self.sender_username = sender_username
        self.image_list = []  # base64 字串 list

        layout = QVBoxLayout()

        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("收件人帳號")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("信件標題")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("信件內容")

        # 附件區域
        attach_layout = QHBoxLayout()
        attach_button = QPushButton("附加圖片")
        attach_button.clicked.connect(self.attach_image)
        self.attachment_preview = QLabel()  # 顯示縮圖
        attach_layout.addWidget(attach_button)
        attach_layout.addWidget(self.attachment_preview)

        # 發送 / 草稿按鈕
        send_button = QPushButton("寄出")
        send_button.clicked.connect(self.send_email)

        store_button = QPushButton('儲存草稿')
        store_button.clicked.connect(self.send_draft)

        layout.addWidget(QLabel("📤 寄信"))
        layout.addWidget(self.receiver_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.content_input)
        layout.addLayout(attach_layout)
        layout.addWidget(send_button)
        layout.addWidget(store_button)

        self.setLayout(layout)

    def attach_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇圖片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                self.image_list.append(encoded)

            # 顯示預覽圖
            pixmap = QPixmap(file_path)
            self.attachment_preview.setPixmap(pixmap.scaledToWidth(100))

    def send_email(self):
        r = requests.post("http://localhost:8080/send", json={
            "sender": self.sender_username,
            "receiver": self.receiver_input.text(),
            "title": self.title_input.text(),
            "content": self.content_input.toPlainText(),
            "image_list": self.image_list  # 加入圖片
        })
        print(self.image_list)
        if r.status_code == 200 and r.json().get("status") == "ok":
            QMessageBox.information(self, "成功", "信件已寄出！")
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "失敗", "寄信失敗，請檢查輸入")

    def send_draft(self):
        r = requests.post("http://localhost:8080/draft", json={
            "sender": self.sender_username,
            "receiver": self.receiver_input.text(),
            "title": self.title_input.text(),
            "content": self.content_input.toPlainText(),
            "image_list": self.image_list  # 加入圖片
        })
        if r.status_code == 200 and r.json().get("status") == "ok":
            QMessageBox.information(self, "成功", "草稿已儲存！")
            self.clear_inputs()
        else:
            QMessageBox.warning(self, "失敗", "儲存草稿失敗，請檢查輸入")

    def load_email(self, email):
        self.receiver_input.setText(email['receiver'])
        self.title_input.setText(email['title'])
        self.content_input.setText(email['content'])
        self.image_list = email.get("image_list", [])
        self.attachment_preview.clear()
        if self.image_list:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self.image_list[0]))
            self.attachment_preview.setPixmap(pixmap.scaledToWidth(100))

    def clear_inputs(self):
        self.receiver_input.clear()
        self.title_input.clear()
        self.content_input.clear()
        self.image_list = []
        self.attachment_preview.clear()