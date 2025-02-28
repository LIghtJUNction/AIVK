from datetime import datetime
from pathlib import Path
import toml
from typing import Any, Dict, List, Optional

class MetaNode:
    def __init__(self, root, path: List[str] = None):
        self._root = root
        self._path = path or []

    def __getattr__(self, name: str) -> Any:
        """访问属性时自动创建路径"""
        value = self._root._get(self._path + [name])
        
        # 对None值返回新节点,允许后续写入
        if value is None:
            return MetaNode(self._root, self._path + [name])
            
        # 包装字典和列表
        if isinstance(value, dict):
            return MetaNode(self._root, self._path + [name])
        if isinstance(value, list):
            return ListNode(self._root, self._path + [name], value)
            
        return value

    def __call__(self, value: Any = None) -> Any:
        """获取或设置值"""
        if value is None:
            return self._root._get(self._path)
            
        # 写入时自动创建路径
        curr = self._root._meta
        for p in self._path[:-1]:
            curr = curr.setdefault(p, {})
        curr[self._path[-1]] = value
        
        # 非延迟模式立即保存
        if not self._root._pending:
            self._root.save()
        return self

    def wait(self) -> 'MetaNode':
        """暂停自动保存"""
        self._root._pending = True
        return self

    def del_(self) -> 'MetaNode':
        """删除当前节点"""
        self._root._delete(self._path)
        return self

class ListNode:
    def __init__(self, root, path: List[str], value: list):
        self._root = root
        self._path = path
        self._value = value.copy()
        self._original = value.copy()
        self._pending = False

    def append(self, item: Any) -> 'ListNode':
        """添加项"""
        self._value.append(item)
        if not self._pending:
            self._root._set(self._path, self._value)
        return self

    def remove(self, index: int) -> 'ListNode':
        """删除项"""
        self._value.pop(index)
        if not self._pending:
            self._root._set(self._path, self._value)
        return self

    def __call__(self) -> list:
        """获取列表值"""
        return self._value.copy()

    def wait(self) -> 'ListNode':
        """暂停自动保存"""
        self._pending = True
        return self

    def save(self) -> None:
        """保存更改"""
        if self._pending:
            self._root._set(self._path, self._value)
            self._pending = False

class MetaLoader:
    def __init__(self, filename: str):
        self.path = Path(filename)
        self._meta = self._load()
        self._pending = False
        self._changes: Dict[str, Any] = {}

    def _load(self) -> dict:
        """加载配置文件"""
        return toml.load(self.path) if self.path.exists() else {}

    def _get(self, path: List[str]) -> Optional[Any]:
        """获取值"""
        curr = self._meta
        for p in path:
            if not isinstance(curr, dict) or p not in curr:
                return None
            curr = curr[p]
        return curr

    def _set(self, path: List[str], value: Any) -> None:
        """设置值"""
        if self._pending:
            self._changes['.'.join(path)] = value
        else:
            curr = self._meta
            for p in path[:-1]:
                curr = curr.setdefault(p, {})
            curr[path[-1]] = value
            self.save()

    def _delete(self, path: List[str]) -> None:
        """删除值"""
        curr = self._meta
        for p in path[:-1]:
            if p not in curr:
                return
            curr = curr[p]
        if path[-1] in curr:
            del curr[path[-1]]
            if not self._pending:
                self.save()

    def save(self) -> None:
        """保存到文件"""
        # 应用待保存的更改
        for path_str, value in self._changes.items():
            curr = self._meta
            path = path_str.split('.')
            for p in path[:-1]:
                curr = curr.setdefault(p, {})
            curr[path[-1]] = value

        # 清理状态并保存
        self._changes.clear()
        self._pending = False
        with open(self.path, 'w', encoding='utf-8') as f:
            toml.dump(self._meta, f)

    def __getattr__(self, name: str) -> MetaNode:
        return MetaNode(self, [name])

    def __str__(self) -> str:
        return str(self._meta)