# ==== inbox_tab.py ====
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox, QPushButton, QTabWidget
from PyQt5.QtCore import pyqtSignal
import requests
from components.email import EmailDialog
from datetime import datetime

class InboxTab(QWidget):
    reply_requested = pyqtSignal(dict)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.trash_manual = []

        main_layout = QVBoxLayout()
        self.tabs = QTabWidget()

        self.normal_tab, self.normal_layout = self.create_tab()
        self.tabs.addTab(self.normal_tab, "\U0001F4E5 正常信件")

        self.spam_tab, self.spam_layout = self.create_tab()
        self.tabs.addTab(self.spam_tab, "\U0001F5D1️ 垃圾信件")

        self.trash_tab, self.trash_layout = self.create_tab()
        self.tabs.addTab(self.trash_tab, "\U0001F9F9 垃圾桶")

        reload_btn = QPushButton("\U0001F504 重新整理")
        reload_btn.clicked.connect(self.load_emails)

        main_layout.addWidget(reload_btn)
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        self.load_emails()

    def create_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        email_layout = QVBoxLayout()
        container.setLayout(email_layout)

        scroll.setWidget(container)
        layout.addWidget(scroll)
        tab.setLayout(layout)
        return tab, email_layout

    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def load_emails(self):
        for layout in [self.normal_layout, self.spam_layout, self.trash_layout]:
            self.clear_layout(layout)

        r = requests.post("http://localhost:8080/fetch", data={"username": self.username, "mode": "receive"})

        if r.status_code != 200 or r.json().get("status") != "ok":
            self.normal_layout.addWidget(QLabel("⚠️ 無法載入信件"))
            return

        for email in r.json().get("emails", []):
            email_id = email.get("id", email.get("uid", "unknown"))
            box = QGroupBox()
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"From: {email['sender']}"))
            layout.addWidget(QLabel(f"Title: {email['title']}"))
            layout.addWidget(QLabel(f"Content: {email['content']}"))
            ts = float(email['timestamp'])
            layout.addWidget(QLabel(f"Time: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))

            detail_btn = QPushButton("🔍 查看內容")
            detail_btn.clicked.connect(lambda _, e=email: EmailDialog(e).exec_())
            layout.addWidget(detail_btn)

            trash_btn = QPushButton("🗑️ 丟到垃圾桶")
            trash_btn.clicked.connect(lambda _, eid=email_id: self.move_to_trash(eid))
            layout.addWidget(trash_btn)

            box.setLayout(layout)
            if email_id in self.trash_manual or email.get("user_type") == "trash":
                self.trash_layout.addWidget(box)
            elif email.get("system_type") == "spam":
                self.spam_layout.addWidget(box)
            else:
                self.normal_layout.addWidget(box)

    def move_to_trash(self, email_id):
        if email_id not in self.trash_manual:
            self.trash_manual.append(email_id)
            requests.post("http://localhost:8080/trash", data={"email_id": email_id})
        self.load_emails()
