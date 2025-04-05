"""
AIVK 异常类定义模块
定义所有 AIVK 系统使用的自定义异常
"""

class AivkError(Exception):
    """AIVK 基础异常类，所有 AIVK 异常的基类"""
    def __init__(self, message: str = None):
        self.message = message or "AIVK 系统发生错误"
        super().__init__(self.message)


class AivkModuleError(AivkError):
    """与模块相关的异常基类"""
    def __init__(self, message: str = None):
        self.message = message or "AIVK 模块发生错误"
        super().__init__(self.message)


class AivkModuleNotFoundError(AivkModuleError):
    """无法找到模块时抛出"""
    def __init__(self, moduleID: str, message: str = None):
        self.moduleID = moduleID
        self.message = message or f"无法找到aivk模块: {moduleID}"
        super().__init__(self.message)


class AivkModuleLoadError(AivkModuleError):
    """加载模块失败时抛出"""
    def __init__(self, moduleID: str, reason: str = None):
        self.moduleID = moduleID
        self.reason = reason
        message = f"加载模块 {moduleID} 失败"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class AivkModuleEntryError(AivkModuleError):
    """无法找到模块入口点或入口点不符合要求时抛出"""
    def __init__(self, moduleID: str, reason: str = None):
        self.moduleID = moduleID
        self.reason = reason
        message = f"aivk模块 {moduleID} 的入口点不符合要求"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class AivkModuleConfigError(AivkError):
    """配置错误基类"""
    def __init__(self, moduleID: str, message: str = None):
        self.moduleID = moduleID
        self.message = message or f"aivk模块 {moduleID} 的配置错误"
        super().__init__(self.message)


class InvalidConfigError(AivkModuleConfigError):
    """配置无效时抛出"""
    def __init__(self, moduleID: str, config: str, message: str = None):
        self.moduleID = moduleID
        self.config = config
        self.message = message or f"aivk模块 {moduleID} 的配置 {config} 无效"
        super().__init__(self.moduleID, self.message)


class PermissionError(AivkError):
    """权限不足时抛出"""
    def __init__(self, permission: str, message: str = None):
        self.permission = permission
        self.message = message or f"权限不足: {permission}"
        super().__init__(self.message)


class DependencyError(AivkError):
    """依赖项错误时抛出"""
    def __init__(self, module: str, dependency: str, message: str = None):
        self.module = module
        self.dependency = dependency
        self.message = message or f"模块 {module} 依赖的 {dependency} 不可用"
        super().__init__(self.message)