# 德语阅读助手

这是一个桌面端德语学习辅助工具，帮助用户理解德语文本。

## 功能

- 截图功能：捕获屏幕上的德语文本
- 德语OCR识别：自动识别图片中的德语文本
- 交互式文本分析：将识别出的文本转换为可点击的文本块
- AI辅助理解：点击单词后使用AI解释选中的单词在上下文中的含义
- 支持追问功能：与AI进行连续对话，进一步理解文本

## 安装

1. 克隆仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 安装Tesseract OCR（必须）:
   - **Windows用户**: 从[这里](https://github.com/UB-Mannheim/tesseract/wiki)下载安装器
   - **Mac用户**: 使用Homebrew安装 `brew install tesseract`
   - **Linux用户**: 使用apt安装 `sudo apt-get install tesseract-ocr`
4. 安装德语语言包:
   - **Windows用户**: 在安装时选择德语包，或下载语言数据文件放入Tesseract安装目录的tessdata文件夹
   - **Mac/Linux用户**: `sudo apt-get install tesseract-ocr-deu` 或 `brew install tesseract-lang`
5. 配置(如果需要):
   - 在`utils/ocr_handler.py`文件中设置Tesseract路径（仅Windows需要）
   - 创建`.env`文件并设置OpenAI API密钥
6. 运行程序：`python main.py`

## 使用方法

1. 点击截图按钮捕获屏幕上的德语文本
2. 软件自动识别文本并显示可点击的文本块
3. 点击感兴趣的单词或短语（支持多选）
4. 点击询问按钮，AI将解释所选文本在上下文中的含义
5. 在对话窗口中可以继续追问相关问题 