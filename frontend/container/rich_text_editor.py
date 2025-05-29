from PyQt5.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QToolBar, QAction, QColorDialog
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor, QFont

class RichTextEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.text_edit = QTextEdit()
        self.toolbar = QToolBar()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # 讓整體不多出空隙
        layout.addWidget(self.toolbar)  # 工具列
        layout.addWidget(self.text_edit)  # 文字區
        self.setLayout(layout)

        self.setup_toolbar()

    def setup_toolbar(self):
        bold_action = QAction("B", self)
        bold_action.setCheckable(True)
        bold_action.triggered.connect(self.toggle_bold)
        self.toolbar.addAction(bold_action)

        italic_action = QAction("I", self)
        italic_action.setCheckable(True)
        italic_action.triggered.connect(self.toggle_italic)
        self.toolbar.addAction(italic_action)

        underline_action = QAction("U", self)
        underline_action.setCheckable(True)
        underline_action.triggered.connect(self.toggle_underline)
        self.toolbar.addAction(underline_action)

        color_action = QAction("字體顏色", self)
        color_action.triggered.connect(self.change_text_color)
        self.toolbar.addAction(color_action)

    def toggle_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.text_edit.fontWeight() != QFont.Bold else QFont.Normal)
        self.merge_format(fmt)

    def toggle_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(not self.text_edit.fontItalic())
        self.merge_format(fmt)

    def toggle_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(not self.text_edit.fontUnderline())
        self.merge_format(fmt)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.merge_format(fmt)

    def merge_format(self, fmt):
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)
        cursor.mergeCharFormat(fmt)
        self.text_edit.mergeCurrentCharFormat(fmt)

    def toPlainText(self):
        return self.text_edit.toPlainText()

    def clear(self):
        self.text_edit.clear()

    # ==== 新增區：提供 toHtml() 方法以支援富文字輸出 ====
    def toHtml(self):
        return self.text_edit.toHtml()
    # ===================================================

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    editor = RichTextEditor()
    editor.show()
    sys.exit(app.exec_())