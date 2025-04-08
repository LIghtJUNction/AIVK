# AIVK Utilities | AIVK 实用工具 | AIVK ユーティリティ

## Core Functions | 核心函数 | コア関数

### aivk_on | AIVK 操作 | AIVK 操作

统一的 AIVK 模块操作函数。  
Unified AIVK module operation function.  
統一された AIVK モジュール操作関数。

```python
async def aivk_on(
    action: Literal["load", "unload", "install", "uninstall", "update"],
    id: str,
    **kwargs: Dict[str, Any]
) -> Any
```

#### Parameters | 参数 | パラメータ

| Name | Type | Description | 描述 | 説明 |
|------|------|-------------|------|------|
| action | str | Operation type | 操作类型 | 操作タイプ |
| id | str | Module ID | 模块ID | モジュールID |
| kwargs | dict | Extra parameters | 额外参数 | 追加パラメータ |

#### Actions | 操作 | アクション

- `load`: Load module | 加载模块 | モジュールをロード
- `unload`: Unload module | 卸载模块 | モジュールをアンロード
- `install`: Install module | 安装模块 | モジュールをインストール
- `uninstall`: Remove module | 移除模块 | モジュールを削除
- `update`: Update module | 更新模块 | モジュールを更新

### AivkExecuter | AIVK执行器 | AIVKエグゼキューター

命令执行工具类。提供同步和异步的命令执行功能。  
Command execution utility class. Provides both sync and async execution capabilities.  
コマンド実行ユーティリティクラス。同期・非同期実行機能を提供。

#### Methods | 方法 | メソッド

##### exec | 同步执行 | 同期実行
```python
@classmethod
def exec(
    cls,
    command: Union[str, List[str]],    # Command to execute | 要执行的命令 | 実行するコマンド
    working_dir: Optional[str] = None,  # Working directory | 工作目录 | 作業ディレクトリ
    env: Optional[Dict[str, str]] = None, # Environment vars | 环境变量 | 環境変数
    timeout: Optional[float] = None,    # Timeout seconds | 超时秒数 | タイムアウト秒数
    encoding: str = 'utf-8',           # Output encoding | 输出编码 | 出力エンコーディング
    check: bool = True,                # Raise on error | 错误时抛出异常 | エラー時に例外を発生
    shell: bool = True                 # Use shell | 使用shell | シェルを使用
) -> AivkExecResult:
    """同步执行命令"""
```

##### aexec | 异步执行 | 非同期実行
```python
@classmethod
async def aexec(
    cls,
    command: Union[str, List[str]],    # Command to execute | 要执行的命令 | 実行するコマンド
    working_dir: Optional[str] = None,  # Working directory | 工作目录 | 作業ディレクトリ
    env: Optional[Dict[str, str]] = None, # Environment vars | 环境变量 | 環境変数
    timeout: Optional[float] = None,    # Timeout seconds | 超时秒数 | タイムアウト秒数
    encoding: str = 'utf-8',           # Output encoding | 输出编码 | 出力エンコーディング
    check: bool = True,                # Raise on error | 错误时抛出异常 | エラー時に例外を発生
    shell: bool = True                 # Use shell | 使用shell | シェルを使用
) -> AivkExecResult:
    """异步执行命令"""
```

#### Return Value | 返回值 | 戻り値

```python
@dataclass
class AivkExecResult:
    returncode: int    # Return code | 返回代码 | リターンコード
    stdout: str        # Standard output | 标准输出 | 標準出力
    stderr: str        # Error output | 错误输出 | エラー出力
    success: bool      # Success flag | 成功标志 | 成功フラグ
    command: str       # Executed command | 执行的命令 | 実行したコマンド
```

## Usage Examples | 使用示例 | 使用例

### Module Operations | 模块操作 | モジュール操作

```python
# Load module | 加载模块 | モジュールをロード
await aivk_on("load", "fs", path="/path/to/modules")

# Install module | 安装模块 | モジュールをインストール
await aivk_on("install", "ai", version="1.0.0")
```

### Command Execution | 命令执行 | コマンド実行

```python
# Sync execution | 同步执行 | 同期実行
result = AivkExecuter.exec("git status")
if result.success:
    print(result.stdout)

# Async execution | 异步执行 | 非同期実行
result = await AivkExecuter.aexec(
    ["docker", "build", "."],
    working_dir="/path/to/project"
)
```

### Error Handling | 错误处理 | エラー処理

```python
try:
    result = await AivkExecuter.aexec("invalid_command")
except Exception as e:
    print(f"Command failed: {e}")
    print(f"Return code: {result.returncode}")
    print(f"Error output: {result.stderr}")
```

## Stats and Metadata | 统计和元数据 | 統計とメタデータ

AivkExecuter maintains execution statistics:  
AivkExecuter 维护执行统计信息：  
AivkExecuter は実行統計を維持します：

```python
stats = AivkExecuter.get_stats()
print(f"Total executions: {stats['total_execs']}")
print(f"Failed executions: {stats['failed_execs']}")
print(f"Success rate: {stats['success_rate']:.2%}")
```

## Best Practices | 最佳实践 | ベストプラクティス

1. Error Handling | 错误处理 | エラー処理
   - Always check result.success | 始终检查result.success | 常にresult.successを確認
   - Use try-except blocks | 使用try-except块 | try-exceptブロックを使用
   - Handle timeouts | 处理超时 | タイムアウトを処理

2. Resource Management | 资源管理 | リソース管理
   - Set appropriate timeouts | 设置适当的超时 | 適切なタイムアウトを設定
   - Clean up resources | 清理资源 | リソースをクリーンアップ
   - Use working_dir | 使用工作目录 | 作業ディレクトリを使用

3. Security | 安全性 | セキュリティ
   - Validate commands | 验证命令 | コマンドを検証
   - Sanitize inputs | 净化输入 | 入力をサニタイズ
   - Control environment | 控制环境 | 環境を制御