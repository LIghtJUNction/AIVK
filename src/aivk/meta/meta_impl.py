import toml
from types import SimpleNamespace
from pathlib import Path

class MetaLoader:
    def __init__(self, filename: str):
        self.path = Path(filename)
        self._meta = toml.load(self.path) if self.path.exists() else {}
        self.data = self._dict_to_namespace(self._meta)

    def _dict_to_namespace(self, d):
        """递归地将字典转换为 SimpleNamespace 对象"""
        if not isinstance(d, dict):
            return d
        ns = SimpleNamespace()
        for k, v in d.items():
            if isinstance(v, dict):
                setattr(ns, k, self._dict_to_namespace(v))
            elif isinstance(v, list):
                setattr(ns, k, [self._dict_to_namespace(item) if isinstance(item, dict) else item for item in v])
            else:
                setattr(ns, k, v)
        return ns

    def _namespace_to_dict(self, ns):
        """将 SimpleNamespace 对象转换回字典"""
        if not isinstance(ns, SimpleNamespace):
            return ns
        result = {}
        for k, v in ns.__dict__.items():
            if isinstance(v, SimpleNamespace):
                result[k] = self._namespace_to_dict(v)
            elif isinstance(v, list):
                result[k] = [self._namespace_to_dict(item) if isinstance(item, SimpleNamespace) else item for item in v]
            else:
                result[k] = v
        return result

    def __getattr__(self, name):
        """获取属性时，如果不存在则创建新的空命名空间"""
        try:
            return getattr(self.data, name)
        except AttributeError:
            setattr(self.data, name, SimpleNamespace())
            self._save()
            return getattr(self.data, name)

    def __setattr__(self, name, value):
        """设置属性时自动保存到文件"""
        if name in ['path', '_meta', 'data']:
            super().__setattr__(name, value)
            return
        
        if isinstance(value, dict):
            value = self._dict_to_namespace(value)
        setattr(self.data, name, value)
        self._meta = self._namespace_to_dict(self.data)
        self._save()

    def _save(self):
        """保存更改到 TOML 文件"""
        with open(self.path, 'w', encoding='utf-8') as f:
            toml.dump(self._meta, f)

    def __str__(self):
        return str(self._meta)