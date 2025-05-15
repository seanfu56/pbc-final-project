from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox,
    QDialog, QTextEdit, QPushButton, QTabWidget
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QByteArray
import requests
from datetime import datetime
import base64


def base64_to_pixmap(base64_str: str) -> QPixmap:
    img_data = base64.b64decode(base64_str)
    qimg = QImage.fromData(QByteArray(img_data))
    return QPixmap.fromImage(qimg)


class InboxTab(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.trash_manual = []  # 使用者手動丟到垃圾桶的信件 ID

        main_layout = QVBoxLayout()

        # 🔄 重新整理按鈕
        reload_button = QPushButton("🔄 重新整理")
        reload_button.clicked.connect(self.load_emails)
        main_layout.addWidget(reload_button)

        # 📑 Tab 控制（正常、垃圾信件、垃圾桶）
        self.tabs = QTabWidget()

        self.normal_tab, self.normal_layout = self.create_tab()
        self.tabs.addTab(self.normal_tab, "📥 正常信件")

        self.spam_tab, self.spam_layout = self.create_tab()
        self.tabs.addTab(self.spam_tab, "🗑️ 垃圾信件")

        self.trash_tab, self.trash_layout = self.create_tab()
        self.tabs.addTab(self.trash_tab, "🧺 垃圾桶")

        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.load_emails()

    def create_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        email_layout = QVBoxLayout()
        content.setLayout(email_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        tab.setLayout(layout)
        return tab, email_layout

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def load_emails(self):
        # 清空所有 layout
        for layout in [self.normal_layout, self.spam_layout, self.trash_layout]:
            self.clear_layout(layout)

        r = requests.post("http://localhost:8080/fetch", data={
            "username": self.username,
            "mode": "receive"
        })

        if r.status_code == 200 and r.json().get("status") == "ok":
            for email in r.json().get("emails", []):
                email_id = email.get("id", email['uid'])  # 使用 id 或 timestamp 當作唯一識別

                box = QGroupBox()
                box_layout = QVBoxLayout()
                box_layout.addWidget(QLabel(f"From: {email['sender']}"))
                box_layout.addWidget(QLabel(f"Title: {email['title']}"))
                box_layout.addWidget(QLabel(f"Content: {email['content']}"))
                ts = float(email['timestamp'])
                box_layout.addWidget(QLabel(
                    f"Time: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))

                # 詳細內容點擊事件
                box.mousePressEvent = lambda event, mail=email: self.show_full_email(mail)

                # 🗑️ 丟到垃圾桶按鈕
                trash_btn = QPushButton("🗑️ 丟到垃圾桶")
                trash_btn.clicked.connect(lambda _, eid=email_id: self.move_to_trash(eid))
                box_layout.addWidget(trash_btn)

                box.setLayout(box_layout)
                print(email.get('user_type'), email.get('system_type'))
                if email_id in self.trash_manual or email.get('user_type')=='trash':
                    self.trash_layout.addWidget(box)
                elif email.get("system_type") == "spam":
                    self.spam_layout.addWidget(box)
                else:
                    self.normal_layout.addWidget(box)
        else:
            self.normal_layout.addWidget(QLabel("⚠️ 無法載入信件"))

    def move_to_trash(self, email_id):
        if email_id not in self.trash_manual:
            self.trash_manual.append(email_id)
            r = requests.post("http://localhost:8080/trash", data={
                "email_id": email_id,
            })
        self.load_emails()

    def show_full_email(self, email):
        dlg = QDialog(self)
        dlg.setWindowTitle("📧 信件內容")
        dlg.resize(600, 500)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"📨 寄件者: {email['sender']}"))
        layout.addWidget(QLabel(f"📝 標題: {email['title']}"))

        ts = float(email['timestamp'])
        layout.addWidget(QLabel(f"🕒 時間: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))

        # 顯示內容
        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        content_edit.setText(email['content'])
        layout.addWidget(content_edit)

        # 顯示圖片（若有）
        image_list = email.get("image_list", [])
        if image_list:
            layout.addWidget(QLabel("🖼️ 附件圖片："))
            for idx, img_str in enumerate(image_list):
                try:
                    pixmap = base64_to_pixmap(img_str)
                    img_label = QLabel()
                    img_label.setPixmap(pixmap.scaledToWidth(400))
                    layout.addWidget(img_label)
                except Exception as e:
                    layout.addWidget(QLabel(f"⚠️ 圖片 {idx+1} 載入失敗：{e}"))

        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(dlg.accept)
        layout.addWidget(close_btn)

        dlg.setLayout(layout)
        dlg.exec_()