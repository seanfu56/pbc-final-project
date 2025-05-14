from PyQt5.QtWidgets import QToolBar, QAction
from PyQt5.QtGui import QTextCharFormat, QFont
from PyQt5.QtCore import pyqtSignal


class RichTextToolBar(QToolBar):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit
        self.setup_actions()

    def setup_actions(self):
        # 粗體按鈕
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        self.addAction(bold_action)

        # 你可以在這裡再加入斜體、底線等按鈕
        # 斜體按鈕
        
    def toggle_bold(self):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold)
        cursor.mergeCharFormat(fmt)