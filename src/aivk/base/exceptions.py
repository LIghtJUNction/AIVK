"""AIVK 异常处理模块"""
from typing import Optional, Dict, Any

# 错误代码常量
ERROR_CODES = {
    # 通用错误 (1-99)
    "NOT_FOUND": 1,
    "INVALID_ARGUMENT": 2,
    "PERMISSION_DENIED": 3,
    "TIMEOUT": 4,
    "ALREADY_EXISTS": 5,
    
    # 模块相关错误 (100-199)
    "MODULE_NOT_FOUND": 100,
    "MODULE_LOAD_FAILED": 101,
    "MODULE_UNLOAD_FAILED": 102,
    "MODULE_INSTALL_FAILED": 103,
    "MODULE_UPDATE_FAILED": 104,
    
    # 配置相关错误 (200-299)
    "CONFIG_NOT_FOUND": 200,
    "CONFIG_INVALID": 201,
    "CONFIG_WRITE_FAILED": 202,
    
    # 资源相关错误 (300-399)
    "RESOURCE_NOT_FOUND": 300,
    "RESOURCE_BUSY": 301,
    "RESOURCE_EXHAUSTED": 302,
    
    # 网络相关错误 (400-499)
    "NETWORK_ERROR": 400,
    "CONNECTION_FAILED": 401,
    "REQUEST_TIMEOUT": 402,
    
    # 文件系统错误 (500-599)
    "FILE_NOT_FOUND": 500,
    "FILE_ACCESS_DENIED": 501,
    "FILE_ALREADY_EXISTS": 502,
}

class AivkException(Exception):
    """AIVK 异常基类"""
    def __init__(self, message: str, code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"

class AivkNotFoundError(AivkException):
    """请求的资源未找到时抛出的异常"""
    def __init__(self, message: str, resource_type: Optional[str] = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(message, ERROR_CODES["NOT_FOUND"], details)

class AivkModuleError(AivkException):
    """模块操作相关异常"""
    def __init__(self, id: str, operation: str , message: str):
        details = {
            'id': id,
            'operation': operation
        }
        self.message = f"{message} (ID: {id}, Operation: {operation})"
        super().__init__(message, ERROR_CODES["MODULE_LOAD_FAILED"], details)

class AivkConfigError(AivkException):
    """配置相关异常"""
    def __init__(self, message: str, config_path: Optional[str] = None):
        details = {"config_path": config_path} if config_path else {}
        super().__init__(message, ERROR_CODES["CONFIG_INVALID"], details)

class AivkResourceError(AivkException):
    """资源相关异常"""
    def __init__(self, message: str, resource_id: str):
        details = {"resource_id": resource_id}
        super().__init__(message, ERROR_CODES["RESOURCE_NOT_FOUND"], details)

class AivkNetworkError(AivkException):
    """网络相关异常"""
    def __init__(self, message: str, url: Optional[str] = None):
        details = {"url": url} if url else {}
        super().__init__(message, ERROR_CODES["NETWORK_ERROR"], details)

class AivkFileError(AivkException):
    """文件系统相关异常"""
    def __init__(self, message: str, file_path: str):
        details = {"file_path": file_path}
        super().__init__(message, ERROR_CODES["FILE_NOT_FOUND"], details)

class AivkPermissionError(AivkException):
    """权限相关异常"""
    def __init__(self, message: str, required_permission: str):
        details = {"required_permission": required_permission}
        super().__init__(message, ERROR_CODES["PERMISSION_DENIED"], details)

class AivkTimeoutError(AivkException):
    """超时相关异常"""
    def __init__(self, message: str, timeout: float):
        details = {"timeout": timeout}
        super().__init__(message, ERROR_CODES["TIMEOUT"], details)

__all__ = [
    "ERROR_CODES",
    "AivkException",
    "AivkNotFoundError",
    "AivkModuleError",
    "AivkConfigError",
    "AivkResourceError",
    "AivkNetworkError", 
    "AivkFileError",
    "AivkPermissionError",
    "AivkTimeoutError"
]