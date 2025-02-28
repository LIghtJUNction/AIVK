from . import Base
from cryptography.fernet import Fernet
import base64
import os
import hashlib
import secrets
import tkinter as tk
from tkinter import simpledialog
import stat
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class SecurityError(Exception):
    """安全错误异常"""
    pass

class Tee(Base):
    """
    Tee class - 提供安全的加密存储功能
    使用AIVKey进行加密，需要密码验证才能解密
    数据结构化存储在Meta文件中
    """
    def __init__(self):
        super().__init__()
        self._aiv_key = None
        self._last_password = None  # 添加密码缓存
        self._secure_storage_path = os.path.join(
            os.path.expanduser('~'),
            '.aivk',
            '.secure'
        )
        self._init_secure_storage()
        
    def _init_secure_storage(self):
        """增强安全存储初始化"""
        if not os.path.exists(self._secure_storage_path):
            os.makedirs(self._secure_storage_path)
            
            # 在Windows上设置ACL
            if os.name == 'nt':
                import win32security
                import win32api
                import ntsecuritycon as con
                
                # 获取当前用户的SID
                user_sid = win32security.LookupAccountName(
                    None, win32api.GetUserName())[0]
                
                # 创建新的DACL
                dacl = win32security.ACL()
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    con.FILE_ALL_ACCESS,
                    user_sid
                )
                
                # 应用安全描述符
                sd = win32security.SECURITY_DESCRIPTOR()
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(
                    self._secure_storage_path, 
                    win32security.DACL_SECURITY_INFORMATION,
                    sd
                )

    def _get_password(self):
        """弹出窗口获取密码"""
        root = tk.Tk()
        root.withdraw()
        # 将窗口置顶
        root.attributes('-topmost', True)
        
        # 修复这里的解包错误
        password = simpledialog.askstring(
            "安全验证", 
            "请输入密码以继续:", 
            show='*'
        )
        
        root.destroy()
        return password

    def _generate_tee_id(self):
        """生成唯一的TEE ID"""
        return f"TEE-{secrets.token_hex(6).upper()}"

    def setup_key(self):
        """首次设置AIVKey"""
        password = self._get_password()
        if not password:
            raise ValueError("未提供密码")
            
        # 缓存密码
        self._last_password = password
            
        # 生成AIVKey
        aiv_key = Fernet.generate_key()
        
        # 生成密码哈希
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # 生成密钥派生哈希
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=password.encode(),
            iterations=100000,
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(aiv_key))
        key_hash = hashlib.sha256(derived_key).hexdigest()
        
        # 保存两个哈希值
        self.meta.Metadata.AIVKey([password_hash, key_hash])
        
        # 安全保存真实的AIVKey
        secure_path = os.path.join(self._secure_storage_path, '.aivkey')
        with open(secure_path, 'wb') as f:
            f.write(aiv_key)
        os.chmod(secure_path, stat.S_IRUSR | stat.S_IWUSR)

    def encrypt(self, data, description):
        """加密数据并保存"""
        if not isinstance(data, (str, bytes)):
            raise ValueError("数据必须是字符串或字节")
            
        if not description:
            raise ValueError("必须提供描述")
        
        try:
            # 获取或加载AIVKey
            if not hasattr(self, '_aiv_key') or self._aiv_key is None:
                aiv_key_path = os.path.join(self._secure_storage_path, '.aivkey')
                if not os.path.exists(aiv_key_path):
                    raise ValueError("找不到AIVKey，请先初始化密码")
                with open(aiv_key_path, 'rb') as f:
                    self._aiv_key = f.read()
            
            # 创建加密器
            fernet = Fernet(self._aiv_key)
            
            # 将数据转换为字节并加密
            if isinstance(data, str):
                data = data.encode()
            encrypted_data = fernet.encrypt(data)
            
            # 生成唯一ID
            tee_id = self._generate_tee_id()
            
            # 保存加密数据
            secure_path = os.path.join(self._secure_storage_path, tee_id)
            with open(secure_path, 'wb') as f:
                f.write(encrypted_data)
            os.chmod(secure_path, stat.S_IRUSR | stat.S_IWUSR)
            
            # 保存描述信息到Meta
            tee_data = self.meta.Metadata.tee() or {}
            tee_data[f"{tee_id}.description"] = [
                description,
                str(data)[-4:] if len(str(data)) > 4 else "****"
            ]
            self.meta.Metadata.tee(tee_data)
            
            return tee_id
            
        except Exception as e:
            raise RuntimeError(f"加密失败: {str(e)}") from e

    def decrypt(self, tee_id):
        """解密数据"""
        try:
            # 获取存储的哈希值
            stored_hash = self.meta.Metadata.AIVKey()
            if not stored_hash:
                raise ValueError("未找到密码哈希")
            
            # 如果没有缓存的密码，获取新密码
            if not self._last_password:
                password = self._get_password()
                if not password:
                    raise ValueError("未提供密码")
                self._last_password = password
                
            # 验证密码
            current_hash = hashlib.sha256(self._last_password.encode()).hexdigest()
            if isinstance(stored_hash, list):
                # 如果是列表格式，取第一个值（密码哈希）
                stored_hash = stored_hash[0]
                
            if current_hash != stored_hash:
                # 密码错误，清除缓存
                self._last_password = None
                raise ValueError("密码错误")
                
            # 读取加密数据
            secure_path = os.path.join(self._secure_storage_path, tee_id)
            if not os.path.exists(secure_path):
                raise ValueError(f"未找到ID为 {tee_id} 的加密数据")
                
            # 获取或加载AIVKey
            if not self._aiv_key:
                aiv_key_path = os.path.join(self._secure_storage_path, '.aivkey')
                if not os.path.exists(aiv_key_path):
                    raise ValueError("找不到AIVKey")
                with open(aiv_key_path, 'rb') as f:
                    self._aiv_key = f.read()
            
            # 读取并解密数据
            with open(secure_path, 'rb') as f:
                encrypted_data = f.read()
                
            # 使用Fernet解密
            fernet = Fernet(self._aiv_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return decrypted_data.decode()
            
        except Exception as e:
            # 出现错误时清除密码缓存
            self._last_password = None
            raise e

    def verify_integrity(self):
        """验证密钥和哈希的完整性"""
        try:
            if not self._last_password:
                return False
                
            # 获取存储的哈希值
            stored_hashes = self.meta.Metadata.AIVKey()
            if not isinstance(stored_hashes, list) or len(stored_hashes) != 2:
                return False
                
            password_hash, stored_key_hash = stored_hashes
            
            # 验证密码哈希
            current_password_hash = hashlib.sha256(self._last_password.encode()).hexdigest()
            if current_password_hash != password_hash:
                return False
            
            # 验证密钥派生哈希
            with open(os.path.join(self._secure_storage_path, '.aivkey'), 'rb') as f:
                aiv_key = f.read()
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self._last_password.encode(),
                iterations=100000,
            )
            derived_key = base64.urlsafe_b64encode(kdf.derive(aiv_key))
            current_key_hash = hashlib.sha256(derived_key).hexdigest()
            
            return current_key_hash == stored_key_hash
        except:
            return False