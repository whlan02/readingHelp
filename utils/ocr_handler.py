import os
import sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

class OCRHandler:
    def __init__(self):
        # 指定pytesseract路径（Windows用户通常需要设置）
        # 如果Tesseract安装在默认位置，取消下面一行的注释并根据需要调整路径
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
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
    
    def preprocess_image(self, image):
        """图像预处理，提高OCR识别率"""
        # 转为灰度图
        gray_image = image.convert('L')
        
        # 增加对比度
        enhancer = ImageEnhance.Contrast(gray_image)
        gray_image = enhancer.enhance(2.0)  # 增强对比度
        
        # 锐化
        gray_image = gray_image.filter(ImageFilter.SHARPEN)
        
        # 二值化处理 (阈值可以根据实际情况调整)
        # 对于德语文本，通常保留灰度图像效果更好，所以这里不进行二值化
        
        return gray_image
    
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
            
            # 图像预处理
            processed_image = self.preprocess_image(image)
            
            # 尝试多种OCR配置，获取最佳结果
            results = []
            
            # 配置1: 自动页面分割
            text1 = pytesseract.image_to_string(
                processed_image, 
                lang=self.lang,
                config='--psm 3 --oem 3'  # 自动页面分割，默认OCR引擎
            )
            if text1.strip():
                results.append(text1)
            
            # 配置2: 假设单一文本块
            text2 = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config='--psm 6 --oem 3'  # 假设单一均匀文本块
            )
            if text2.strip():
                results.append(text2)
            
            # 如果第一种方法识别的文本更多，则使用第一种
            if results and len(results) > 1:
                if len(text1) >= len(text2):
                    return text1.strip()
                else:
                    return text2.strip()
            elif results:
                return results[0].strip()
            else:
                # 原始图像再试一次（无预处理）
                text = pytesseract.image_to_string(
                    image,
                    lang=self.lang,
                    config='--psm 3'
                )
                if text.strip():
                    return text.strip()
                
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