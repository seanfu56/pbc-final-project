# ==== widgets/image_with_caption.py ====
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsBlurEffect
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QByteArray
import base64

class ImageWithCaptionWidget(QWidget):
    def __init__(self, base64_img: str, caption: str):
        super().__init__()

        self.is_revealed = False

        # Decode base64 image
        img_data = base64.b64decode(base64_img)
        qimg = QImage.fromData(QByteArray(img_data))
        self.pixmap = QPixmap.fromImage(qimg)

        # Display blurred image
        self.image_label = QLabel()
        self.image_label.setPixmap(self.pixmap.scaledToWidth(400, Qt.SmoothTransformation))
        self.image_label.setCursor(Qt.PointingHandCursor)
        self.image_label.mousePressEvent = self.reveal_image

        # Add blur effect
        self.blur = QGraphicsBlurEffect()
        self.blur.setBlurRadius(15)
        self.image_label.setGraphicsEffect(self.blur)

        # Caption
        self.caption_label = QLabel(caption)
        self.caption_label.setStyleSheet("color: gray; font-style: italic;")
        self.caption_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.caption_label)
        self.setLayout(layout)

    def reveal_image(self, event):
        if not self.is_revealed:
            self.image_label.setGraphicsEffect(None)
            self.caption_label.setStyleSheet("color: black; font-weight: bold;")
            self.is_revealed = True