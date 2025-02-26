from . import MetaLoader
import inspect
import os

class Base():
    """ base class for all classes """
    def __init__(self):
        # 获取子类的文件路径
        child_class = self.__class__
        child_module = inspect.getmodule(child_class)
        module_path = os.path.dirname(os.path.abspath(child_module.__file__))
        # 使用子类所在目录的Meta.toml
        self.meta = MetaLoader(os.path.join(module_path, 'Meta.toml'))