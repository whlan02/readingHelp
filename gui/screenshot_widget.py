from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, Signal, QRect, QPoint, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush, QPen, QPixmap, QGuiApplication, QScreen

class ScreenshotWidget(QWidget):
    screenshot_taken = Signal(QPixmap)
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)  # 整个窗口背景透明
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)
        
        # 初始化变量
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        
        # 黑色半透明背景
        self.background_color = QColor(0, 0, 0, 100)
        
        # 选择框样式
        self.border_color = QColor(0, 174, 255)
        self.mask_color = QColor(0, 120, 215, 30)  # 选择区域内的颜色，轻微蓝色半透明
        
        # 捕获整个屏幕用于显示
        self.screen_pixmap = None
        self.screen = None
        self.device_pixel_ratio = 1.0
        
        # 截图完成后延迟关闭的标志
        self.screenshot_completed = False
    
    def start_screenshot(self):
        # 获取主屏幕
        self.screen = QGuiApplication.primaryScreen()
        if not self.screen:
            return
        
        # 获取设备像素比
        self.device_pixel_ratio = self.screen.devicePixelRatio()
        
        # 捕获屏幕
        geometry = self.screen.geometry()
        self.screen_pixmap = self.screen.grabWindow(
            0,
            geometry.x(),
            geometry.y(),
            geometry.width(),
            geometry.height()
        )
        
        # 清除选择区域
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False
        self.screenshot_completed = False
        
        # 显示全屏窗口
        self.showFullScreen()
        self.activateWindow()  # 确保窗口获得焦点
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制屏幕截图作为背景
        if self.screen_pixmap:
            painter.drawPixmap(self.rect(), self.screen_pixmap)
        
        # 绘制半透明遮罩层
        painter.fillRect(self.rect(), self.background_color)
        
        # 如果正在选择区域，绘制选择框
        if not self.start_point.isNull() and not self.end_point.isNull():
            selected_rect = self.get_selected_rect()
            
            # 绘制选择区域：透明显示原始内容
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selected_rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # 给选择区域添加轻微的蓝色遮罩，但保持透明度
            painter.fillRect(selected_rect, self.mask_color)
            
            # 绘制选择区域的边框
            pen = QPen(self.border_color, 2)
            painter.setPen(pen)
            painter.drawRect(selected_rect)
            
            # 在选择框四角绘制标记点
            self.draw_corner_marks(painter, selected_rect)
            
            # 显示尺寸信息
            self.draw_size_info(painter, selected_rect)
    
    def draw_size_info(self, painter, rect):
        """绘制选择区域的尺寸信息"""
        size_text = f"{rect.width()} × {rect.height()}"
        painter.setPen(Qt.white)
        painter.drawText(
            rect.right() - 70,  # 位置可以根据需要调整
            rect.bottom() + 20,
            size_text
        )
    
    def draw_corner_marks(self, painter, rect):
        """在选择框四角绘制标记点，增强视觉反馈"""
        mark_size = 6
        pen = QPen(self.border_color, 2)
        painter.setPen(pen)
        
        # 左上角
        painter.drawLine(rect.left(), rect.top(), rect.left() + mark_size, rect.top())
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.top() + mark_size)
        
        # 右上角
        painter.drawLine(rect.right(), rect.top(), rect.right() - mark_size, rect.top())
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.top() + mark_size)
        
        # 左下角
        painter.drawLine(rect.left(), rect.bottom(), rect.left() + mark_size, rect.bottom())
        painter.drawLine(rect.left(), rect.bottom(), rect.left(), rect.bottom() - mark_size)
        
        # 右下角
        painter.drawLine(rect.right(), rect.bottom(), rect.right() - mark_size, rect.bottom())
        painter.drawLine(rect.right(), rect.bottom(), rect.right(), rect.bottom() - mark_size)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 考虑设备像素比
            pos = event.position()
            self.start_point = QPoint(int(pos.x()), int(pos.y()))
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()
    
    def mouseMoveEvent(self, event):
        if self.is_drawing:
            # 考虑设备像素比
            pos = event.position()
            self.end_point = QPoint(int(pos.x()), int(pos.y()))
            self.update()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_drawing:
            # 考虑设备像素比
            pos = event.position()
            self.end_point = QPoint(int(pos.x()), int(pos.y()))
            self.is_drawing = False
            
            # 如果选择了有效区域，则捕获该区域
            if not self.start_point.isNull() and not self.end_point.isNull():
                selected_rect = self.get_selected_rect()
                
                # 最小尺寸检查
                if selected_rect.width() > 10 and selected_rect.height() > 10:
                    # 考虑设备像素比进行截图
                    scaled_rect = QRect(
                        int(selected_rect.x() * self.device_pixel_ratio),
                        int(selected_rect.y() * self.device_pixel_ratio),
                        int(selected_rect.width() * self.device_pixel_ratio),
                        int(selected_rect.height() * self.device_pixel_ratio)
                    )
                    
                    # 从原始屏幕截图中提取选择的区域
                    capture = self.screen_pixmap.copy(scaled_rect)
                    
                    # 标记截图已完成
                    self.screenshot_completed = True
                    
                    # 发送信号并隐藏截图窗口
                    self.screenshot_taken.emit(capture)
                    self.hide()
    
    def keyPressEvent(self, event):
        # ESC键退出截图
        if event.key() == Qt.Key_Escape:
            self.hide()
    
    def get_selected_rect(self):
        """获取选择矩形区域，确保坐标正确"""
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        
        x = min(x1, x2)
        y = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        return QRect(x, y, width, height) 