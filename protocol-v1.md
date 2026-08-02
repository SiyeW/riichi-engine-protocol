# 进程协议 v1

状态：公开草案 1.0

## 1. 基础

协议名称：`riichi-engine-protocol`

当前版本：

```json
{
  "major": 1,
  "minor": 0
}
```

v1 使用 JSON-RPC 2.0 语义，通过 UTF-8 newline-delimited JSON（JSONL）传输。
本文只定义两类引擎共用的进程、生命周期、状态和错误。业务字段分别见
[决策引擎规范](decision-engine-v1.md)与[读牌引擎规范](opponent-analysis-engine-v1.md)。

## 2. 启动与传输

程序使用清单中的 executable 和 arguments 启动引擎：

```text
engine.exe --stdio
```

传输要求：

- stdin：程序到引擎，每行一个完整 JSON-RPC 消息。
- stdout：引擎到程序，每行一个完整 JSON-RPC 消息。
- stderr：普通日志、诊断信息和 Python traceback。
- 所有流必须使用 UTF-8。
- stdout 不得包含 banner、进度条或普通日志。
- 一条消息不得跨行。
- 引擎必须及时 flush stdout。
- 程序必须持续读取 stderr，避免管道阻塞。

程序不得通过 shell 拼接命令。executable 和 arguments 必须作为参数数组传给进程 API。

## 3. JSON-RPC 消息

### 3.1 请求

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "method": "engine.hello",
  "params": {}
}
```

### 3.2 成功响应

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "result": {}
}
```

### 3.3 错误响应

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "error": {
    "code": -32011,
    "message": "Weight is not compatible with this engine",
    "data": {
      "expectedFormat": "example-decision-onnx",
      "actualPath": "weights/model.pth"
    }
  }
}
```

### 3.4 通知

通知没有 `id`，接收方不得响应：

```json
{
  "jsonrpc": "2.0",
  "method": "engine.status",
  "params": {
    "state": "loading",
    "message": "Loading model weights"
  }
}
```

## 4. 生命周期

标准生命周期：

```text
spawn
  -> engine.hello
  -> engine.initialize
  -> analyze / predict / reset / cancel
  -> engine.shutdown
  -> process exit
```

引擎进程启动后不得自动加载默认权重。程序必须先完成 `engine.hello`，再通过
`engine.initialize` 指定配置。

## 5. 通用方法

### 5.1 `engine.hello`

用途：

- 协商协议版本
- 读取动态能力
- 验证启动到的程序是否与清单一致

请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "method": "engine.hello",
  "params": {
    "protocol": {
      "name": "riichi-engine-protocol",
      "major": 1,
      "minor": 0
    },
    "host": {
      "id": "example.host",
      "version": "1.2.0"
    }
  }
}
```

响应：

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "result": {
    "protocol": {
      "name": "riichi-engine-protocol",
      "major": 1,
      "minor": 0
    },
    "engine": {
      "id": "example.decision-engine",
      "name": "Example Decision Engine",
      "version": "1.0.0",
      "kinds": ["decision"],
      "modelFormats": [
        {
          "id": "example-legacy-decision-onnx",
          "extensions": [".onnx"],
          "inputSchema": "example-legacy-observation-v1",
          "outputSchema": "decision-v1"
        },
        {
          "id": "example-decision-onnx",
          "extensions": [".onnx"],
          "inputSchema": "example-decision-observation-v1",
          "outputSchema": "decision-v1"
        }
      ]
    },
    "capabilities": {
      "multipleSessions": true,
      "incrementalHistory": true,
      "concurrentRequests": false,
      "rawValues": true,
      "probabilities": true,
      "cancellation": true,
      "reload": true,
      "batching": false
    },
    "optionsSchema": {
      "type": "object",
      "properties": {}
    }
  }
}
```

要求：

- `engine.id` 必须与 `engine.json` 相同。
- `engine.modelFormats` 是选择权重文件时的权威兼容格式；宿主不得按引擎名称猜测扩展名或输入版本。
- 协议 major 不同则程序必须拒绝连接。
- 引擎 minor 小于程序请求时，程序只能使用双方共同支持的能力。
- 动态能力可以比静态清单更保守，但不得声明清单中不存在的危险权限。
- 对手分析引擎通过 `opponentInputModes` 声明实现能够支持的输入模式。
- `optionsSchema` 是当前引擎参数的权威定义；程序必须通过握手读取，而不能硬编码温度等参数名。

### 5.2 `engine.initialize`

用途：加载一个模型配置。

请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-2",
  "method": "engine.initialize",
  "params": {
    "profileId": "profile.decision.default",
    "kind": "decision",
    "model": {
      "id": "example.decision-model.default",
      "format": "example-decision-onnx",
      "path": "C:\\Models\\Example\\model.onnx",
      "expectedSha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    },
    "device": {
      "type": "cpu"
    },
    "options": {}
  }
}
```

响应：

```json
{
  "jsonrpc": "2.0",
  "id": "host-2",
  "result": {
    "state": "ready",
    "engineId": "example.decision-engine",
    "engineVersion": "1.0.0",
    "model": {
      "id": "example.decision-model.default",
      "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
      "format": "example-decision-onnx"
    },
    "device": {
      "type": "cpu",
      "displayName": "CPU"
    },
    "effectiveOptions": {},
    "capabilities": {
      "multipleSessions": true,
      "incrementalHistory": true
    },
    "outputSchema": "decision-v1",
    "outputSchemaVersion": 1,
    "fingerprint": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  }
}
```

要求：

- 引擎必须在耗时加载前发送 `engine.status=loading`。
- `model.path` 是程序解析后的本机绝对路径；引擎不得依赖进程工作目录。
- `model.id` 是稳定身份，`model.format` 必须是引擎清单声明的格式之一。
- 初始化结果中的 `capabilities` 是当前权重和有效参数下的最终能力，优先于 hello
  返回的引擎级能力。
- `effectiveOptions` 必须包含应用默认值并完成校验后的最终参数，并参与指纹计算。
- `outputSchema` 必须与所选模型格式声明的输出 Schema 一致；宿主按引擎类型强制校验。
- `fingerprint` 是当前引擎、权重、有效参数和结果语义的稳定身份；业务响应在
  `engineFingerprint` 字段回显它。
- 摘要存在时必须校验；不匹配必须失败。
- 权重结构不兼容必须返回 `WEIGHT_INCOMPATIBLE`，不得忽略未知层继续运行。
- 初始化成功前不得接受分析任务。
- 重新调用 initialize 等价于卸载旧配置并初始化新配置。

### 5.3 `engine.reload`

用途：重新读取当前配置的权重。适用于同一路径文件被替换。

请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-3",
  "method": "engine.reload",
  "params": {
    "reason": "user-request"
  }
}
```

行为：

- 取消或拒绝尚未开始的任务。
- 等待或取消正在运行的任务。
- 清除所有会话增量状态。
- 重新计算模型摘要和引擎指纹。
- 发送 `engine.status=reloading`，成功后发送 `ready`。

不支持热重载的引擎在 hello 中声明 `reload=false`。程序随后通过重启进程实现重载。

### 5.4 `engine.getStatus`

响应示例：

```json
{
  "state": "ready",
  "activeTasks": 0,
  "queuedTasks": 0,
  "fingerprint": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "lastError": null
}
```

程序不应依赖高频轮询。正常状态变化通过通知推送，`engine.getStatus` 只用于恢复同步和调试。

### 5.5 `session.reset`

请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-20",
  "method": "session.reset",
  "params": {
    "sessionId": "game-17:seat-2:play"
  }
}
```

引擎只清除指定会话，不得清除其他座位或用途的会话。未知会话重置视为成功。

### 5.6 `session.close`

释放指定会话。程序离开牌谱、删除分支或切换引擎时应该关闭不再使用的会话。

### 5.7 `request.cancel`

请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-30",
  "method": "request.cancel",
  "params": {
    "requestId": "host-29",
    "reason": "position-superseded"
  }
}
```

取消是 best-effort：

- 排队中的任务应该立即取消。
- 正在推理的任务可以在安全点取消。
- 无法中断的推理可以完成，但程序必须丢弃过时结果。
- 被取消的原请求返回 `REQUEST_CANCELED`。

支持取消的引擎必须使用独立读取线程，使其在推理期间仍能读取取消请求。

### 5.8 `engine.shutdown`

引擎停止接收新任务，清理资源并返回成功。程序随后等待进程退出；超过宽限时间后可以强制
终止。

## 6. `decision` 方法

`decision` 引擎实现 `decision.analyze`。完整请求、结果、候选动作、评分组及概率约束只在
[决策引擎规范 v1](decision-engine-v1.md)定义。

通用传输层只规定该方法：

- 使用 JSON-RPC 请求 ID 关联一次调用；
- 遵守初始化得到的 `outputSchema: decision-v1`；
- 成功时返回一个 JSON 对象，失败时返回标准 JSON-RPC 错误；
- 在方法执行期间按需发送 `task.status` 通知。

## 7. `opponent-analysis` 方法

`opponent-analysis` 引擎实现 `opponent.predict`。完整请求、结果、可见性、向听与振听
语义、精确零及规则修饰只在
[读牌引擎规范 v1](opponent-analysis-engine-v1.md)定义。

通用传输层只规定该方法：

- 使用 JSON-RPC 请求 ID 关联一次调用；
- 遵守初始化得到的 `outputSchema: opponent-analysis-v1`；
- 成功时返回一个 JSON 对象，失败时返回标准 JSON-RPC 错误；
- 在方法执行期间按需发送 `task.status` 通知。

## 8. 状态通知

### 8.1 `engine.status`

```json
{
  "jsonrpc": "2.0",
  "method": "engine.status",
  "params": {
    "state": "loading",
    "message": "Loading decision model",
    "error": null
  }
}
```

允许状态：

- `starting`
- `loading`
- `ready`
- `reloading`
- `error`
- `stopping`
- `stopped`

`error` 时必须附带结构化错误：

```json
{
  "code": "WEIGHT_INCOMPATIBLE",
  "message": "Checkpoint observation version is 3, expected 4",
  "recoverable": true
}
```

### 8.2 `task.status`

```json
{
  "jsonrpc": "2.0",
  "method": "task.status",
  "params": {
    "requestId": "host-101",
    "sessionId": "game-17:seat-2:recommendation",
    "kind": "decision",
    "seat": 2,
    "role": "recommendation",
    "state": "running",
    "queueDepth": 0
  }
}
```

允许状态：

- `queued`
- `running`
- `completed`
- `canceled`
- `error`

程序是界面状态的最终来源。若引擎没有来得及发送错误通知便退出，程序仍必须根据进程退出
合成 `error`。

## 9. 错误码

JSON-RPC 标准错误保持原定义。引擎专用错误使用 server error 范围：

| code | symbolic name | 含义 |
| --- | --- | --- |
| `-32010` | `ENGINE_NOT_INITIALIZED` | 尚未成功初始化 |
| `-32011` | `WEIGHT_INCOMPATIBLE` | 权重格式或结构不兼容 |
| `-32012` | `MODEL_NOT_FOUND` | 权重文件不存在 |
| `-32013` | `SESSION_INVALID` | 会话参数非法 |
| `-32014` | `REQUEST_CANCELED` | 请求已取消 |
| `-32015` | `ENGINE_BUSY` | 引擎拒绝更多任务 |
| `-32016` | `UNSUPPORTED_CAPABILITY` | 请求了未声明能力 |
| `-32017` | `INVALID_INPUT` | 输入事件或候选非法 |
| `-32018` | `INVALID_MODEL_OUTPUT` | 模型输出包含非法值 |
| `-32019` | `ENGINE_INTERNAL_ERROR` | 未分类内部错误 |

错误 `data` 不得包含完整暗牌、完整权重内容或敏感系统环境变量。

## 10. 限制与保护

程序默认限制：

- 单条协议消息：8 MiB
- 单个 stderr 行：256 KiB
- hello：5 秒
- initialize/reload：180 秒
- 交互推理：由程序设置，默认 120 秒硬超时
- shutdown 宽限：5 秒

实现可以调整限制，但必须防止无界 stdout、无界任务队列和无限重启。
