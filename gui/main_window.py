from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
                               QWidget, QScrollArea, QLabel, QFrame, QSplitter)
from PySide6.QtCore import Qt, Signal, QRect, QTimer
from PySide6.QtGui import QPixmap, QScreen, QKeySequence, QShortcut
from PySide6.QtWidgets import QApplication

from gui.screenshot_widget import ScreenshotWidget
from gui.text_block_widget import TextBlockWidget
from gui.chat_widget import ChatWidget
from utils.ocr_handler import OCRHandler
from utils.ai_handler import AIHandler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("德语阅读助手")
        self.resize(1000, 800)
        
        # 初始化组件
        self.screenshot_widget = ScreenshotWidget()
        self.ocr_handler = OCRHandler()
        self.ai_handler = AIHandler()
        
        self.selected_words = []
        self.original_pixmap = None
        
        # 创建状态栏
        self.statusBar().showMessage("准备就绪")
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        
        # 顶部工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        
        self.screenshot_btn = QPushButton("截图 (Ctrl+G)")
        self.ask_ai_btn = QPushButton("询问AI")
        self.ask_ai_btn.setEnabled(False)
        
        toolbar_layout.addWidget(self.screenshot_btn)
        toolbar_layout.addWidget(self.ask_ai_btn)
        toolbar_layout.addStretch()
        
        # 添加截图快捷键
        self.screenshot_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        self.screenshot_shortcut.activated.connect(self.take_screenshot)
        
        # 主分割区域
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧区域 - 图片和文本块
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 图片显示区域
        self.image_label = QLabel("点击截图按钮开始")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFrameShape(QFrame.Box)
        self.image_label.setMinimumHeight(200)
        
        # 文本块区域
        self.text_block_area = QScrollArea()
        self.text_block_widget = TextBlockWidget()
        self.text_block_area.setWidget(self.text_block_widget)
        self.text_block_area.setWidgetResizable(True)
        
        left_layout.addWidget(self.image_label)
        left_layout.addWidget(self.text_block_area, 1)  # 1表示可拉伸
        
        # 右侧区域 - 聊天区域
        self.chat_widget = ChatWidget()
        
        # 添加到分割器
        splitter.addWidget(left_widget)
        splitter.addWidget(self.chat_widget)
        splitter.setSizes([500, 500])  # 初始大小平分
        
        # 添加到主布局
        main_layout.addWidget(toolbar)
        main_layout.addWidget(splitter, 1)  # 1表示可拉伸
        
        self.setCentralWidget(main_widget)
    
    def setup_connections(self):
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.ask_ai_btn.clicked.connect(self.ask_ai)
        self.text_block_widget.word_selected.connect(self.on_word_selected)
    
    def take_screenshot(self):
        # 截图前最小化窗口并释放资源，确保截图工具能捕获到屏幕内容
        self.showMinimized()
        QApplication.processEvents()  # 处理挂起的事件，确保窗口真正最小化
        
        # 延迟一小段时间再启动截图
        # 使用QTimer单次触发
        QTimer.singleShot(200, self._execute_screenshot)
    
    def _execute_screenshot(self):
        # 断开之前的连接（如果有）
        try:
            self.screenshot_widget.screenshot_taken.disconnect()
        except:
            pass
        
        # 连接新的信号槽
        self.screenshot_widget.screenshot_taken.connect(self.process_screenshot)
        
        # 启动截图
        self.screenshot_widget.start_screenshot()
    
    def process_screenshot(self, pixmap):
        # 显示主窗口（从最小化状态恢复）
        self.showNormal()
        self.activateWindow()  # 确保窗口获得焦点
        
        # 显示截图
        scaled_pixmap = pixmap.scaled(
            self.image_label.width(), 
            200, 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # 保存原始截图，方便处理
        self.original_pixmap = pixmap
        
        # OCR处理
        self.statusBar().showMessage("正在识别文本...")
        QApplication.processEvents()  # 更新UI
        
        text = self.ocr_handler.process_image(pixmap)
        self.text_block_widget.set_text(text)
        
        # 重置选择
        self.selected_words = []
        self.ask_ai_btn.setEnabled(False)
        
        self.statusBar().showMessage("文本识别完成", 3000)
    
    def on_word_selected(self, word, is_selected):
        if is_selected and word not in self.selected_words:
            self.selected_words.append(word)
        elif not is_selected and word in self.selected_words:
            self.selected_words.remove(word)
        
        # 至少选择了一个单词才能询问AI
        self.ask_ai_btn.setEnabled(len(self.selected_words) > 0)
    
    def ask_ai(self):
        if not self.selected_words:
            return
        
        selected_text = " ".join(self.selected_words)
        context = self.text_block_widget.get_full_text()
        
        prompt = f"在这个语境下，如何理解'{selected_text}'"
        
        # 发送到聊天窗口，AI会异步回复
        self.chat_widget.new_conversation(context, selected_text, prompt) 