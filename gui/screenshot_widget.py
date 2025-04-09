from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QGuiApplication

class ScreenshotWidget(QWidget):
    screenshot_taken = Signal(QPixmap)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)
        
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        # 黑色半透明背景
        self.background_color = QColor(0, 0, 0, 100)
        self.setStyleSheet("background: transparent;")
        
        # 捕获整个屏幕用于显示
        self.screen_pixmap = None
    
    def start_screenshot(self):
        screen = QGuiApplication.primaryScreen()
        self.screen_pixmap = screen.grabWindow(0)
        
        # 清除选择区域
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        self.showFullScreen()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 绘制屏幕截图作为背景
        if self.screen_pixmap:
            painter.drawPixmap(0, 0, self.screen_pixmap)
        
        # 绘制半透明遮罩层
        painter.fillRect(self.rect(), self.background_color)
        
        # 如果正在选择区域，绘制选择框
        if not self.start_point.isNull() and not self.end_point.isNull():
            selected_rect = self.get_selected_rect()
            
            # 选择区域内显示原始图像
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selected_rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # 绘制选择区域的边框
            pen = QPen(QColor(0, 174, 255), 2)
            painter.setPen(pen)
            painter.drawRect(selected_rect)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_point = event.position().toPoint()
            self.is_drawing = True
    
    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.position().toPoint()
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.end_point = event.position().toPoint()
            self.is_drawing = False
            
            # 如果选择了有效区域，则捕获该区域
            if not self.start_point.isNull() and not self.end_point.isNull():
                selected_rect = self.get_selected_rect()
                
                # 最小尺寸检查
                if selected_rect.width() > 10 and selected_rect.height() > 10:
                    capture = self.screen_pixmap.copy(selected_rect)
                    self.screenshot_taken.emit(capture)
                    self.hide()
    
    def keyPressEvent(self, event):
        # ESC键退出截图
        if event.key() == Qt.Key_Escape:
            self.hide()
    
    def get_selected_rect(self):
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return QRect(x, y, width, height) 