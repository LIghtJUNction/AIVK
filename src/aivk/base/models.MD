# AIVK Models | AIVK 模型 | AIVK モデル

## Data Models | 数据模型 | データモデル

### ErrorInfo | 错误信息 | エラー情報
基础错误信息模型。用于封装错误的基本信息。  
Basic error information model. Used to encapsulate basic error information.  
基本エラー情報モデル。エラーの基本情報をカプセル化します。

```python
@dataclass
class ErrorInfo:
    code: int          # Error code | 错误代码 | エラーコード
    message: str       # Error message | 错误信息 | エラーメッセージ
    details: dict      # Additional details | 附加详情 | 追加詳細情報
    timestamp: str     # Error timestamp | 错误时间戳 | エラー発生時刻
```

### ErrorResponse | 错误响应 | エラーレスポンス
用于 API 响应的错误信息模型。包含更多上下文信息。  
Error information model for API responses. Contains more context information.  
API レスポンス用のエラー情報モデル。より多くのコンテキスト情報を含みます。

```python
@dataclass
class ErrorResponse:
    error: ErrorInfo     # Error info | 错误信息 | エラー情報
    success: bool        # Operation success flag | 操作成功标志 | 操作成功フラグ
    request_id: str      # Request tracking ID | 请求追踪ID | リクエスト追跡ID
    suggestions: list    # Helpful suggestions | 帮助建议 | ヘルプ提案
```

### ErrorLogEntry | 错误日志条目 | エラーログエントリ
用于日志记录的详细错误信息模型。  
Detailed error information model for logging.  
ログ記録用の詳細なエラー情報モデル。

```python
@dataclass
class ErrorLogEntry:
    error: ErrorInfo   # Error info | 错误信息 | エラー情報
    module: str        # Source module | 来源模块 | ソースモジュール
    function: str      # Function name | 函数名称 | 関数名
    stack_trace: str   # Stack trace | 堆栈跟踪 | スタックトレース
    user_info: dict    # User context | 用户上下文 | ユーザーコンテキスト
```

## Usage Examples | 使用示例 | 使用例

### Basic Error Info | 基本错误信息 | 基本エラー情報
```python
error_info = ErrorInfo(
    code=404,
    message="Resource not found",
    details={"resource_type": "file"},
    timestamp="2025-04-09T10:30:00Z"
)
```

### API Error Response | API错误响应 | APIエラーレスポンス
```python
response = ErrorResponse(
    error=error_info,
    success=False,
    request_id="req-123456",
    suggestions=[
        "Check if the file exists",
        "Verify file permissions"
    ]
)
```

### Error Logging | 错误日志记录 | エラーログ記録
```python
log_entry = ErrorLogEntry(
    error=error_info,
    module="fs",
    function="read_file",
    stack_trace="...",
    user_info={
        "user_id": "user123",
        "operation": "file_read"
    }
)
```

## Integration Examples | 集成示例 | 統合例

### With Exception System | 与异常系统集成 | 例外システムとの統合
```python
try:
    # Operation | 操作 | 操作
    raise AivkFileError("File not found", "/path/to/file")
except AivkException as e:
    error_info = ErrorInfo(
        code=e.code,
        message=str(e),
        details=e.details
    )
    log_entry = ErrorLogEntry(
        error=error_info,
        module=__name__,
        function="process_file",
        stack_trace=traceback.format_exc()
    )
```

### With HTTP API | 与HTTP API集成 | HTTP APIとの統合
```python
async def api_error_handler(request, error):
    """API error handler | API错误处理器 | APIエラーハンドラー"""
    error_info = ErrorInfo(
        code=error.code,
        message=str(error)
    )
    return ErrorResponse(
        error=error_info,
        success=False,
        request_id=request.id
    )
```

## Design Principles | 设计原则 | 設計原則

1. Extensibility | 可扩展性 | 拡張性
   - Easy to add new fields | 易于添加新字段 | 新しいフィールドの追加が容易
   - Compatible with various systems | 兼容多种系统 | 様々なシステムと互換

2. Consistency | 一致性 | 一貫性
   - Standard format | 标准格式 | 標準フォーマット
   - Predictable structure | 可预测的结构 | 予測可能な構造

3. Flexibility | 灵活性 | 柔軟性
   - Optional fields | 可选字段 | オプションフィールド
   - Custom extensions | 自定义扩展 | カスタム拡張