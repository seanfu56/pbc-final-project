# ==== dialogs/email_dialog.py ====
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
from datetime import datetime
from components.image import ImageWithCaptionWidget

class EmailDialog(QDialog):
    def __init__(self, email: dict):
        super().__init__()
        self.setWindowTitle("\U0001F4E7 信件內容")
        self.resize(600, 500)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"\U0001F4E8 寄件者: {email['sender']}"))
        layout.addWidget(QLabel(f"\U0001F4DD 標題: {email['title']}"))

        ts = float(email['timestamp'])
        layout.addWidget(QLabel(f"\U0001F552 時間: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"))

        content_edit = QTextEdit()
        content_edit.setReadOnly(True)
        content_edit.setText(email['content'])
        layout.addWidget(content_edit)

        # Show images with captions
        image_list = email.get("image_list", [])
        if image_list:
            layout.addWidget(QLabel("\U0001F5BC️ 附件圖片："))
            for idx, img_str in enumerate(image_list):
                fake_caption = f"AI caption for image {idx+1}"  # TODO: Replace with real caption
                layout.addWidget(ImageWithCaptionWidget(img_str, fake_caption))

        close_btn = QPushButton("關閉")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        self.setLayout(layout)

