import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QGroupBox, QDialog,
    QLineEdit, QTextEdit, QPushButton, QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QStackedWidget, QTabWidget, QSizePolicy, QSplitter, QApplication, QFormLayout, QColorDialog,
    QInputDialog, QDialogButtonBox, QComboBox, QFontDialog, 
)
from PyQt5.QtGui import QPixmap, QIcon, QColor, QPainter, QImage, QFont, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QByteArray, pyqtSignal, QSignalBlocker, QPropertyAnimation, QSize, QTimer
import base64
import requests
from datetime import datetime
import time
from transformers import pipeline
import json

from container.ai_helper import DiscussionDialog

# 登入窗口類
class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login System")
        self.resize(300, 200)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.create_button = QPushButton("Sign Up")
        self.create_button.clicked.connect(self.create_account)
        self.layout.addWidget(self.create_button)

        self.message_label = QLabel("")
        self.layout.addWidget(self.message_label)

        self.setLayout(self.layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            print(f"Sending login request: username={username}")
            r = requests.post("http://localhost:8080/login", data={"username": username, "password": password})
            print(f"Login response: status_code={r.status_code}, response={r.text}")
            if r.status_code == 200 and r.json().get("status") == "ok":
                categories = r.json().get("categories")
                categories = json.loads(categories)
                print("categories: ", categories)
                self.goto_main_window(username, categories)
            elif r.status_code == 200 and r.json().get("status") == "fail":
                self.message_label.setText("Failed to login: Incorrect username or password")
            else:
                self.message_label.setText("Error: Server returned an unexpected response")
        except requests.exceptions.RequestException as e:
            self.message_label.setText(f"Connection failed: {str(e)}")

    def create_account(self):
        username = self.username_input.text()
        password = self.password_input.text()
        try:
            print(f"Sending sign-up request: username={username}")
            r = requests.post("http://localhost:8080/create", data={"username": username, "password": password})
            print(f"Sign-up response: status_code={r.status_code}, response={r.text}")
            msg = r.json().get("msg", "Account created successfully")
            self.message_label.setText(msg)
        except requests.exceptions.RequestException as e:
            self.message_label.setText(f"Connection error: {str(e)}")

    def goto_main_window(self, username, categories):
        self.hide()
        self.main_window = MailSystem(username, categories)
        self.main_window.logout_signal.connect(self.show)
        self.main_window.show()

# 類別管理對話框
class CategoryDialog(QDialog):
    def __init__(self, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理類別")
        self.categories = categories
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.category_list = QListWidget()
        self.category_list.setDragEnabled(True)
        self.category_list.setAcceptDrops(True)
        self.category_list.setDragDropMode(QListWidget.InternalMove)
        self.category_list.model().rowsMoved.connect(self.update_categories_order)
        self.update_category_list()
        self.layout.addWidget(self.category_list)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("新增類別")
        add_btn.clicked.connect(self.add_category)
        delete_btn = QPushButton("刪除選中類別")
        delete_btn.clicked.connect(self.delete_category)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        self.layout.addLayout(btn_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout.addWidget(buttons)

    def update_category_list(self):
        self.category_list.clear()
        if not self.categories:
            self.category_list.addItem("無類別")
            return
        for name, color in self.categories:
            item = QListWidgetItem(name)
            pixmap = QPixmap(12, 12)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 12, 12)
            painter.end()
            item.setIcon(QIcon(pixmap))
            self.category_list.addItem(item)
        self.category_list.repaint()

    def update_categories_order(self):
        new_order = []
        for i in range(self.category_list.count()):
            item = self.category_list.item(i)
            name = item.text()
            if name != "無類別":
                color = next((cat[1] for cat in self.categories if cat[0] == name), None)
                if color:
                    new_order.append([name, color])
        self.categories[:] = new_order
        self.update_category_list()

    def add_category(self):
        name, ok = QInputDialog.getText(self, "新增類別", "輸入類別名稱：")
        if not ok or not name.strip():
            QMessageBox.warning(self, "錯誤", "類別名稱不能為空")
            return
        name = name.strip()
        if any(cat[0] == name for cat in self.categories):
            QMessageBox.warning(self, "錯誤", "類別名稱已存在")
            return
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.categories.append([name, color.name()])

            self.update_category_list()

    def delete_category(self):
        selected = self.category_list.selectedItems()
        if not selected:
            QMessageBox.warning(self, "錯誤", "請選擇一個類別")
            return
        category = selected[0].text()
        self.categories[:] = [cat for cat in self.categories if cat[0] != category]
        self.update_category_list()

    def accept(self):
        super().accept()
        if hasattr(self.parent(), 'refresh_ui'):
            self.parent().refresh_ui()

# 自定義郵件列表
class CustomEmailList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setSelectionBehavior(QListWidget.SelectItems)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)

# 撰寫郵件標籤
class ComposeTab(QWidget):
    def __init__(self, sender_username, mail_system):
        super().__init__()
        self.sender_username = sender_username
        self.mail_system = mail_system
        self.image_list = []

        layout = QVBoxLayout()
        layout.setSpacing(8)

        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText("收件人帳號")
        layout.addWidget(self.to_input)

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("信件標題")
        layout.addWidget(self.subject_input)

        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("信件內容")
        self.content_input.textChanged.connect(self.handle_text_changed)
        self.content_input.installEventFilter(self)
        layout.addWidget(self.content_input, stretch=1)

        # 附件區域
        attach_layout = QHBoxLayout()
        attach_button = QPushButton("附加圖片")
        attach_button.clicked.connect(self.attach_image)
        self.attachment_preview = QLabel()
        attach_layout.addWidget(attach_button)
        attach_layout.addWidget(self.attachment_preview)
        layout.addLayout(attach_layout)

        # 按鈕區域
        btn_layout = QHBoxLayout()
        send_button = QPushButton("寄出")
        send_button.clicked.connect(self.send_email)
        self.toggle_button = QPushButton("預測：開啟")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_prediction)

        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.trigger_suggestion)

        store_button = QPushButton("儲存草稿")
        store_button.clicked.connect(self.send_draft)
        close_button = QPushButton("關閉")
        close_button.clicked.connect(lambda: self.mail_system.hide_compose())
        btn_layout.addWidget(send_button)
        btn_layout.addWidget(self.toggle_button)
        btn_layout.addWidget(store_button)
        btn_layout.addWidget(close_button)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        model_tag = 'pszemraj/opt-350m-email-generation'
        self.generator = pipeline(
            'text-generation',
            model=model_tag,
            use_fast = False,
            do_sample = False,
            early_stopping = True,
        )

        self.init_state()

    def init_state(self):
        self.user_text = ""
        self.suggestion = ""
        self.prediction_enabled = True
        self.prediction_start_pos = None
        self.is_handling_preview = False
        self.last_predict_time = time.time()

    def toggle_prediction(self):
        self.prediction_enabled = self.toggle_button.isChecked()
        if self.prediction_enabled:
            self.toggle_button.setText("預測：開啟")
        else:
            self.toggle_button.setText("預測：關閉")
            self.clear_prediction()

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

        now = time.time()
        print(now - self.last_predict_time)
        if now - self.last_predict_time < 3:
            return
        else:
            self.last_predict_time = now

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
        print("call apply suggestion")
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
    

    def attach_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "選擇圖片", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)")
        if file_path:
            with open(file_path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                self.image_list.append(encoded)
            pixmap = QPixmap(file_path)
            self.attachment_preview.setPixmap(pixmap.scaledToWidth(100))

    def send_email(self):
        try:
            payload = {
                "sender": self.sender_username,
                "receiver": self.to_input.text(),
                "title": self.subject_input.text(),
                "content": self.content_input.toPlainText(),
                "image_list": self.image_list
            }
            print(f"Sending email with payload: {payload}")
            r = requests.post("http://localhost:8080/send", json=payload)
            print(f"Response from /send: status_code={r.status_code}, response={r.text}")
            if r.status_code == 200 and r.json().get("status") == "ok":
                QMessageBox.information(self, "成功", "信件已寄出！")
                self.clear_inputs()
                self.mail_system.hide_compose()
                self.mail_system.refresh_ui()
            else:
                QMessageBox.warning(self, "失敗", f"寄信失敗：{r.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")

    def send_draft(self):
        try:
            payload = {
                "sender": self.sender_username,
                "receiver": self.to_input.text(),
                "title": self.subject_input.text(),
                "content": self.content_input.toPlainText(),
                "image_list": self.image_list
            }
            print(f"Saving draft with payload: {payload}")
            r = requests.post("http://localhost:8080/draft", json=payload)
            print(f"Response from /draft: status_code={r.status_code}, response={r.text}")
            if r.status_code == 200 and r.json().get("status") == "ok":
                QMessageBox.information(self, "成功", "草稿已儲存！")
                self.clear_inputs()
                self.mail_system.hide_compose()
                self.mail_system.refresh_ui()
            else:
                QMessageBox.warning(self, "失敗",  f"儲存草稿失敗：{r.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")

    def load_email(self, email):
        self.to_input.setText(email.get('receiver', ''))
        self.subject_input.setText(email.get('title', ''))
        self.content_input.setText(email.get('content', ''))
        self.image_list = email.get("image_list", [])
        self.attachment_preview.clear()
        if self.image_list:
            pixmap = QPixmap()
            pixmap.loadFromData(base64.b64decode(self.image_list[0]))
            self.attachment_preview.setPixmap(pixmap.scaledToWidth(100))

    def clear_inputs(self):
        self.to_input.clear()
        self.subject_input.clear()
        self.content_input.clear()
        self.image_list = []
        self.attachment_preview.clear()

# 主窗口類
class MailSystem(QMainWindow):
    logout_signal = pyqtSignal()

    def __init__(self, username, categories):
        super().__init__()
        print(f"Initializing MailSystem for {username} at {datetime.now()}")
        self.setWindowTitle("郵件系統")
        self.setGeometry(100, 100, 1000, 600)
        self.username = username
        self.current_folder = "inbox"
        self.search_query = ""
        self.filter_type = "all"
        self.content_keyword = ""
        self.selection_mode = False
        self.current_email = None
        self.categories = [
            ["工作", "#FF0000"],
            ["學校", "#00FF00"],
            ["居家", "#0000FF"]
        ]
        self.categories = categories
        self.trash_manual = []
        self.sidebar_expanded = False
        self.is_displaying_email = False
        self.emails = []

        # QSS 樣式表
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QListWidget {
                border: 1px solid #d0d0d0;
                background: #ffffff;
                padding: 5px;
            }
            QListWidget::item:selected {
                background: #e6f3ff;
                color: #000000;
            }
            QListWidget::item {
                padding: 3px;
                color: #000000;
            }
            QListWidget#sidebarMenu::item {
                padding: 8px;
            }
            QListWidget#sidebarMenu::item:hover {
                background: #f0f0f0;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                background: #ffffff;
                color: #000000;
            }
            QPushButton {
                padding: 5px 15px;
                border-radius: 4px;
                background: #0078d4;
                color: #ffffff;
                border: none;
                min-width: 80px;
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
            QPushButton:hover:!disabled {
                background: #005a9e;
            }
            QPushButton:pressed:!disabled {
                background: #003c6b;
            }
            QPushButton#toggleBtn {
                padding: 5px;
                font-size: 16px;
                background: #f5f5f5;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                min-width: 30px;
                min-height: 30px;
            }
            QPushButton#toggleBtn:hover {
                background: #e0e0e0;
            }
            QWidget#emailContentWidget {
                border: none;
                background: #fafafa;
                padding: 10px;
                border-radius: 4px;
            }
            QLabel {
                color: #000000;
                background: transparent;
            }
            QTextEdit {
                color: #000000;
                background: #ffffff;
                border: 1px solid #d0d0d0;
            }
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                background: #ffffff;
                min-width: 150px;
            }
            QComboBox:hover {
                background: #f0f0f0;
            }
            QComboBox::drop-down {
                width: 20px;
                border-left: 1px solid #d0d0d0;
            }
            QComboBox QAbstractItemView {
                min-width: 150px;
            }
            QWidget#searchCategoryWidget {
                background: #f5f5f5;
                border-bottom: 1px solid #d0d0d0;
                padding: 5px;
            }
            QWidget#sidebarWidget {
                background: #f5f5f5;
                border-right: 1px solid #d0d0d0;
            }
            QSplitter::handle {
                background: #d0d0d0;
                width: 5px;
            }
            QSplitter::handle:hover {
                background: #a0a0a0;
            }
        """)

        # 主容器
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_h_layout = QHBoxLayout()
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)
        self.central_widget.setLayout(self.main_h_layout)

        # 漢堡按鈕
        self.toggle_btn = QPushButton("☰")
        self.toggle_btn.setObjectName("toggleBtn")
        self.toggle_btn.setFixedSize(30, 30)
        self.toggle_btn.clicked.connect(self.toggle_sidebar)
        self.main_h_layout.addWidget(self.toggle_btn)

        # 隱藏式選單
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setObjectName("sidebarWidget")
        self.sidebar_widget.setFixedWidth(0)
        self.sidebar_widget.setVisible(False)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(5, 5, 5, 5)
        self.sidebar_widget.setLayout(self.sidebar_layout)
        self.main_h_layout.addWidget(self.sidebar_widget)

        self.sidebar_menu = QListWidget()
        self.sidebar_menu.setObjectName("sidebarMenu")
        self.sidebar_menu.itemClicked.connect(self.handle_sidebar_click)
        self.update_sidebar_menu()
        self.sidebar_layout.addWidget(self.sidebar_menu)

        # 內容容器
        self.content_container_widget = QWidget()
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.content_container_widget.setLayout(self.main_layout)
        self.main_h_layout.addWidget(self.content_container_widget, stretch=1)

        # 搜尋和操作區域
        self.search_category_widget = QWidget()
        self.search_category_widget.setObjectName("searchCategoryWidget")
        self.search_category_layout = QHBoxLayout()
        self.search_category_layout.setSpacing(15)
        self.search_category_widget.setLayout(self.search_category_layout)
        self.main_layout.addWidget(self.search_category_widget)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索郵件（發件人或主旨）")
        self.search_input.textChanged.connect(self.search_emails)
        self.search_category_layout.addWidget(self.search_input)

        # 篩選下拉菜單
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "全部", "最近一周", "已讀郵件", "未讀郵件", "內容關鍵字"
        ])
        self.filter_combo.currentTextChanged.connect(self.filter_emails)
        self.search_category_layout.addWidget(self.filter_combo)

        # 內容關鍵字輸入框
        self.content_keyword_input = QLineEdit()
        self.content_keyword_input.setPlaceholderText("輸入內容關鍵字")
        self.content_keyword_input.textChanged.connect(self.update_content_keyword)
        self.content_keyword_input.hide()
        self.search_category_layout.addWidget(self.content_keyword_input)

        # 重新整理按鈕
        self.refresh_btn = QPushButton("重新整理")
        self.refresh_btn.clicked.connect(self.refresh_emails)
        self.search_category_layout.addWidget(self.refresh_btn)

        # 選取按鈕
        self.select_btn = QPushButton("選取")
        self.select_btn.setCheckable(True)
        self.select_btn.toggled.connect(self.toggle_selection_mode)
        self.search_category_layout.addWidget(self.select_btn)

        self.select_all_btn = QPushButton("全選")
        self.select_all_btn.setCheckable(True)
        self.select_all_btn.toggled.connect(self.toggle_select_all)
        self.select_all_btn.setVisible(False)
        self.select_all_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.select_all_btn)

        # 操作按鈕
        self.mark_read_btn = QPushButton("標記為已讀")
        self.mark_read_btn.clicked.connect(lambda: self.mark_read_status(True))
        self.mark_read_btn.setVisible(True)
        self.mark_read_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.mark_read_btn)

        self.mark_unread_btn = QPushButton("標記為未讀")
        self.mark_unread_btn.clicked.connect(lambda: self.mark_read_status(False))
        self.mark_unread_btn.setVisible(True)
        self.mark_unread_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.mark_unread_btn)

        self.set_category_btn = QPushButton("設定類別")
        self.set_category_btn.clicked.connect(self.open_set_category_dialog)
        self.set_category_btn.setVisible(True)
        self.set_category_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.set_category_btn)

        self.delete_btn = QPushButton("刪除")
        self.delete_btn.clicked.connect(self.delete_email)
        self.delete_btn.setVisible(True)
        self.delete_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.delete_btn)

        self.restore_btn = QPushButton("恢復至收件匣")
        self.restore_btn.clicked.connect(self.restore_to_inbox)
        self.restore_btn.setVisible(True)
        self.restore_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.restore_btn)

        self.permanently_delete_btn = QPushButton("永久刪除")
        self.permanently_delete_btn.clicked.connect(self.permanently_delete)
        self.permanently_delete_btn.setVisible(True)
        self.permanently_delete_btn.setEnabled(False)
        self.search_category_layout.addWidget(self.permanently_delete_btn)

        self.logout_btn = QPushButton("登出")
        self.logout_btn.clicked.connect(self.logout)
        self.search_category_layout.addWidget(self.logout_btn)

        self.search_category_layout.addStretch()

        # 內容區域（使用 QSplitter）
        self.content_container = QSplitter(Qt.Horizontal)
        self.content_container.setHandleWidth(5)
        self.content_container.splitterMoved.connect(self.on_splitter_moved)
        self.main_layout.addWidget(self.content_container, stretch=1)

        # 左側：郵件列表
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.left_widget.setLayout(self.left_layout)
        self.content_container.addWidget(self.left_widget)

        self.email_list = CustomEmailList()
        self.email_list.itemClicked.connect(self.load_email)
        self.left_layout.addWidget(self.email_list)

        # 右側內容區域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        self.content_widget.setLayout(self.content_layout)
        self.content_container.addWidget(self.content_widget)

        # 分類標籤
        self.folder_label = QLabel("當前分類：收件匣")
        self.folder_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.content_layout.addWidget(self.folder_label)

        # 撰寫按鈕
        self.compose_btn = QPushButton("撰寫郵件")
        self.compose_btn.clicked.connect(self.show_compose)
        self.search_category_layout.addWidget(self.refresh_btn)
        self.compose_btn = QPushButton("撰寫郵件")
        self.compose_btn.clicked.connect(self.show_compose)
        self.search_category_layout.addWidget(self.compose_btn)  # 添加這一行
        

        # 郵件內容顯示
        self.email_content_widget = QWidget()
        self.email_content_widget.setObjectName("emailContentWidget")
        self.email_content_widget.setMinimumHeight(100)
        self.email_content_widget.setVisible(True)
        self.email_content_layout = QVBoxLayout()
        self.email_content_layout.setContentsMargins(0, 0, 0, 0)
        self.email_content_layout.setSpacing(8)
        self.email_content_widget.setLayout(self.email_content_layout)
        self.content_layout.addWidget(self.email_content_widget, stretch=1)

        self.subject_label = QLabel("")
        self.subject_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.subject_label.setMinimumHeight(20)
        self.subject_label.setEnabled(True)
        self.email_content_layout.addWidget(self.subject_label)

        self.sender_label = QLabel("")
        self.sender_label.setEnabled(True)
        self.email_content_layout.addWidget(self.sender_label)

        self.date_label = QLabel("")
        self.date_label.setEnabled(True)
        self.email_content_layout.addWidget(self.date_label)

        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        self.content_text.setMinimumHeight(50)
        self.content_text.setEnabled(True)
        self.email_content_layout.addWidget(self.content_text, stretch=1)

        # 郵件內容操作（回復、轉發、設定類別、恢復）
        self.email_actions_layout = QHBoxLayout()
        self.reply_btn = QPushButton("回復")
        self.reply_btn.clicked.connect(self.reply_email)
        self.forward_btn = QPushButton("轉發")
        self.forward_btn.clicked.connect(self.forward_email)
        self.content_restore_btn = QPushButton("恢復")
        self.content_restore_btn.clicked.connect(self.restore_to_inbox)
        self.content_restore_btn.hide()
        self.content_set_category_combo = QComboBox()
        self.content_set_category_combo.addItem("無類別")
        self.email_actions_layout.addWidget(self.reply_btn)
        self.email_actions_layout.addWidget(self.forward_btn)
        self.discuss_btn = QPushButton("AI助手")
        self.discuss_btn.clicked.connect(self.open_discussion_dialog)
        self.email_actions_layout.addWidget(self.discuss_btn)
        self.email_actions_layout.addWidget(self.content_restore_btn)
        self.email_actions_layout.addWidget(self.content_set_category_combo)
        self.email_actions_layout.addStretch()
        self.email_content_layout.addLayout(self.email_actions_layout)

        # 撰寫郵件表單
        self.compose_widget = ComposeTab(self.username, self)
        self.compose_widget.hide()
        self.content_layout.addWidget(self.compose_widget)

        # 初始化為收件匣介面
        print(f"Switching to {self.current_folder} at {datetime.now()}")
        self.switch_folder(self.current_folder)
        print(f"Switched to {self.current_folder} at {datetime.now()}")

    def on_splitter_moved(self, pos, index):
        pass

    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        if self.sidebar_expanded:
            self.toggle_btn.setText("✖")
            self.sidebar_widget.setVisible(True)
            self.animation = QPropertyAnimation(self.sidebar_widget, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(0)
            self.animation.setEndValue(200)
            self.animation.start()
        else:
            self.toggle_btn.setText("☰")
            self.animation = QPropertyAnimation(self.sidebar_widget, b"maximumWidth")
            self.animation.setDuration(200)
            self.animation.setStartValue(self.sidebar_widget.width())
            self.animation.setEndValue(0)
            self.animation.finished.connect(lambda: self.sidebar_widget.setVisible(False))
            self.animation.start()

    def handle_sidebar_click(self, item):
        callback = item.data(Qt.UserRole)
        if callback:
            callback()
        self.toggle_sidebar()

    def update_sidebar_menu(self):
        self.sidebar_menu.clear()
        folders = [
            ("收件匣", "#0000FF", lambda: self.switch_folder("inbox")),
            ("寄件備份", "#00FF00", lambda: self.switch_folder("sent")),
            ("草稿", "#FFD700", lambda: self.switch_folder("drafts")),
            ("垃圾郵件", "#FFA500", lambda: self.switch_folder("spam")),
            ("垃圾桶", "#808080", lambda: self.switch_folder("trash")),
        ]
        for name, color, callback in folders:
            item = QListWidgetItem(name)
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(2, 2, 12, 12)
            painter.end()
            item.setIcon(QIcon(pixmap))
            item.setData(Qt.UserRole, callback)
            self.sidebar_menu.addItem(item)

        # 分隔線
        item = QListWidgetItem()
        item.setFlags(Qt.NoItemFlags)
        item.setSizeHint(QSize(0, 10))
        self.sidebar_menu.addItem(item)

        # 類別
        for name, color in self.categories:
            item = QListWidgetItem(name)
            pixmap = QPixmap(12, 12)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 12, 12)
            painter.end()
            item.setIcon(QIcon(pixmap))
            item.setData(Qt.UserRole, lambda n=name: self.switch_to_category(n))
            self.sidebar_menu.addItem(item)

        # 管理類別
        item = QListWidgetItem("管理類別")
        pixmap = QPixmap(12, 12)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#4169E1"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 12, 12)
        painter.end()
        item.setIcon(QIcon(pixmap))
        item.setData(Qt.UserRole, self.manage_categories)
        self.sidebar_menu.addItem(item)

    def refresh_ui(self):
        self.update_email_list()
        self.update_category_combo()
        self.update_operation_buttons()
        QApplication.processEvents()

    def refresh_emails(self):
        """重新整理郵件列表，使用現有的 fetch 邏輯"""
        print(f"Refreshing emails for {self.username} at {datetime.now()}")
        self.refresh_ui()
        QMessageBox.information(self, "成功", "郵件列表已重新整理！")

    def update_email_list(self):
        checked_indices = []
        if self.selection_mode:
            for i in range(self.email_list.count()):
                item = self.email_list.item(i)
                if item.checkState() == Qt.Checked:
                    checked_indices.append(i)

        self.email_list.clear()
        filtered_emails = self.get_filtered_emails()
        if not filtered_emails:
            self.email_list.addItem("無符合條件的郵件")
            if not self.current_email and not self.is_displaying_email:
                self.clear_content()
            return
        for i, email in enumerate(filtered_emails):
            display_text = (
                f"{email.get('receiver', '無收件人')} - {email.get('title', '無標題')}"
                if email.get('mode') == 'drafts'
                else f"{email.get('sender', '未知寄件人')} - {email.get('title', '無標題')}"
            )
            item = QListWidgetItem(display_text)
            item.setSizeHint(QSize(0, 30))
            font = QFont()
            font.setBold(not email.get('read', False))
            item.setFont(font)
            item.setForeground(Qt.blue if not email.get('read', False) else Qt.black)
            if self.selection_mode:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Checked if i in checked_indices else Qt.Unchecked)
            else:
                item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
            if email.get("category") and any(cat[0] == email.get("category") for cat in self.categories):
                category_color = next(cat[1] for cat in self.categories if cat[0] == email.get("category"))
                pixmap = QPixmap(12, 12)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.setBrush(QColor(category_color))
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(0, 0, 12, 12)
                painter.end()
                item.setIcon(QIcon(pixmap))
            else:
                item.setIcon(QIcon())
            self.email_list.addItem(item)
        self.email_list.repaint()
        QApplication.processEvents()

    def update_category_combo(self):
        with QSignalBlocker(self.content_set_category_combo):
            current_category = self.content_set_category_combo.currentText()
            self.content_set_category_combo.clear()
            self.content_set_category_combo.addItem("無類別")
            for name, _ in self.categories:
                self.content_set_category_combo.addItem(name)
            if current_category in [cat[0] for cat in self.categories] or current_category == "無類別":
                self.content_set_category_combo.setCurrentText(current_category)
        self.content_set_category_combo.repaint()
        QApplication.processEvents()

    def get_filtered_emails(self):
        print(f"Fetching emails for {self.current_folder} at {datetime.now()}")
        try:
            mode = self.current_folder
            endpoint = "http://localhost:8080/fetch"
            if mode == "inbox":
                mode = "receive"
            elif mode == "sent":
                mode = "send"
            elif mode == "drafts":
                endpoint = "http://localhost:8080/fetch_draft"
            elif mode.startswith("category:"):
                mode = "receive"

            payload = {"username": self.username, "mode": mode}
            r = requests.post(endpoint, data=payload)
            if r.status_code == 200 and r.json().get("status") == "ok":
                self.emails = r.json().get("emails", [])
                if self.current_folder == "drafts":
                    for email in self.emails:
                        email["mode"] = "drafts"
            else:
                self.emails = []
                QMessageBox.warning(self, "錯誤", f"無法載入郵件：{r.text}")
        except requests.exceptions.RequestException as e:
            self.emails = []
            QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")

        emails = self.emails
        if self.current_folder.startswith("category:"):
            category = self.current_folder.replace("category:", "")
            emails = [e for e in emails if e.get("category", "") == category]
        elif self.current_folder == "spam":
            emails = [e for e in emails if e.get("system_type") == "spam"]
        elif self.current_folder == "trash":
            emails = [e for e in emails if e.get("user_type") == "trash" or e.get("uid") in self.trash_manual]
        elif self.current_folder not in ["drafts", "sent"]:
            emails = [e for e in emails if e.get("system_type") != "spam" and (e.get("user_type") != "trash" and e.get("uid") not in self.trash_manual)]

        if self.search_query:
            emails = [
                e for e in emails
                if (
                    self.search_query.lower() in e.get('sender', '').lower() or
                    self.search_query.lower() in e.get('receiver', '').lower() or
                    self.search_query.lower() in e.get('title', '').lower()
                )
            ]

        if self.filter_type == "最近一周":
            one_week_ago = (datetime.now() - datetime.timedelta(days=7)).timestamp()
            emails = [e for e in emails if float(e.get('timestamp', 0)) >= one_week_ago]
        elif self.filter_type == "已讀郵件":
            emails = [e for e in emails if e.get('read', False)]
        elif self.filter_type == "未讀郵件":
            emails = [e for e in emails if not e.get('read', False)]
        elif self.filter_type == "內容關鍵字" and self.content_keyword:
            emails = [e for e in emails if self.content_keyword.lower() in e.get('content', '').lower()]

        return emails

    def toggle_selection_mode(self, checked):
        self.selection_mode = checked
        self.select_all_btn.setChecked(False)
        self.select_all_btn.setVisible(checked)
        self.select_all_btn.setEnabled(checked)
        self.select_btn.setText("取消選取" if checked else "選取")
        self.update_email_list()
        self.update_operation_buttons()

    def exit_selection_mode(self):
        self.selection_mode = False
        self.select_btn.setChecked(False)
        self.select_btn.setText("選取")
        self.select_all_btn.setChecked(False)
        self.select_all_btn.setVisible(False)
        self.select_all_btn.setEnabled(False)
        self.update_email_list()
        self.update_operation_buttons()

    def toggle_select_all(self, checked):
        for i in range(self.email_list.count()):
            item = self.email_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.select_all_btn.setText("取消全選" if checked else "全選")
        if not checked:
            self.exit_selection_mode()

    def switch_folder(self, folder):
        self.current_folder = folder
        self.folder_label.setText(f"當前分類：{self.get_folder_name(folder)}")
        self.search_input.clear()
        self.filter_combo.setCurrentText("全部")
        self.content_keyword_input.clear()
        self.content_keyword_input.hide()
        self.exit_selection_mode()
        self.refresh_ui()

    def switch_to_category(self, category):
        if category == "無類別":
            return
        self.current_folder = f"category:{category}"
        self.folder_label.setText(f"當前分類：{category}")
        self.search_input.clear()
        self.filter_combo.setCurrentText("全部")
        self.content_keyword_input.clear()
        self.content_keyword_input.hide()
        self.exit_selection_mode()
        self.refresh_ui()

    def get_folder_name(self, folder):
        if folder.startswith("category:"):
            return folder.replace("category:", "")
        return {
            "inbox": "收件匣",
            "sent": "寄件備份",
            "drafts": "草稿",
            "spam": "垃圾郵件",
            "trash": "垃圾桶"
        }.get(folder, "未知分類")

    def update_operation_buttons(self):
        is_inbox = self.current_folder == "inbox"
        is_spam_or_trash = self.current_folder in ["spam", "trash"]
        is_inbox_or_trash = self.current_folder in ["inbox", "trash"]
        is_trash = self.current_folder == "trash"
        is_inbox_sent_or_drafts = self.current_folder in ["inbox", "sent", "drafts"]
        has_target_emails = bool(self.get_target_emails())

        self.mark_read_btn.setVisible(is_inbox)
        self.mark_read_btn.setEnabled(is_inbox and has_target_emails)

        self.mark_unread_btn.setVisible(is_inbox)
        self.mark_unread_btn.setEnabled(is_inbox and has_target_emails)

        self.set_category_btn.setVisible(is_inbox)
        self.set_category_btn.setEnabled(is_inbox and has_target_emails)

        self.delete_btn.setVisible(is_inbox_sent_or_drafts)
        self.delete_btn.setEnabled(is_inbox_sent_or_drafts and has_target_emails)

        self.restore_btn.setVisible(is_spam_or_trash)
        self.restore_btn.setEnabled(is_spam_or_trash and has_target_emails)

        self.permanently_delete_btn.setVisible(is_trash)
        self.permanently_delete_btn.setEnabled(is_trash and has_target_emails)

    def search_emails(self, query):
        self.search_query = query
        self.refresh_ui()

    def filter_emails(self, filter_type):
        self.filter_type = filter_type
        self.content_keyword_input.setVisible(filter_type == "內容關鍵字")
        self.content_keyword = ""
        self.content_keyword_input.clear()
        self.refresh_ui()

    def update_content_keyword(self, keyword):
        self.content_keyword = keyword
        if self.filter_type == "內容關鍵字":
            self.refresh_ui()

    def manage_categories(self):
        dialog = CategoryDialog(self.categories, self)
        dialog.exec_()
        self.refresh_ui()

    def open_set_category_dialog(self):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        categories = ["無類別"] + [cat[0] for cat in self.categories]
        category, ok = QInputDialog.getItem(self, "設定類別", "選擇類別：", categories, 0, False)
        if ok and category:
            self.set_category(category)

    def set_category(self, category):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        category = "" if category == "無類別" else category
        count = 0
        try:
            for email in emails:
                print("set_category, email.get('uid')", email.get('uid'))
                payload = {'username': self.username, 'email_id': email.get('uid'), 'category': category}
                r = requests.post('http://localhost:8080/set_cat', data=payload)
                print(r.json())
                email["category"] = category
                count += 1
        except requests.exceptions.RequestException as e:
            print(e)
            QMessageBox.warning(self, "修改類別錯誤")
        self.exit_selection_mode()
        self.refresh_ui()
        QMessageBox.information(self, "成功", f"{count} 封郵件已設為類別：{category or '無'}")
        

    def load_email(self, item):
        index = self.email_list.row(item)
        emails_in_folder = self.get_filtered_emails()
        if index >= len(emails_in_folder):
            return
        email = emails_in_folder[index]
        self.current_email = email
        email['read'] = True
        self.is_displaying_email = True
        self.display_email(email)
        QTimer.singleShot(50, self.post_display_refresh)

    def post_display_refresh(self):
        self.is_displaying_email = False
        self.refresh_ui()

    def display_email(self, email):
        if email.get('mode') == 'drafts':
            self.show_compose()
            self.compose_widget.load_email(email)
            self.email_content_widget.setVisible(False)
        else:
            self.subject_label.setText(email.get('title', '無標題'))
            self.sender_label.setText(f"寄件人: {email.get('sender', '未知寄件人')}")
            ts = float(email.get('timestamp', 0))
            self.date_label.setText(f"日期: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}")
            self.content_text.setPlainText(email.get('content', ''))
            self.reply_btn.show()
            self.forward_btn.show()
            self.content_restore_btn.setVisible(
                (email.get('user_type') == 'trash' or email.get('system_type') == 'spam') and 
                self.current_folder not in ["sent"]
            )
            self.content_set_category_combo.setVisible(
                email.get('system_type') != 'spam' and email.get('user_type') != 'trash' and 
                self.current_folder == "inbox"
            )
            self.hide_compose()
            self.email_content_widget.setVisible(True)
            image_list = email.get("image_list", [])
            while self.email_content_layout.count() > 5:
                widget = self.email_content_layout.itemAt(5).widget()
                if widget:
                    widget.setParent(None)
            if image_list:
                self.email_content_layout.addWidget(QLabel("🖼️ 附件圖片："))
                for idx, img_str in enumerate(image_list):
                    try:
                        pixmap = QPixmap()
                        pixmap.loadFromData(base64.b64decode(img_str))
                        img_label = QLabel()
                        img_label.setPixmap(pixmap.scaledToWidth(400))
                        self.email_content_layout.addWidget(img_label)
                    except Exception as e:
                        self.email_content_layout.addWidget(QLabel(f"⚠️ 圖片 {idx+1} 載入失敗：{e}"))

    def base64_to_pixmap(self, base64_str: str) -> QPixmap:
        img_data = base64.b64decode(base64_str)
        qimg = QImage.fromData(QByteArray(img_data))
        return QPixmap.fromImage(qimg)

    def mark_as_spam(self):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        reply = QMessageBox.question(self, "確認", "確定要標記為垃圾郵件？", QMessageBox.Ok | QMessageBox.Cancel)
        if reply != QMessageBox.Ok:
            return
        count = 0
        for email in emails:
            email_id = email.get("uid")
            try:
                payload = {"email_id": email_id}
                r = requests.post("http://localhost:8080/mark_spam", data=payload)
                if r.status_code == 200 and r.json().get("status") == "ok":
                    email['system_type'] = 'spam'
                    count += 1
                else:
                    QMessageBox.warning(self, "失敗", f"標記為垃圾郵件失敗：{r.json().get('msg', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")
                return
        self.current_email = None
        self.exit_selection_mode()
        self.refresh_ui()
        QMessageBox.information(self, "成功", f"{count} 封郵件已標記為垃圾郵件")

    def delete_email(self):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        reply = QMessageBox.question(self, "確認", "確定要將選中的郵件移至垃圾桶？", QMessageBox.Ok | QMessageBox.Cancel)
        if reply != QMessageBox.Ok:
            return
        count = 0
        for email in emails:
            email_id = email.get("uid")
            if email_id not in self.trash_manual:
                self.trash_manual.append(email_id)
                try:
                    payload = {"email_id": email_id}
                    r = requests.post("http://localhost:8080/trash", data=payload)
                    if r.status_code == 200 and r.json().get("status") == "ok":
                        email['user_type'] = 'trash'
                        count += 1
                    else:
                        QMessageBox.warning(self, "失敗", f"移動到垃圾桶失敗：{r.json().get('msg', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")
                    return
        self.current_email = None
        self.exit_selection_mode()
        self.refresh_ui()
        QMessageBox.information(self, "成功", f"{count} 封郵件已移至垃圾桶")

    def restore_to_inbox(self):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        reply = QMessageBox.question(self, "確認", "確定要恢復至收件匣？", QMessageBox.Ok | QMessageBox.Cancel)
        if reply != QMessageBox.Ok:
            return
        count = 0
        for email in emails:
            email_id = email.get("uid")
            if email_id in self.trash_manual:
                self.trash_manual.remove(email_id)
            try:
                payload = {"email_id": email_id}
                r = requests.post("http://localhost:8080/restore", data=payload)
                if r.status_code == 200 and r.json().get("status") == "ok":
                    email['user_type'] = 'normal'
                    count += 1
                else:
                    QMessageBox.warning(self, "失敗", f"恢復失敗：{r.json().get('msg', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")
                return
        self.current_email = None
        self.exit_selection_mode()
        self.refresh_ui()
        QMessageBox.information(self, "成功", f"{count} 封郵件已恢復至收件匣")

    def permanently_delete(self):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        reply = QMessageBox.question(
            self, "確認", "確定要永久刪除選中的郵件？此操作無法復原。",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if reply != QMessageBox.Ok:
            return
        count = 0
        for email in emails:
            email_id = email.get("uid")
            try:
                payload = {"email_id": email_id}
                r = requests.post("http://localhost:8080/delete_permanent", data=payload)
                if r.status_code == 200 and r.json().get("status") == "ok":
                    self.emails.remove(email)
                    if email_id in self.trash_manual:
                        self.trash_manual.remove(email_id)
                    count += 1
                else:
                    QMessageBox.warning(self, "失敗", f"永久刪除失敗：{r.json().get('msg', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")
                return
        self.current_email = None
        self.exit_selection_mode()
        self.refresh_ui()
        self.clear_content()
        QMessageBox.information(self, "成功", f"{count} 封郵件已永久刪除")

    def mark_read_status(self, read_status):
        emails = self.get_target_emails()
        if not emails:
            QMessageBox.warning(self, "錯誤", "請選擇一封郵件或瀏覽一封郵件")
            return
        count = 0
        for email in emails:
            email_id = email.get("uid")
            try:
                payload = {"email_id": email_id, "read_status": read_status}
                r = requests.post("http://localhost:8080/mark_read", data=payload)
                if r.status_code == 200 and r.json().get("status") == "ok":
                    email['read'] = read_status
                    count += 1
                else:
                    QMessageBox.warning(self, "失敗", f"標記狀態失敗：{r.json().get('msg', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                QMessageBox.warning(self, "錯誤", f"無法連線到後端伺服器：{str(e)}")
                return
        self.exit_selection_mode()
        self.refresh_ui()
        QMessageBox.information(self, "成功", f"{count} 封郵件已標記為{'已讀' if read_status else '未讀'}")

    def get_target_emails(self):
        selected_emails = self.get_selected_emails()
        if selected_emails:
            return selected_emails
        if self.current_email:
            return [self.current_email]
        return []

    def get_selected_emails(self):
        emails_in_folder = self.get_filtered_emails()
        if self.selection_mode:
            selected_emails = []
            for i in range(self.email_list.count()):
                item = self.email_list.item(i)
                if item.checkState() == Qt.Checked:
                    if i < len(emails_in_folder):
                        selected_emails.append(emails_in_folder[i])
            return selected_emails
        else:
            current_item = self.email_list.currentItem()
            if current_item:
                index = self.email_list.row(current_item)
                if index < len(emails_in_folder):
                    return [emails_in_folder[index]]
            return []

    def reply_email(self):
        emails = self.get_target_emails()
        if len(emails) != 1:
            QMessageBox.warning(self, "錯誤", "請選擇或瀏覽一封郵件進行回復")
            return
        email = emails[0]
        self.show_compose()
        self.compose_widget.to_input.setText(email.get('sender', ''))
        self.compose_widget.subject_input.setText(f"Re: {email.get('title', '')}")
        self.compose_widget.content_input.setPlainText(f"\n\n--- 原郵件 ---\n{email.get('content', '')}")

    def forward_email(self):
        emails = self.get_target_emails()
        if len(emails) != 1:
            QMessageBox.warning(self, "錯誤", "請選擇或瀏覽一封郵件進行轉發")
            return
        email = emails[0]
        self.show_compose()
        self.compose_widget.to_input.clear()
        self.compose_widget.subject_input.setText(f"Fwd: {email.get('title', '')}")
        ts = float(email.get('timestamp', 0))
        self.compose_widget.content_input.setPlainText(
            f"\n\n--- 轉發郵件 ---\n寄件人: {email.get('sender', '')}\n日期: {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}\n{email.get('content', '')}"
        )

    def show_compose(self):
        self.email_content_widget.setVisible(False)
        self.compose_widget.setVisible(True)
        if not self.current_email or self.current_email.get('mode') != 'drafts':
            self.compose_widget.clear_inputs()
        self.reply_btn.hide()
        self.forward_btn.hide()
        self.content_restore_btn.hide()
        self.content_set_category_combo.hide()
        self.content_widget.update()
        self.content_widget.repaint()
        self.content_layout.activate()
        self.content_widget.updateGeometry()
        QApplication.processEvents()

    def hide_compose(self):
        self.compose_widget.setVisible(False)
        self.email_content_widget.setVisible(True)
        if self.current_email and self.current_email.get('mode') != 'drafts':
            self.reply_btn.show()
            self.forward_btn.show()
            self.content_restore_btn.setVisible(
                (self.current_email.get('user_type') == 'trash' or self.current_email.get('system_type') == 'spam') and 
                self.current_folder not in ["sent"]
            )
            self.content_set_category_combo.setVisible(
                self.current_email.get('system_type') != 'spam' and self.current_email.get('user_type') != 'trash' and 
                self.current_folder == "inbox"
            )
        else:
            self.clear_content()
        self.content_widget.update()
        self.content_widget.repaint()
        self.content_layout.activate()
        self.content_widget.updateGeometry()
        QApplication.processEvents()

    def clear_content(self):
        if self.is_displaying_email:
            return
        if self.current_email and self.current_email.get('mode') != 'drafts':
            self.reply_btn.hide()
            self.forward_btn.hide()
            self.content_restore_btn.hide()
            self.content_set_category_combo.hide()
        else:
            self.current_email = None
            self.subject_label.setText("")
            self.sender_label.setText("")
            self.date_label.setText("")
            self.content_text.setPlainText("")
            self.reply_btn.hide()
            self.forward_btn.hide()
            self.content_restore_btn.hide()
            self.content_set_category_combo.hide()
            while self.email_content_layout.count() > 5:
                widget = self.email_content_layout.itemAt(5).widget()
                if widget:
                    widget.setParent(None)
        self.subject_label.setEnabled(True)
        self.sender_label.setEnabled(True)
        self.date_label.setEnabled(True)
        self.content_text.setEnabled(True)
        self.subject_label.setVisible(True)
        self.sender_label.setVisible(True)
        self.date_label.setVisible(True)
        self.content_text.setVisible(True)
        self.email_content_widget.setVisible(True)
        self.subject_label.update()
        self.sender_label.update()
        self.date_label.update()
        self.content_text.update()
        self.email_content_widget.update()
        self.content_widget.update()
        QApplication.processEvents()

    def open_discussion_dialog(self):
        if not self.current_email:
            QMessageBox.warning(self, "錯誤", "請先選擇一封郵件")
            return
        email_text = self.current_email.get("content")
        dialog = DiscussionDialog(email_text, self)
        dialog.exec_()

    def logout(self):
        self.logout_signal.emit()
        self.close()

if __name__ == "__main__":
    print(f"Starting application at {datetime.now()}")
    try:
        app = QApplication(sys.argv)
        print("QApplication created successfully")
        window = LoginWindow()
        print("LoginWindow initialized")
        window.show()
        print("LoginWindow shown")
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error occurred: {str(e)}")