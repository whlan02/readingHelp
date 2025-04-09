import os
import sys
import numpy as np
from PIL import Image
import pytesseract

class OCRHandler:
    def __init__(self):
        # 指定pytesseract路径（Windows用户通常需要设置）
        # 如果Tesseract安装在默认位置，取消下面一行的注释并根据需要调整路径
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # 设置语言包，确保已经安装了德语语言包
        # deu: 德语, eng: 英语
        self.lang = 'deu+eng'
        
        # 检查是否安装了Tesseract
        self.tesseract_installed = self._check_tesseract()
    
    def _check_tesseract(self):
        """检查Tesseract是否正确安装"""
        try:
            # 尝试运行一个简单的OCR测试
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            print(f"Tesseract OCR检测失败: {e}")
            print("请确保已安装Tesseract OCR并设置正确的路径:")
            print("- Windows: pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
            print("- Mac/Linux: 确保tesseract在系统PATH中")
            return False
    
    def process_image(self, pixmap):
        """
        处理QPixmap图像，返回识别出的文本
        
        参数:
        - pixmap: QPixmap对象，通常来自截图
        
        返回:
        - 识别出的文本字符串
        """
        if not self.tesseract_installed:
            return "错误: Tesseract OCR未正确安装。请参考README.md中的安装说明。"
        
        try:
            # 将QPixmap转换为PIL Image
            image = self.pixmap_to_image(pixmap)
            
            # 图像预处理（可以提高OCR质量）
            # 转换为灰度图像
            gray_image = image.convert('L')
            
            # 执行OCR
            text = pytesseract.image_to_string(
                gray_image, 
                lang=self.lang,
                config='--psm 3'  # 页面分割模式：自动，以段为单位
            )
            
            # 如果识别文本为空，尝试不同的页面分割模式
            if not text.strip():
                text = pytesseract.image_to_string(
                    gray_image,
                    lang=self.lang,
                    config='--psm 6'  # 将图像视为单个文本块
                )
            
            # 返回识别的文本
            if text.strip():
                return text.strip()
            else:
                return "未能识别出文本，请尝试重新截图或调整图像清晰度。"
            
        except Exception as e:
            print(f"OCR处理过程中出错：{e}")
            return f"OCR处理错误：{str(e)}"
    
    def pixmap_to_image(self, pixmap):
        """将QPixmap转换为PIL Image"""
        # 保存为临时图像
        temp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_ocr.png")
        pixmap.save(temp_path, "PNG")
        
        # 读取为PIL图像
        image = Image.open(temp_path)
        
        # 删除临时文件
        try:
            os.remove(temp_path)
        except:
            pass
            
        return image 