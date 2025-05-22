from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox, QHBoxLayout
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor
from PyQt5.QtCore import Qt, QTimer
import requests
import llama_cpp
import time
from transformers import pipeline
# ========================== 主介面類別 ==========================
class ComposeTab(QWidget):
    def __init__(self, sender_username):
        super().__init__()
        self.sender_username = sender_username

        # ==================== UI 設定 ====================
        layout = QVBoxLayout()

        self.receiver_input = QLineEdit()
        self.receiver_input.setPlaceholderText("收件人帳號")

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("信件標題")

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("信件內容")
        self.content_input.textChanged.connect(self.handle_text_changed)
        self.content_input.installEventFilter(self)

        send_button = QPushButton("寄出")
        send_button.clicked.connect(self.send_email)

        self.toggle_button = QPushButton("預測：開啟")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_prediction)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.toggle_button)
        button_layout.addWidget(send_button)

        layout.addWidget(QLabel("寄信"))
        layout.addWidget(self.receiver_input)
        layout.addWidget(self.title_input)
        layout.addWidget(self.content_input)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.trigger_suggestion)

        # ========================== 初始化模型與狀態 ==========================
        self.init_model()
        self.init_state()

    # ========================== 模型初始化 ==========================
    def init_model(self):

        model_tag = "pszemraj/opt-350m-email-generation"
        self.generator = pipeline(
                    'text-generation', 
                    model=model_tag, 
                    use_fast=False,
                    do_sample=False,
                    early_stopping=True,
                    )
                    

    # ========================== 預測狀態初始化 ==========================
    def init_state(self):
        self.user_text = ""
        self.suggestion = ""
        self.prediction_enabled = True
        self.prediction_start_pos = None
        self.is_handling_preview = False

    # ========================== 切換預測功能開關 ==========================
    def toggle_prediction(self):
        self.prediction_enabled = self.toggle_button.isChecked()
        if self.prediction_enabled:
            self.toggle_button.setText("預測：開啟")
        else:
            self.toggle_button.setText("預測：關閉")
            self.clear_prediction()

    # ========================== 使用者輸入變動時處理 ==========================
    def handle_text_changed(self):
        if not self.prediction_enabled or self.is_handling_preview:
            return

        current_text = self.get_user_text_only()
        if self.suggestion:
            self.clear_prediction()

        if current_text != self.user_text:
            self.user_text = current_text
            self.clear_prediction()
            self.debounce_timer.start(400)

    # ========================== 執行文字預測 ==========================
    def trigger_suggestion(self):
        if not self.prediction_enabled:
            return

        input_text = self.user_text.strip()
        if len(input_text) < 10:
            self.clear_prediction()
            return

        prompt = input_text
        

        try:
            outputs = self.generator(prompt, max_new_tokens=5)
            generated_tokens = outputs[0]['generated_text']
            print(generated_tokens)
            generated = generated_tokens.strip()

            # 嘗試移除與 user_text 重疊的開頭部分
            overlap_len = len(self.user_text)
            if generated.startswith(self.user_text):
                generated = generated[overlap_len:]

            # 進一步移除完全重複的片段（例如模型重複輸出了一句）
            for i in range(len(self.user_text)):
                suffix = self.user_text[i:]
                if generated.startswith(suffix):
                    generated = generated[len(suffix):]
                    break

            self.suggestion = generated
            
        except Exception as e:
            print("產生建議時發生錯誤：", e)
            self.suggestion = ""

        self.update_preview()

    # ========================== 顯示預測文字 ==========================
    def update_preview(self):
        if not self.suggestion:
            self.clear_prediction()
            return

        self.is_handling_preview = True

        cursor = self.content_input.textCursor()
        original_position = cursor.position()

        cursor.movePosition(QTextCursor.End)
        self.prediction_start_pos = cursor.position()

        fmt = QTextCharFormat()
        fmt.setForeground(QColor("gray"))
        cursor.insertText(self.suggestion, fmt)

        cursor.setPosition(original_position)
        self.content_input.setTextCursor(cursor)

        self.is_handling_preview = False

    # ========================== 取得使用者真實輸入（不含預測） ==========================
    def get_user_text_only(self):
        if self.prediction_start_pos is None:
            return self.content_input.toPlainText()
        else:
            cursor = self.content_input.textCursor()
            cursor.setPosition(0)
            cursor.setPosition(self.prediction_start_pos, QTextCursor.KeepAnchor)
            return cursor.selectedText()

    # ========================== 清除預測文字 ==========================
    def clear_prediction(self):
        if self.prediction_start_pos is not None:
            self.is_handling_preview = True
            cursor = self.content_input.textCursor()
            cursor.setPosition(self.prediction_start_pos)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            self.prediction_start_pos = None
            self.suggestion = ""
            self.is_handling_preview = False
   
    # ==========================
    def apply_suggestion(self):
        if not self.suggestion or self.prediction_start_pos is None:
            return

        self.is_handling_preview = True

        cursor = self.content_input.textCursor()
        cursor.beginEditBlock()

        # 移除灰色預測文字
        cursor.setPosition(self.prediction_start_pos)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.removeSelectedText()

        # 插入黑色正式文字
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("black"))
        cursor.insertText(self.suggestion, fmt)

        cursor.endEditBlock()

        # 更新狀態
        self.user_text = self.get_user_text_only()
        self.suggestion = ""
        self.prediction_start_pos = None
        self.is_handling_preview = False

        # 重新啟動預測
        self.debounce_timer.start(400)

    # ========================== 處理鍵盤事件（包含 Tab 鍵） ==========================
    def eventFilter(self, obj, event):
        if obj == self.content_input and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Tab and self.suggestion:
                self.apply_suggestion()
                return True  # 告訴 Qt：事件已處理，不要再傳給其他元件
            elif event.key() in [Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Backspace, Qt.Key_Delete]:
                if self.suggestion:
                    self.clear_prediction()
        return super().eventFilter(obj, event)

    # ========================== 發送信件功能 ==========================
    def send_email(self):
        r = requests.post("http://localhost:8080/send", data={
            "sender": self.sender_username,
            "receiver": self.receiver_input.text(),
            "title": self.title_input.text(),
            "content": self.get_user_text_only()
        })
        if r.status_code == 200 and r.json().get("status") == "ok":
            QMessageBox.information(self, "成功", "信件已寄出！")
            self.receiver_input.clear()
            self.title_input.clear()
            self.content_input.clear()
            self.user_text = ""
            self.clear_prediction()
        else:
            QMessageBox.warning(self, "失敗", "寄信失敗，請檢查輸入")
