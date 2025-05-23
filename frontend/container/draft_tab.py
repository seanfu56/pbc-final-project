from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGroupBox, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
import requests
from datetime import datetime

class DraftTab(QWidget):
    draft_selected = pyqtSignal(dict)   
    def __init__(self, username):
        super().__init__()
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        email_layout = QVBoxLayout()
        content.setLayout(email_layout)

        r = requests.post("http://localhost:8080/fetch_draft", data={"username": username})
        if r.status_code == 200 and r.json().get("status") == "ok":
            for email in r.json().get("emails", []):
                box = QGroupBox()
                box_layout = QVBoxLayout()
                box_layout.addWidget(QLabel(f"To: {email['receiver']}"))
                box_layout.addWidget(QLabel(f"Title: {email['title']}"))
                box_layout.addWidget(QLabel(f"Content: {email['content']}"))
                ts = float(email['timestamp'])
                box_layout.addWidget(QLabel(f"Time: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))
                box.mousePressEvent = lambda event, e=email: self.draft_selected.emit(e)
                box.setLayout(box_layout)
                email_layout.addWidget(box)
        else:
            email_layout.addWidget(QLabel("\u2757 無法載入寄件備份"))

        scroll.setWidget(content)
        layout.addWidget(scroll)
        self.setLayout(layout)
