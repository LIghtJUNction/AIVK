# aivk-module-sample
 module-sample

moduleID : 唯一标识符 模块文件夹/moduleID
特殊模块ID(唯一性):
loader : 模块加载器 -- 前置 -- 核心
frontend : 前端模块 -- 前置
backend : 后端模块 -- 前置
webui : 前后端模块 -- 一般模块

模块依赖管理：
由loader模块负责加载和管理模块依赖

模块安装/卸载/更新/：由loader模块负责安装/卸载/更新模块

# 模块开发指南

aivk模块是一个压缩包/python包
aivk模块集合也是一个压缩包/包含多个模块

刷入模块
1. 通过loader模块安装aivk模块
1.1. 通过模块集刷入模块

- moduleID.zip : 单个aivk模块
moduleID.py : 模块入口
meta.toml : 模块元数据

'''toml
type = "module"
modules = ['moduleID']
'''
- modules.zip : 模块集合
moduleID_1.zip : 单个aivk模块
moduleID_2.zip : 单个aivk模块
meta.toml : 模块集合元数据

meta.toml
'''toml
type = "modules"
modules = ["moduleID_1", "moduleID_2"]

顺序决定安装顺序，前置模块在前，一般模块在后。
如果模块依赖缺失：安装失败
'''
支持嵌套模块集合

1. 通过python包刷入aivk模块
适合：
- 需要频繁更新的模块
- 需要调用大量第三方库的模块

调用loader刷入
