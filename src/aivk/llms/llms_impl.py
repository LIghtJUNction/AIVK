from . import Base
import openai

class Llms(Base):
    """
    self.llms = [client1, client2, ...]
    """
    def __init__(self):
        super().__init__()

    def _load(self):
        self.models = self.meta.Metadata.llms.models
        self.llms = []
        for model in self.models:
            self._check(model)

    def _check(self, model):
        """
        检查API连接和模型可用性
        Args:
            model: [model_name, base_url, api_key]
        Returns:
            bool: 连接验证是否成功
        """
        try:
            # 创建客户端实例
            client = openai.OpenAI(
                base_url=model[1], 
                api_key=model[2]
            )
            
            # 尝试发送一个简单的测试请求
            try:
                response = client.chat.completions.create(
                    model=model[0],
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1  # 最小化token消耗
                )
                print(f"成功连接到 {model[1]} 并验证模型 {model[0]}")
                
                # 验证成功，保存客户端实例
                self.llms.append({
                    "model": model[0],
                    "client": client
                })
                return True
                
            except openai.APIError as api_err:
                print(f"API错误: {str(api_err)}")
                return False
                
            except openai.APIConnectionError as conn_err:
                print(f"连接错误: {str(conn_err)}")
                return False
                
            except openai.APITimeoutError as timeout_err:
                print(f"超时错误: {str(timeout_err)}")
                return False
                
        except Exception as e:
            print(f"初始化客户端失败: {str(e)}")
            return False

    def list(self):
        """
        列出所有模型
        """
        self.available_models = []
        for llm in self.llms:
            self.available_models.append(llm["model"])
            print(llm['model'])
        return self.models

    def chat(self, model, prompt):
        """
        model: 模型名称
        prompt: 输入文本
        """
        for client in self.llms:
            if client.model == model:
                return client.chat(prompt)
        return None