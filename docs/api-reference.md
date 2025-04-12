# AIVK API 参考 | API Reference | APIリファレンス

## 核心 API | Core API | コアAPI

### AivkExecuter | AIVK执行器 | AIVKエグゼキューター

命令执行工具类。  
Command execution utility class.  
コマンド実行ユーティリティクラス。

#### 同步执行 | Sync Execution | 同期実行

```python
@classmethod
def exec(
    command: Union[str, List[str]],    # 命令 | Command | コマンド
    working_dir: Optional[str] = None,  # 工作目录 | Working dir | 作業ディレクトリ
    env: Optional[Dict[str, str]] = None, # 环境变量 | Env vars | 環境変数
    timeout: Optional[float] = None,    # 超时 | Timeout | タイムアウト
    encoding: str = 'utf-8',           # 编码 | Encoding | エンコーディング
    check: bool = True,                # 检查 | Check | チェック
    shell: bool = True                 # Shell | シェル
) -> AivkExecResult:
    """
    同步执行外部命令。
    Synchronously execute external command.
    外部コマンドを同期実行します。
    """
```

#### 异步执行 | Async Execution | 非同期実行

```python
@classmethod
async def aexec(
    command: Union[str, List[str]],
    working_dir: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    encoding: str = 'utf-8',
    check: bool = True,
    shell: bool = True
) -> AivkExecResult:
    """
    异步执行外部命令。
    Asynchronously execute external command.
    外部コマンドを非同期実行します。
    """
```

### aivk_on | AIVK操作 | AIVK操作

从 `AivkCLI` 类调用的方法，用于动态获取特定操作的函数。  
Method called from `AivkCLI` class to dynamically get the function for a specific action.  
`AivkCLI` クラスから呼び出され、特定のアクションに対応する関数を動的に取得するメソッド。

```python
# 在 base/cli.py 中定义
@classmethod
def on(cls, action: str, id: str) -> callable:
    """
    动态导入并返回指定模块和操作的函数。
    Dynamically imports and returns the function for the specified module and action.
    指定されたモジュールとアクションの関数を動的にインポートして返します。

    Args:
        action (str): 操作名称 (如 "load", "unload", "install", "cli")。 | Action name (e.g., "load", "unload", "install", "cli"). | アクション名（例：「load」、「unload」、「install」、「cli」）。
        id (str): 模块 ID (如 "aivk", "fs")。 | Module ID (e.g., "aivk", "fs"). | モジュールID（例：「aivk」、「fs」）。

    Returns:
        callable: 对应操作的函数。 | The function for the corresponding action. | 対応するアクションの関数。

    Raises:
        ImportError: 如果模块或函数无法导入。 | If the module or function cannot be imported. | モジュールまたは関数をインポートできない場合。
        ValueError: 如果 ID 无效。 | If the ID is invalid. | IDが無効な場合。
    """
    # ... 实现细节 ...
```

*注意：* `onCli/__main__.py` 中使用的 `aivk.on(...)` 是 `AivkCLI` 实例上的调用，它内部使用了上述类方法。

### AivkCLI | AIVK命令行接口基类 | AIVKコマンドラインインターフェース基底クラス

用于构建命令行节点树的基础模型。  
Base model for building the command-line node tree.  
コマンドラインノードツリーを構築するための基本モデル。

```python
# 定义在 base/cli.py
class AivkCLI(BaseModel, NodeMixin):
    cli_parent : Optional["AivkCLI"] = None # 父节点 | Parent node | 親ノード
    nodes : dict[str, "AivkCLI"] = {}     # 子节点字典 | Child node dictionary | 子ノード辞書
    id: str                               # 节点 ID | Node ID | ノードID
    cli: Optional[click.Group] = None     # Click 命令组 | Click command group | Clickコマンドグループ

    # ... 其他方法和配置 ...
```

### AivkGroup | AIVK命令组 | AIVKコマンドグループ

自定义的 `click.Group`，支持动态加载命令。  
Custom `click.Group` that supports dynamic command loading.  
動的なコマンドロードをサポートするカスタム `click.Group`。

```python
# 定义在 base/cli.py
class AivkGroup(click.Group):
    def list_commands(self, ctx):
        # ... 列出命令 ...
        pass

    def get_command(self, ctx, cmd_name):
        # ... 获取命令，如果不存在则尝试通过 AivkCLI.on(action="cli", id=cmd_name) 动态加载 ...
        pass
```

## 异常类 | Exception Classes | 例外クラス

### AivkException | AIVK异常 | AIVK例外

所有 AIVK 异常的基类。  
Base class for all AIVK exceptions.  
すべての AIVK 例外の基底クラス。

```python
class AivkException(Exception):
    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化异常。
        Initialize exception.
        例外を初期化します。
        """
```

### 专用异常 | Specific Exceptions | 特定の例外

```python
class AivkNotFoundError(AivkException): ...     # 未找到 | Not found | 見つかりません
class AivkModuleError(AivkException): ...       # 模块错误 | Module error | モジュールエラー
class AivkConfigError(AivkException): ...       # 配置错误 | Config error | 設定エラー
class AivkNetworkError(AivkException): ...      # 网络错误 | Network error | ネットワークエラー
class AivkFileError(AivkException): ...         # 文件错误 | File error | ファイルエラー
```

## 数据模型 | Data Models | データモデル

### AivkExecResult | 执行结果 | 実行結果

命令执行结果的数据类。  
Data class for command execution results.  
コマンド実行結果のデータクラス。

```python
@dataclass
class AivkExecResult:
    returncode: int    # 返回码 | Return code | リターンコード
    stdout: str        # 标准输出 | Standard output | 標準出力
    stderr: str        # 错误输出 | Error output | エラー出力
    success: bool      # 成功标志 | Success flag | 成功フラグ
    command: str       # 执行的命令 | Executed command | 実行したコマンド
```

### ErrorInfo | 错误信息 | エラー情報

错误信息的数据类。  
Data class for error information.  
エラー情報のデータクラス。

```python
@dataclass
class ErrorInfo:
    code: int          # 错误码 | Error code | エラーコード
    message: str       # 错误消息 | Error message | エラーメッセージ
    details: dict      # 详细信息 | Details | 詳細情報
    timestamp: str     # 时间戳 | Timestamp | タイムスタンプ
```

## 事件系统 | Event System | イベントシステム

### 事件类型 | Event Types | イベントタイプ

```python
class AivkEventType(Enum):
    """
    AIVK事件类型。
    AIVK event types.
    AIVKイベントタイプ。
    """
    MODULE_LOAD = "module_load"           # 模块加载 | Module load | モジュールロード
    MODULE_UNLOAD = "module_unload"       # 模块卸载 | Module unload | モジュールアンロード
    ERROR = "error"                       # 错误 | Error | エラー
    STATE_CHANGE = "state_change"         # 状态改变 | State change | 状態変更
```

### 事件处理 | Event Handling | イベント処理

```python
async def on_event(
    event_type: AivkEventType,
    handler: Callable[[Dict[str, Any]], Awaitable[None]]
) -> None:
    """
    注册事件处理器。
    Register event handler.
    イベントハンドラーを登録します。
    """
```

## 配置系统 | Configuration System | 設定システム

### 配置访问 | Configuration Access | 設定アクセス

```python
def get_config(
    key: str,
    default: Any = None
) -> Any:
    """
    获取配置值。
    Get configuration value.
    設定値を取得します。
    """

def set_config(
    key: str,
    value: Any
) -> None:
    """
    设置配置值。
    Set configuration value.
    設定値を設定します。
    """
```

### 配置验证 | Configuration Validation | 設定検証

```python
def validate_config(
    config: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    """
    验证配置。
    Validate configuration.
    設定を検証します。
    """
```

## 使用示例 | Usage Examples | 使用例

### 命令执行 | Command Execution | コマンド実行

```python
# 同步执行 | Sync execution | 同期実行
result = AivkExecuter.exec("ls -l")
if result.success:
    print(result.stdout)

# 异步执行 | Async execution | 非同期実行
result = await AivkExecuter.aexec(
    ["docker", "build", "."],
    working_dir="/path/to/project"
)
```

### 模块操作 | Module Operations | モジュール操作

```python
# 加载模块 | Load module | モジュールをロード
await aivk_on("load", "fs", path="/path/to/modules")

# 安装模块 | Install module | モジュールをインストール
await aivk_on("install", "net", version="1.0.0")

# onCli/__main__.py 中的示例用法
# 获取 load 函数
load_func = aivk.on("load", "aivk")
# 调用函数
asyncio.run(load_func(path="/path/to/modules"))

# 获取 install 函数
install_func = aivk.on("install", "aivk")
# 调用函数
asyncio.run(install_func(id="net"))

# 获取 list 函数
list_func = aivk.on("list", "aivk")
# 调用函数
asyncio.run(list_func())
```

### 错误处理 | Error Handling | エラー処理

```python
try:
    result = await AivkExecuter.aexec("invalid_command")
except AivkException as e:
    error_info = ErrorInfo(
        code=e.code,
        message=str(e),
        details=e.details
    )
    print(f"Error {error_info.code}: {error_info.message}")
```

### 事件监听 | Event Listening | イベントリスニング

```python
async def handle_error(event_data: Dict[str, Any]):
    """错误事件处理器 | Error event handler | エラーイベントハンドラー"""
    error_info = event_data["error"]
    print(f"Error occurred: {error_info.message}")

# 注册处理器 | Register handler | ハンドラーを登録
await on_event(AivkEventType.ERROR, handle_error)
```

## 最佳实践 | Best Practices | ベストプラクティス

### 异步操作 | Async Operations | 非同期操作

1. 优先使用异步 API | Prefer async APIs | 非同期APIを優先
2. 正确处理超时 | Handle timeouts properly | タイムアウトを適切に処理
3. 使用异步上下文管理器 | Use async context managers | 非同期コンテキストマネージャーを使用

### 错误处理 | Error Handling | エラー処理

1. 使用专用异常 | Use specific exceptions | 特定の例外を使用
2. 包含错误上下文 | Include error context | エラーコンテキストを含める
3. 实现优雅降级 | Implement graceful degradation | 優雅な機能低下を実装

### 资源管理 | Resource Management | リソース管理

1. 及时清理资源 | Clean up resources timely | リソースを適時クリーンアップ
2. 使用上下文管理器 | Use context managers | コンテキストマネージャーを使用
3. 监控资源使用 | Monitor resource usage | リソース使用状況を監視