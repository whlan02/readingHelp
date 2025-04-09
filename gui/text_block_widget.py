from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame, QScrollArea
from PySide6.QtCore import Qt, Signal, QSize, QMargins
from PySide6.QtGui import QFont, QColor

class WordButton(QLabel):
    clicked = Signal(str, bool)  # 单词, 是否选中
    
    def __init__(self, word, parent=None):
        super().__init__(parent)
        
        self.word = word
        self.selected = False
        
        self.setText(word)
        self.setContentsMargins(5, 2, 5, 2)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameShape(QFrame.Box)
        self.setStyleSheet(
            "background-color: white; border: 1px solid #cccccc; border-radius: 3px;"
        )
        
        # 设置鼠标悬停效果
        self.setMouseTracking(True)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_selected()
            self.clicked.emit(self.word, self.selected)
        
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        if not self.selected:
            self.setStyleSheet(
                "background-color: #f0f0f0; border: 1px solid #cccccc; border-radius: 3px;"
            )
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if not self.selected:
            self.setStyleSheet(
                "background-color: white; border: 1px solid #cccccc; border-radius: 3px;"
            )
        super().leaveEvent(event)
    
    def toggle_selected(self):
        self.selected = not self.selected
        self.update_style()
    
    def set_selected(self, selected):
        self.selected = selected
        self.update_style()
    
    def update_style(self):
        if self.selected:
            self.setStyleSheet(
                "background-color: #e1f5fe; border: 1px solid #4fc3f7; border-radius: 3px;"
            )
        else:
            self.setStyleSheet(
                "background-color: white; border: 1px solid #cccccc; border-radius: 3px;"
            )

class TextBlockWidget(QWidget):
    word_selected = Signal(str, bool)  # 单词, 是否选中
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.word_buttons = []
        self.full_text = ""
    
    def set_text(self, text):
        # 清除旧内容
        self.clear()
        self.full_text = text
        
        if not text:
            return
        
        # 按行分割文本
        lines = text.split("\n")
        
        for line in lines:
            if not line.strip():
                continue
                
            # 创建一个水平布局用于一行文本
            line_widget = QWidget()
            line_layout = QHBoxLayout(line_widget)
            line_layout.setSpacing(5)
            line_layout.setContentsMargins(0, 0, 0, 0)
            
            # 使用空格分割单词（简化处理，实际应用中可能需要更复杂的分词逻辑）
            words = line.split()
            
            for word in words:
                word_btn = WordButton(word)
                word_btn.clicked.connect(self.on_word_clicked)
                line_layout.addWidget(word_btn)
                self.word_buttons.append(word_btn)
            
            # 添加弹性空间，使单词靠左对齐
            line_layout.addStretch(1)
            
            # 将行添加到主布局
            self.layout.addWidget(line_widget)
        
        # 添加弹性空间，使所有内容靠上对齐
        self.layout.addStretch(1)
    
    def on_word_clicked(self, word, selected):
        # 转发信号
        self.word_selected.emit(word, selected)
    
    def clear(self):
        # 清除所有文本块和单词按钮
        self.word_buttons.clear()
        
        # 删除所有子部件
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def get_full_text(self):
        return self.full_text
    
    def sizeHint(self):
        return QSize(400, 400) 