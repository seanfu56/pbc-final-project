from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
)
import sys
import requests

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
        self.main_window = QWidget()
        self.main_window.setWindowTitle("主畫面")
        layout = QVBoxLayout()
        layout.addWidget(QLabel("登入成功！歡迎使用"))
        logout_button = QPushButton("登出")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)
        self.main_window.setLayout(layout)
        self.main_window.resize(300, 150)
        self.main_window.show()

    def logout(self):
        self.main_window.close()
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())