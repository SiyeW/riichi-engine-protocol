# 引擎包与模型配置格式 v1

状态：公开草案 1.0

本文规定引擎实现、模型权重和用户配置的组织方式。协议消息格式见
[protocol-v1.md](protocol-v1.md)。

## 1. 设计原则

- 引擎文件、模型权重和用户配置是三个独立选择，但一个可分发引擎目录应把引擎与默认权重放在一起。
- 一个引擎实现可以支持多个兼容权重。
- 一个权重可以被多个用户配置引用，但文件本身不应被重复复制。
- 用户配置只保存可编辑内容，不修改引擎包内的静态清单。
- 引擎和权重都必须有稳定 ID；显示名称可以修改，不可用作缓存键。
- 宿主不得用模型家族枚举代替引擎文件路径；所有引擎配置都应使用同一套普通用户配置机制。

业务输出 Schema 的语义分别由
[决策引擎规范](decision-engine-v1.md)和
[读牌引擎规范](opponent-analysis-engine-v1.md)定义；本文件只规定它们如何在包中声明。

## 2. 推荐目录结构

```text
engines/
  example-decision/
    engine.json
    runtime/
      example-decision-engine.exe
      _internal/
    models/
      default/
        model.json
        model.onnx
    LICENSE
    NOTICE
  example-opponent-analysis/
    engine.json
    runtime/
      example-opponent-analysis-engine.exe
      _internal/
    model.json
    model.onnx
profiles.json
```

已安装的引擎包可以位于只读目录。添加配置时，用户直接选择引擎文件与权重文件；程序也可以扫描同一目录中的 `engine.json` 和 `model.json` 提供预检信息。扫描结果不能取代用户配置中的实际文件路径。

## 3. `engine.json`

`engine.json` 描述一个可执行引擎实现，不包含用户选择的模型路径。

```json
{
  "$schema": "urn:riichi-engine-protocol:schema:engine-manifest:v1",
  "schemaVersion": 1,
  "id": "example.decision-engine",
  "name": "Example Decision Engine",
  "version": "1.0.0",
  "sourceUrl": "https://github.com/example/example-decision-engine",
  "protocol": {
    "name": "riichi-engine-protocol",
    "major": 1,
    "minor": 0
  },
  "kinds": ["decision"],
  "entrypoints": {
    "windows-x64": {
      "executable": "runtime/example-decision-engine.exe",
      "arguments": []
    }
  },
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
  ],
  "capabilities": {
    "multipleSessions": true,
    "incrementalHistory": true,
    "concurrentRequests": false,
    "cancellation": true,
    "reload": true,
    "batching": false,
    "rawValues": true,
    "probabilities": true
  },
  "optionsSchema": {
    "type": "object",
    "properties": {
      "temperature": {
        "type": "number",
        "minimum": 0,
        "default": 1,
        "x-ui": {
          "control": "number",
          "label": "温度"
        }
      }
    },
    "additionalProperties": false
  },
  "licenses": [
    {
      "name": "GNU Affero General Public License v3.0",
      "path": "LICENSE"
    }
  ],
  "notices": [
    {
      "name": "Third-party notices",
      "path": "THIRD_PARTY_NOTICES.md"
    }
  ]
}
```

### 3.1 路径规则

- 所有路径都相对于 `engine.json` 所在目录。
- 路径必须使用 `/`，不得是绝对路径，不得包含 `..`。
- `executable` 是文件路径，不是 Shell 命令。
- `arguments` 每一项作为独立参数传给进程；程序不得拼接后交给 Shell。
- 引擎管理器只能选择与当前平台匹配的入口。

### 3.2 `optionsSchema`

清单中的 `optionsSchema` 是安装前检查使用的静态提示；运行时
`engine.hello.optionsSchema` 才是权威参数定义。`x-ui` 是可选的界面提示，不影响校验语义。

v1 建议支持以下 `x-ui` 字段：

| 字段 | 含义 |
| --- | --- |
| `control` | `select`、`number`、`checkbox`、`text` 或 `path` |
| `label` | 本地化前的默认标签 |
| `description` | 简短说明 |
| `order` | 控件排序整数 |
| `advanced` | 是否放入高级设置 |

程序不认识 `x-ui` 时，仍应能依据标准 JSON Schema 生成基础控件。

### 3.3 对手分析输入能力

对手分析引擎在静态清单和 hello 中用 `opponentInputModes` 声明最大能力：

```json
{
  "opponentInputModes": ["public", "full-information"]
}
```

`public` 是必需模式，`full-information` 是可选模式。初始化具体权重后，引擎还要返回
该权重实际支持的模式；初始化结果不得超出静态清单和 hello 的声明。

## 4. `model.json`

`model.json` 描述一个模型权重及其兼容性。

```json
{
  "$schema": "urn:riichi-engine-protocol:schema:model-metadata:v1",
  "schemaVersion": 1,
  "id": "example.decision-model.default",
  "name": "Example Decision Model",
  "engineId": "example.decision-engine",
  "format": "example-decision-onnx",
  "file": "model.onnx",
  "sha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
  "sizeBytes": 95392490,
  "inputSchema": "example-decision-observation-v1",
  "outputSchema": "decision-v1",
  "training": {
    "createdAt": "2026-07-29T00:00:00Z",
    "description": "示例权重"
  },
  "license": {
    "name": "Project-specific model license",
    "path": "LICENSE"
  }
}
```

程序必须在首次载入、文件变更和用户要求重新载入时计算 SHA-256。文件摘要不匹配时不得静默继续，应把引擎状态设为 `error` 并提供明确错误信息。

对手分析模型可以在元数据中增加同名的 `opponentInputModes`，用于载入前的兼容性提示；
实际运行能力仍以引擎初始化结果为准。

## 5. 用户配置

用户配置引用引擎与权重，并保存显示名称和参数：

```json
{
  "schemaVersion": 1,
  "decisionProfiles": [
    {
      "id": "profile.decision.default",
      "name": "Example Decision Model",
      "enginePath": "engines/example_decision_engine/runtime/example-engine.exe",
      "engineId": "example.decision-engine",
      "modelPath": "engines/example_decision_engine/models/default/model.onnx",
      "modelId": "example.decision-model.default",
      "enabled": true,
      "options": {
        "temperature": 1
      }
    }
  ],
  "opponentAnalysisProfiles": [
    {
      "id": "profile.opponent-analysis.default",
      "name": "Example Opponent Model",
      "enginePath": "engines/example_opponent_engine/runtime/example-opponent-engine.exe",
      "engineId": "example.opponent-analysis-engine",
      "modelPath": "engines/example_opponent_engine/models/default/model.onnx",
      "modelId": "example.opponent-model.default",
      "enabled": true,
      "options": {}
    }
  ],
  "selectedDecisionProfileId": "profile.decision.default",
  "selectedOpponentAnalysisProfileId": "profile.opponent-analysis.default"
}
```

同一时间分别选择一个决策引擎配置和一个对手分析引擎配置。四个座位统一使用所选决策配置，座位隔离由会话负责，不再为四家分别选择权重。

配置列表允许：

- 新增、复制、重命名和删除用户配置。
- 上移、下移以改变显示顺序。
- 修改模型、引擎参数和显示名称。
- 启用或停用配置。

删除用户配置不得隐式删除它引用的引擎包或模型文件；包资源应通过独立的卸载流程管理。

## 6. 身份与缓存

引擎初始化后返回的 `engineFingerprint` 至少应覆盖：

- 引擎 ID 与版本。
- 协议主版本。
- 可执行文件内容摘要或发布构建 ID。
- 模型权重 SHA-256。
- 会影响结果的有效参数。
- 输出 Schema 版本。

缓存不得只按显示名称或文件名识别模型。任何影响引擎原始结果的部分发生变化，都必须
产生不同的引擎指纹。引擎内部的规则修饰版本也必须反映在该指纹中。

## 7. 分发与许可

公开分发的引擎包必须在 `licenses` 中列出适用的完整许可证文本，在
`notices` 中列出必要的版权、归属和第三方声明。宿主应向用户显示这些文档的名称，并提供直接打开入口；`sourceUrl` 应指向与该二进制版本对应、可实际取得的源码。

仅附带许可证文件不自动满足全部许可义务。发布者仍须按实际许可证保留版权与修改声明、提供必要的 NOTICE，并在 GPL/AGPL 等许可证要求时随目标代码提供对应源码或有效的源码获取方式。界面入口不能代替发行包内应包含的完整文件。

第三方引擎是可执行代码，安装界面必须明确提示其来源和风险。

进程边界不改变引擎原有许可证义务，也不应被当作规避开源许可证的手段。发布者应分别确认程序、引擎代码和模型权重的再分发条件。
