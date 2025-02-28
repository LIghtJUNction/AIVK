import hashlib
import random
import string
import asyncio
from typing import List, Dict, Union, Optional

from aivk.kernel.tee.tee_impl import Tee
from . import Base
import openai
from ..kernel.tee.tee_impl import Tee

class Llms(Base):
    """LLMs模型管理类
    
    处理LLM模型的配置加载和连接验证
    支持同步和异步调用
    """
    def __init__(self):
        super().__init__()
        self.tee = Tee()
        self.id_client: Dict[str, openai.OpenAI] = {}  # ID到同步客户端实例的映射
        self.async_id_client: Dict[str, openai.AsyncOpenAI] = {}  # ID到异步客户端实例的映射
        # 确保模型配置存在
        if not self.meta.Metadata.llms.models():
            self.meta.Metadata.llms.models([])
        self._load()
    
    @property
    def models(self) -> List[List[str]]:
        """获取所有已配置的模型列表"""
        return self.meta.Metadata.llms.models()
    
    def _load(self):
        """从Meta配置加载并验证模型"""
        for model in self.models:
            self._check(model)

    def get_local_models(self) -> List[List[str]]:
        """获取本地模型列表"""
        return [model for model in self.models if model[3] == 'local']
    
    def get_online_models(self) -> List[List[str]]:
        """获取在线模型列表"""
        return [model for model in self.models if model[3] == 'online']
    
    def get_local_model_id(self, model_name: str) -> Dict[str, List[str]]:
        """获取本地模型ID"""
        result = {}
        for model in self.models:
            if model[0] == model_name and model[3] == 'local':
                if model_name not in result:
                    result[model_name] = []
                result[model_name].append(self._make_model_id(model))
        return result

    def get_online_model_id(self, model_name: str) -> Dict[str, List[str]]:
        """获取在线模型ID"""
        result = {}
        for model in self.models:
            if model[0] == model_name and model[3] == 'online':
                if model_name not in result:
                    result[model_name] = []
                result[model_name].append(self._make_model_id(model))
        return result

    def get_model_name_by_id(self, model_id: str) -> str:
        """根据模型ID获取模型名称"""
        for model in self.models:
            if self._make_model_id(model) == model_id:
                return model[0]
        return ''
    
    def get_model_id_by_name(self, model_name: str) -> str:
        """根据模型名称获取模型ID"""
        for model in self.models:
            if model[0] == model_name:
                return self._make_model_id(model)
        return ''

    def chat(self, messages: List[Dict[str, str]], 
             model_id: str,
             stream: bool = False,
             **kwargs) -> str:
        """代理路由聊天接口（同步）"""
        if model_id not in self.id_client:
            raise ValueError(f"未找到模型ID: {model_id}")
            
        # 根据stream参数选择不同的处理函数
        if stream:
            return self._stream_chat(messages, model_id, **kwargs)
        else:
            return self._normal_chat(messages, model_id, **kwargs)
    
    async def async_chat(self, messages: List[Dict[str, str]],
                         model_id: str,
                         stream: bool = False,
                         **kwargs) -> str:
        """代理路由聊天接口（异步）"""
        if model_id not in self.async_id_client:
            raise ValueError(f"未找到异步模型ID: {model_id}")
            
        # 根据stream参数选择不同的处理函数
        if stream:
            return await self._async_stream_chat(messages, model_id, **kwargs)
        else:
            return await self._async_normal_chat(messages, model_id, **kwargs)
    
    def _normal_chat(self, messages: List[Dict[str, str]], model_id: str, **kwargs) -> str:
        """非流式聊天处理（同步）"""
        try:
            client = self.id_client[model_id]
            model_name = self.get_model_name_by_id(model_id)
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"聊天请求失败: {str(e)}")
    
    async def _async_normal_chat(self, messages: List[Dict[str, str]], model_id: str, **kwargs) -> str:
        """非流式聊天处理（异步）"""
        try:
            client = self.async_id_client[model_id]
            model_name = self.get_model_name_by_id(model_id)
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                **kwargs
            )
            
            # 如果指定了工具，返回完整响应对象，否则仅返回内容
            if 'tools' in kwargs:
                return response  # 返回完整响应对象
            else:
                return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"异步聊天请求失败: {str(e)}")
    
    def _stream_chat(self, messages: List[Dict[str, str]], model_id: str, **kwargs) -> str:
        """流式聊天处理（同步）"""
        try:
            client = self.id_client[model_id]
            model_name = self.get_model_name_by_id(model_id)
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            # 收集并打印流式响应
            collected_messages = []
            for chunk in response:
                # 更健壮的响应处理
                try:
                    if (hasattr(chunk, 'choices') and 
                        len(chunk.choices) > 0 and
                        hasattr(chunk.choices[0], 'delta') and
                        hasattr(chunk.choices[0].delta, 'content') and
                        chunk.choices[0].delta.content is not None):
                        
                        content = chunk.choices[0].delta.content
                        print(content, end='', flush=True)
                        collected_messages.append(content)
                except Exception as e:
                    print(f"\n[流处理警告: {str(e)}]", end='', flush=True)
                    continue
                    
            print()  # 完成后换行
            return ''.join(collected_messages)
            
        except Exception as e:
            import traceback
            print(f"\n调试信息: {traceback.format_exc()}")
            raise RuntimeError(f"流式聊天请求失败: {str(e)}")
    
    async def _async_stream_chat(self, messages: List[Dict[str, str]], model_id: str, **kwargs) -> str:
        """流式聊天处理（异步）"""
        try:
            client = self.async_id_client[model_id]
            model_name = self.get_model_name_by_id(model_id)
            response = await client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            # 收集并打印流式响应
            collected_messages = []
            async for chunk in response:
                # 更健壮的响应处理
                try:
                    if (hasattr(chunk, 'choices') and 
                        len(chunk.choices) > 0 and
                        hasattr(chunk.choices[0], 'delta') and
                        hasattr(chunk.choices[0].delta, 'content') and
                        chunk.choices[0].delta.content is not None):
                        
                        content = chunk.choices[0].delta.content
                        print(content, end='', flush=True)
                        collected_messages.append(content)
                except Exception as e:
                    print(f"\n[流处理警告: {str(e)}]", end='', flush=True)
                    continue
                    
            print()  # 完成后换行
            return ''.join(collected_messages)
            
        except Exception as e:
            import traceback
            print(f"\n调试信息: {traceback.format_exc()}")
            raise RuntimeError(f"异步流式聊天请求失败: {str(e)}")

    def _make_model_id(self, model: List[str]) -> str:
        """生成模型唯一标识
        对于本地模型: 使用配置信息哈希值末尾4位
        对于在线模型: 使用api_key末尾4位
        """
        tee_api_key = model[2]
        model_type = model[3]
        
        if model_type == 'local':
            # 对模型配置列表进行哈希
            model_str = '_'.join(model)
            hash_obj = hashlib.md5(model_str.encode())
            tag = hash_obj.hexdigest()[-4:]
        else:
            api_key = self.tee.decrypt(tee_api_key)
            tag = api_key[-4:]
            # 安全考虑：使用后立即擦除api_key
            api_key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            
        return f"{model_type}_{tag}"

    def _check(self, model: List[str]) -> bool:
        """检查API连接和模型可用性，同时初始化同步和异步客户端"""
        try:
            model_name, base_url, tee_api_key, model_type = model
            model_id = self._make_model_id(model)
            
            # 获取API密钥
            if "TEE" in tee_api_key:
                api_key = self.tee.decrypt(tee_api_key)
            else:
                api_key = tee_api_key
                
            # 创建同步客户端实例
            sync_client = openai.OpenAI(
                base_url=base_url,
                api_key=api_key
            )
            
            # 创建异步客户端实例
            async_client = openai.AsyncOpenAI(
                base_url=base_url,
                api_key=api_key
            )
            
            # 安全考虑：使用后立即擦除api_key
            api_key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            
            # 发送测试请求（只用同步客户端测试）
            response = sync_client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            
            # 保存客户端实例
            self.id_client[model_id] = sync_client
            self.async_id_client[model_id] = async_client
            
            # 更新模型ID映射
            client_map = self.meta.Metadata.llms.client() or {}
            if model_name not in client_map:
                client_map[model_name] = []
            if model_id not in client_map[model_name]:
                client_map[model_name].append(model_id)
            self.meta.Metadata.llms.client(client_map)
            
            print(f"✓ 已连接 {model_name} ({model_id})")
            return True
                
        except Exception as e:
            print(f"✗ 初始化失败: {model_name} ({str(e)})")
            return False