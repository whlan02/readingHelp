import os
import openai
from dotenv import load_dotenv

class AIHandler:
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 获取OpenAI API密钥
        api_key = os.getenv("OPENAI_API_KEY")
        
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
            self.api_available = True
        else:
            self.api_available = False
            print("警告：未找到OpenAI API密钥，请在.env文件中设置OPENAI_API_KEY")
    
    def get_response(self, prompt, context=None):
        """获取AI回复"""
        if not self.api_available:
            return "错误：未配置OpenAI API密钥。请在项目根目录创建.env文件，并添加OPENAI_API_KEY=your_api_key"
        
        try:
            messages = []
            
            # 创建系统提示
            system_message = (
                "你是一位精通德语的语言学家和教师，专门帮助中文学习者理解德语文本。"
                "请用中文解释德语单词和短语在特定语境中的含义、用法和语法特点。"
                "解释要简明扼要，针对中文学习者，不要过于专业化。"
                "不需要将德语单词翻译成英语，直接用中文解释即可。"
            )
            messages.append({"role": "system", "content": system_message})
            
            # 如果有上下文，添加到消息中
            if context and "original_text" in context:
                original_text = context["original_text"]
                selected_text = context["selected_text"]
                
                context_message = f"以下是完整的德语文本：\n\n{original_text}\n\n用户希望了解在这个语境中的'{selected_text}'。"
                messages.append({"role": "system", "content": context_message})
            
            # 添加历史对话（如果有）
            if context and "chat_history" in context:
                for msg in context["chat_history"]:
                    messages.append(msg)
            
            # 添加当前用户问题
            messages.append({"role": "user", "content": prompt})
            
            # 调用API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # 可以根据需要替换为其他模型
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # 返回回复内容
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"AI请求错误：{e}")
            return f"获取AI回复时出错：{str(e)}"
    
    def create_env_file(self, api_key):
        """创建或更新.env文件"""
        try:
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}\n")
            return True
        except Exception as e:
            print(f"创建.env文件失败：{e}")
            return False 