from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QScrollArea, QGroupBox, QTabWidget
)
import sys
import requests
import datetime

from container.compose_tab import ComposeTab
from container.receive_tab import InboxTab
from container.send_tab import SentTab
from container.draft_tab import DraftTab

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login system")
        self.resize(300, 200)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("username")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.create_button = QPushButton("sign up")
        self.create_button.clicked.connect(self.create_account)
        self.layout.addWidget(self.create_button)

        self.message_label = QLabel("")
        self.layout.addWidget(self.message_label)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            r = requests.post("http://localhost:8080/login", data={"username": username, "password": password})
            if r.status_code == 200 and r.json().get("status") == "ok":
                self.goto_main_window()
            elif r.status_code == 200 and r.json().get("status") == "fail":
                self.message_label.setText("failed to login")
            else:
                self.message_label.setText("error")
        except Exception as e:
            self.message_label.setText(f"connection failed: {e}")

    def create_account(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            r = requests.post("http://localhost:8080/create", data={"username": username, "password": password})
            msg = r.json().get("msg", "帳號建立成功")
            self.message_label.setText(msg)
        except Exception as e:
            self.message_label.setText(f"連線錯誤：{e}")

    def goto_main_window(self):
        self.hide()
        username = self.username_input.text()

        self.main_window = QWidget()
        self.main_window.setWindowTitle("信箱系統")
        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        self.inbox_tab = InboxTab(username)
        self.sent_tab = SentTab(username)
        self.compose_tab = ComposeTab(username)
        self.draft_tab = DraftTab(username)

        # 當草稿被選取時，切換到撰寫頁並填入資料
        self.draft_tab.draft_selected.connect(self.handle_draft_selected)

        self.tabs.addTab(self.inbox_tab, "📥 收件匣")
        self.tabs.addTab(self.sent_tab, "📤 已寄信")
        self.tabs.addTab(self.draft_tab, "草稿")
        self.tabs.addTab(self.compose_tab, "✉️ 寫新信")
        layout.addWidget(self.tabs)

        logout_btn = QPushButton("登出")
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)

        self.main_window.setLayout(layout)
        self.main_window.resize(600, 600)
        self.main_window.show()
        
    def logout(self):
        self.main_window.close()
        self.show()

    def handle_draft_selected(self, email):
        self.compose_tab.load_email(email)
        self.tabs.setCurrentWidget(self.compose_tab)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())