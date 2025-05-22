from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGroupBox, QDialog,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QStackedWidget, QTabWidget, QSizePolicy, QSplitter, QApplication, QFormLayout, QColorDialog,
    QInputDialog, QDialogButtonBox, QComboBox, QFontDialog, 
)
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QImage, QFont, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QByteArray, pyqtSignal, QSignalBlocker, QPropertyAnimation, QSize, QTimer
import llama_cpp

class DiscussionDialog(QDialog):
    def __init__(self, email_content, parent=None):
        super().__init__(parent)
        self.setWindowTitle("與 LLaMA 討論郵件內容")
        self.resize(500, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.history = QTextEdit()
        self.history.setReadOnly(True)
        layout.addWidget(self.history)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("輸入你想問 LLaMA 的問題")
        layout.addWidget(self.input_box)

        send_button = QPushButton("發送")
        send_button.clicked.connect(self.send_to_llama)
        layout.addWidget(send_button)

        self.history.append(f"<b>📧 Email Content:</b>\n{email_content}\n")

    def send_to_llama(self):
        question = self.input_box.text().strip()
        if not question:
            return
        self.history.append(f"<b>🧑 你：</b> {question}")
        self.input_box.clear()
        context = self.history.toPlainText()

        try:
            repo_name = 'TheBloke/LLaMA-7b-GGUF'
            model_path = 'llama-7b.Q4_K_M.gguf'

            llm = llama_cpp.Llama.from_pretrained(
                repo_id=repo_name,
                filename=model_path,
                verbose=False
            )
            
            response = llm(f"{context}\n\nLLaMA Response:", max_tokens=30)
            answer = response['choices'][0]['text'].split('.')[0]
            self.history.append(f"<b>🤖 LLaMA：</b> {answer}")
        except Exception as e:
            self.history.append(f"<b>錯誤：</b> {str(e)}")