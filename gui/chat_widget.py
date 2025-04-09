from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QTextEdit, QLineEdit, QLabel, QScrollArea, QFrame)
from PySide6.QtCore import Qt, Signal, QSize, QThread, Slot
from PySide6.QtGui import QColor, QTextCursor, QFont

from utils.ai_handler import AIHandler

class ChatThread(QThread):
    response_received = Signal(str)
    
    def __init__(self, ai_handler, prompt, context=None):
        super().__init__()
        self.ai_handler = ai_handler
        self.prompt = prompt
        self.context = context
    
    def run(self):
        response = self.ai_handler.get_response(self.prompt, self.context)
        self.response_received.emit(response)

class ChatWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ai_handler = AIHandler()
        self.chat_history = []
        self.context_text = ""
        self.selected_text = ""
        
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 对话标题
        title_label = QLabel("AI 对话")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        # 聊天记录显示区域
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(
            "background-color: white; border: 1px solid #cccccc; border-radius: 5px;"
        )
        
        # 输入框和发送按钮
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("输入追问...")
        self.message_input.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton("发送")
        self.send_button.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.message_input, 1)
        input_layout.addWidget(self.send_button)
        
        # 添加到主布局
        layout.addWidget(title_label)
        layout.addWidget(self.chat_display, 1)  # 1表示可拉伸
        layout.addLayout(input_layout)
        
        # 初始提示
        self.chat_display.setText("选择单词并点击「询问AI」按钮开始对话...")
    
    def new_conversation(self, context, selected_text, prompt):
        # 保存上下文和选中文本，用于后续追问
        self.context_text = context
        self.selected_text = selected_text
        
        # 清除聊天记录
        self.chat_history = []
        
        # 发送第一条消息
        self.display_user_message(prompt)
        
        # 创建线程获取AI回复
        self.request_ai_response(prompt)
    
    def send_message(self):
        message = self.message_input.text().strip()
        if not message:
            return
        
        # 清空输入框
        self.message_input.clear()
        
        # 显示用户消息
        self.display_user_message(message)
        
        # 创建上下文，包含原始文本、选中单词和聊天历史
        context = {
            "original_text": self.context_text,
            "selected_text": self.selected_text,
            "chat_history": self.chat_history
        }
        
        # 获取AI回复
        self.request_ai_response(message, context)
    
    def request_ai_response(self, prompt, context=None):
        # 显示等待消息
        self.chat_display.append("<div style='color: #777777; text-align: center;'>AI 正在思考...</div>")
        
        # 创建线程获取AI回复
        self.chat_thread = ChatThread(self.ai_handler, prompt, context)
        self.chat_thread.response_received.connect(self.display_ai_response)
        self.chat_thread.start()
    
    def display_user_message(self, message):
        # 添加用户消息到聊天记录
        self.chat_history.append({"role": "user", "content": message})
        
        # 显示在聊天窗口
        self.chat_display.append(
            f"<div style='margin-bottom: 10px;'>"
            f"<div style='font-weight: bold; color: #2979ff;'>你:</div>"
            f"<div style='background-color: #e3f2fd; padding: 8px; border-radius: 5px;'>"
            f"{message}</div></div>"
        )
        
        # 滚动到底部
        self.chat_display.moveCursor(QTextCursor.End)
    
    @Slot(str)
    def display_ai_response(self, response):
        # 添加AI回复到聊天记录
        self.chat_history.append({"role": "assistant", "content": response})
        
        # 删除"AI正在思考..."消息
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.select(QTextCursor.LineUnderCursor)
        cursor.removeSelectedText()
        
        # 显示AI回复
        self.chat_display.append(
            f"<div style='margin-bottom: 10px;'>"
            f"<div style='font-weight: bold; color: #00897b;'>AI:</div>"
            f"<div style='background-color: #e0f2f1; padding: 8px; border-radius: 5px;'>"
            f"{response}</div></div>"
        )
        
        # 滚动到底部
        self.chat_display.moveCursor(QTextCursor.End)
    
    def sizeHint(self):
        return QSize(400, 600) 