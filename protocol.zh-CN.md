### [中文](protocol.zh-CN.md) | [日本語](protocol.ja-JP.md) | [English](protocol.en-US.md)

<div lang="zh-CN">

# Riichi Engine Protocol

引擎通过输出契约声明自己能够提供的数据。一个引擎可以同时提供多个输出，宿主也可以把不同输出交给不同的引擎配置。引擎的模型结构、训练方法和内部数据结构不属于协议。

引擎进程使用 JSON-RPC 2.0 和 JSONL 与宿主通信。本文定义引擎程序包、进程通信、牌局输入、输出声明、权重要求、初始化、分析请求和标准输出数据。牌局数据仅适用于四人立直麻将。

## 协议版本

协议标识固定为：

```json
{
  "name": "riichi-engine-protocol",
  "major": 2,
  "minor": 2
}
```

`major` 不同的双方不得继续通信。宿主在 `engine.hello` 请求中给出自己支持的最高 `minor`；引擎返回双方共同支持的最高 `minor`，不得高于宿主请求值。提高 `minor` 只能增加可忽略的字段、方法或能力，不得改变现有字段和方法的意义。

`engine.hello` 的结果及之后的消息必须符合协商后的 `minor`；引擎不得使用更高 `minor` 才新增的字段、取值、方法或能力。

输出契约具有独立版本。协议版本相同不表示双方支持相同输出；宿主只使用自己认识并且引擎已经声明的输出。引擎声明额外输出不得导致宿主拒绝整个引擎。

## 进程与传输

宿主直接启动引擎可执行文件，不通过 Shell 拼接命令。引擎从标准输入读取消息，向标准输出写入消息，并把日志写入标准错误。标准输入和标准输出使用 UTF-8；每行必须恰好包含一个完整 JSON 对象，以 `\n` 结束。协议行不得超过 8 MiB，空行可以忽略。

所有消息遵守 JSON-RPC 2.0：

| 消息 | 必需字段 | 说明 |
| --- | --- | --- |
| 请求 | `jsonrpc`、`id`、`method`、`params` | `jsonrpc` 固定为 `"2.0"`；`id` 是宿主生成的非空字符串或整数。 |
| 成功响应 | `jsonrpc`、`id`、`result` | `id` 必须与请求一致。 |
| 错误响应 | `jsonrpc`、`id`、`error` | `error` 的结构见“错误”一节。 |
| 通知 | `jsonrpc`、`method`、`params` | 不含 `id`，接收方不得回复。 |

宿主向引擎发送请求和通知；引擎只向宿主发送响应和通知，不反向调用宿主方法。一个请求必须恰好得到一个成功响应或错误响应。JSON 数值必须有限，布尔值不视为数值。

解析错误或无效请求导致接收方无法取得请求 ID 时，错误响应的 `id` 使用 `null`。除此之外，响应 ID 必须与请求完全一致。

## 引擎程序包

引擎程序包以 `engine.json` 作为入口。程序包可以位于只读目录；权重文件和用户设置不属于引擎程序包，也不写回该目录。

```json
{
  "schemaVersion": 2,
  "id": "example.engine",
  "name": "Example Engine",
  "version": "1.0.0",
  "sourceUrl": "https://github.com/example/example-engine",
  "protocol": {
    "name": "riichi-engine-protocol",
    "major": 2,
    "minor": 2
  },
  "entrypoints": {
    "windows-x64": {
      "executable": "runtime/example-engine.exe",
      "arguments": []
    }
  },
  "licenses": [
    {
      "name": "Apache License 2.0",
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

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `schemaVersion` | 是 | 固定为 `2`。 |
| `id` | 是 | 引擎稳定 ID，使用小写 ASCII 字母、数字、点和连字符，长度为 `3..128`。 |
| `name` | 是 | 面向用户的默认名称，长度为 `1..128`。 |
| `version` | 是 | 引擎版本，使用 Semantic Versioning。 |
| `sourceUrl` | 否 | 与当前程序包对应的公开源代码地址。 |
| `protocol` | 是 | 引擎实现的协议名称和最高版本。 |
| `entrypoints` | 是 | 非空平台入口对象。平台键使用小写 ASCII 字母、数字和连字符。 |
| `entrypoints.*.executable` | 是 | 相对于 `engine.json` 的可执行文件路径。 |
| `entrypoints.*.arguments` | 是 | 字符串参数数组；每项作为独立参数传递。 |
| `licenses` | 是 | 非空许可证文件数组。 |
| `licenses[].name` | 是 | 许可证名称。 |
| `licenses[].path` | 是 | 相对于 `engine.json` 的许可证文件路径。 |
| `notices` | 否 | 第三方声明等附加文件数组，字段与 `licenses` 相同。 |

程序包内路径统一使用 `/`，不得是绝对路径，不得包含空段、`.` 或 `..`，解析后必须仍位于程序包目录内。宿主只选择与当前平台完全匹配的入口，并把程序包目录作为进程工作目录。

`engine.json` 不声明引擎类型、输出、权重格式、参数或运行能力。宿主启动进程后必须以 `engine.hello` 为这些信息的唯一依据，并验证握手返回的引擎 ID 和版本与程序包一致。

## 通用数据类型

### 输出引用

输出引用用于握手、初始化和分析请求：

```json
{
  "id": "opponent-shanten",
  "version": 1
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 输出契约的稳定 ID。使用小写 ASCII 字母、数字和连字符，长度为 `3..128`。 |
| `version` | 是 | 输出契约主版本，值为不小于 `1` 的整数。 |

改变字段含义、概率条件、目标定义或删除既有字段时，必须提高 `version`。增加接收方可以忽略的可选字段不要求提高主版本。

### 多语言文本

引擎提供给用户阅读的标题和说明使用多语言文本对象：

```json
{
  "default": "Backbone weights",
  "en": "Backbone weights",
  "zh-CN": "主模型权重",
  "ja": "基盤モデルの重み"
}
```

| 键 | 必需 | 格式与意义 |
| --- | --- | --- |
| `default` | 是 | 找不到匹配语言时使用的文本，长度为 `1..256`。 |
| 其他键 | 否 | BCP 47 语言标签及其文本，长度为 `1..256`。 |

宿主依次尝试完整语言标签、主语言标签和 `default`。所有文本按纯文本显示，不解释 HTML、 Markdown 或终端控制字符。

### 概率与离散分布

概率必须是位于闭区间 `[0, 1]` 的有限 JSON 数值，不得为 `NaN` 或无穷大。概率分布的概率和在 `1e-4` 容差内必须为 `1`。

离散分布使用以下结构：

```json
[
  {"value": 1000, "probability": 0.10},
  {"value": 2000, "probability": 0.25},
  {"value": 3900, "probability": 0.45},
  {"value": 8000, "probability": 0.20}
]
```

`value` 必须是字符串或有限 JSON 数值，并且在同一分布中不得重复。数组顺序不具有协议意义；宿主可以根据输出契约和显示需要重新排列。每项的 `probability` 表示对应取值的概率，允许但未列出的取值视为概率 `0`。具体输出契约可以进一步限制 `value` 的类型和取值范围。

### 数值预测

数值预测使用以下结构：

```json
{
  "distribution": [
    {"value": 1000, "probability": 0.10},
    {"value": 2000, "probability": 0.25},
    {"value": 3900, "probability": 0.45},
    {"value": 8000, "probability": 0.20}
  ],
  "expectedValue": 3955,
  "pointEstimate": 3900
}
```

数值预测允许三种表示：

| 表示 | 对应字段 | 格式与意义 |
| --- | --- | --- |
| `distribution` | `distribution` | 离散概率分布。 |
| `expected-value` | `expectedValue` | 预测值的数学期望，必须是有限 JSON 数值。 |
| `point-estimate` | `pointEstimate` | 引擎直接给出的标量预测，必须是有限 JSON 数值。 |

数值预测中，`distribution` 的 `value` 必须是有限 JSON 数值，除非具体输出契约另行规定字符串区间。包含字符串区间的分布不能与 `expected-value` 同时使用，也不能用于派生标量。

当前引擎配置在初始化时确定每项输出使用哪些表示。声明的字段必须出现在之后的每个对应结果中，未声明的字段不得出现。若同时声明 `distribution` 和 `expected-value`，`expectedValue` 必须在 `1e-4` 的绝对或相对容差内等于 `distribution` 的加权平均。`pointEstimate` 是独立表示，不要求等于 `expectedValue` 或分布的加权平均。

宿主可以自行决定如何使用可用表示。只提供数值 `distribution` 时，可以用其加权平均得到标量；同时提供 `point-estimate` 时，可以优先使用 `pointEstimate`。

数量分布的值必须是非负整数；打点分布的值必须是非负整数点数。数量和打点的 `expectedValue`、`pointEstimate` 不得小于 `0`，也不要求是实际可能出现的离散值。

### 牌

实体牌使用以下字符串：

```text
1m..9m, 1p..9p, 1s..9s, 5mr, 5pr, 5sr, E, S, W, N, P, F, C
```

`5mr`、`5pr`、`5sr` 表示赤五。`?` 表示在当前输入模式中不可见的暗牌，只能出现在牌局事件中，不能出现在候选动作或输出结果中。

按牌种输出的 `tiles` 使用34种牌，不区分赤五。键名为：

```text
1m..9m, 1p..9p, 1s..9s, E, S, W, N, P, F, C
```

完整的 `tiles` 必须恰好包含这34个键，其中 `5m`、`5p`、`5s` 分别包含同花色的普通五和赤五。枚数输出还可以提供 `redTiles`，其键为 `5mr`、`5pr`、`5sr`；赤五的数量已经包含在 `tiles` 中对应的五里。动作数据中的实体牌仍可保留赤五标记。

### 座位

座位使用绝对编号 `0..3`，不会随当前庄家或界面视角旋转。以某一受控座位为视角的对手预测中，`players` 必须恰好包含另外三个互不重复的座位，并不得包含受控座位。

### 牌局事件

`analysis.run.events` 使用按发生顺序排列的 MJAI 事件对象。每次请求携带当前小局的完整历史，第一项必须是 `start_kyoku`，也可以在它之前包含一项 `start_game`。引擎可以缓存共同前缀，但不得要求宿主只发送增量后缀。

每个事件都有字符串字段 `type`。协议定义以下事件：

| `type` | 必需字段 | 意义 |
| --- | --- | --- |
| `start_game` | 无 | 一场牌局开始。 |
| `start_kyoku` | `bakaze`、`kyoku`、`honba`、`kyotaku`、`oya`、`dora_marker`、`scores`、`tehais` | 小局开始；`scores` 为四家点数，`tehais` 为四个起手牌数组。 |
| `tsumo` | `actor`、`pai` | 对应座位摸牌。 |
| `dahai` | `actor`、`pai`、`tsumogiri` | 对应座位打牌；`tsumogiri` 为布尔值。 |
| `chi` | `actor`、`target`、`pai`、`consumed` | 吃牌；`consumed` 恰好包含手中使用的两张实体牌。 |
| `pon` | `actor`、`target`、`pai`、`consumed` | 碰牌；`consumed` 恰好包含手中使用的两张实体牌。 |
| `daiminkan` | `actor`、`target`、`pai`、`consumed` | 大明杠；`consumed` 恰好包含手中使用的三张实体牌。 |
| `ankan` | `actor`、`consumed` | 暗杠；`consumed` 恰好包含四张实体牌。 |
| `kakan` | `actor`、`pai`、`consumed` | 加杠；`pai` 是追加牌，`consumed` 是原碰的三张实体牌。 |
| `reach` | `actor` | 对应座位宣布立直。 |
| `reach_accepted` | `actor` | 立直成立并支付立直棒。 |
| `dora` | `dora_marker` | 新宝牌指示牌公开。 |
| `hora` | `actor`、`target`、`pai` | 和牌；自摸时 `target` 等于 `actor`。 |
| `ryukyoku` | 无 | 流局。 |
| `end_kyoku` | 无 | 当前小局结束。 |
| `end_game` | 无 | 当前牌局结束。 |

`actor`、`target` 和 `oya` 使用绝对座位。`bakaze`、`dora_marker`、`pai`、`consumed` 和 `tehais` 使用“牌”一节定义的字符串。`kyoku` 为整数 `1..4`，`honba` 和 `kyotaku` 为非负整数，`scores` 恰好包含四个整数。事件可以附带结算、显示或来源字段；接收方必须忽略自己不使用的已知附加字段，但不得忽略未知 `type` 后继续推理。

`standard` 输入中，受控座位起手牌使用实际牌，其他座位起手牌以等量 `?` 占位；其他座位未公开的摸牌也使用 `?`。已经通过打牌、副露、宝牌指示牌或结算公开的牌使用实际牌。 `revealed` 输入把牌谱实际记录的暗牌和摸牌也写为实际牌。

### 候选动作

`action-recommendation` 的候选动作由宿主完成规则校验。每个动作都包含 `type` 和 `actor`，其中 `actor` 必须等于请求的 `controlledSeat`。

| `type` | 其他必需字段 | 意义 |
| --- | --- | --- |
| `dahai` | `pai`、`tsumogiri` | 打出一张实体牌。 |
| `reach` | 无 | 宣布立直。 |
| `chi` | `target`、`pai`、`consumed` | 吃牌。 |
| `pon` | `target`、`pai`、`consumed` | 碰牌。 |
| `daiminkan` | `target`、`pai`、`consumed` | 大明杠。 |
| `ankan` | `consumed` | 暗杠。 |
| `kakan` | `pai`、`consumed` | 加杠。 |
| `hora` | `target`、`pai` | 荣和或自摸；自摸时 `target` 等于 `actor`。 |
| `ryukyoku` | 无 | 宣告允许由玩家主动选择的流局。 |
| `none` | 无 | 放弃当前可选动作。 |

动作中的牌和数组规则与同名牌局事件一致。`none` 可以增加稳定 `variant` 说明放弃的动作；立直后的暗杠选择中，放弃暗杠使用 `variant: "skip-ankan"`，并同时提供强制摸切的 `pai` 和 `tsumogiri: true`。

宿主必须保留所有实体候选，包括同牌的摸切与手切、不同赤五组合等。`candidateId` 只在一次请求内用于关联，引擎不得解释其字符串结构，也不得根据动作内容擅自合并候选。

## 标准输出契约

| 输出契约 ID | 意义 |
| --- | --- |
| `action-recommendation` | 从宿主提供的合法动作候选中推荐一个候选，并可提供各候选的评估指标。 |
| `opponent-shanten` | 预测其他座位的向听分布，以及听牌条件下振听或无役的概率。 |
| `opponent-deal-in-probability` | 预测受控座位向各对手打出34种牌时的铳率。 |
| `opponent-concealed-tile-count` | 预测各对手暗牌中34种牌的数量，可另行预测三种赤五。 |
| `opponent-dora-count` | 提供各对手的宝牌数量预测。 |
| `opponent-score` | 提供各对手的打点预测。 |
| `wall-tile-count` | 预测尚未公开且仍留在牌山中的34种牌数量，可另行预测三种赤五。 |
| `kyoku-outcome` | 提供当前小局的流局、和牌和放铳概率，或互斥的最终结果分布。 |
| `kyoku-score-delta` | 预测四家从当前位置到当前小局结算完成时的点数变化。 |
| `match-placement` | 预测四家在当前对局结束时的顺位。 |
| `match-score` | 预测四家在当前对局结束时的点棒分数。 |

`opponent-dora-count` 和 `opponent-score` 各自规定推荐的统计解释。协议不要求引擎采用该解释，也不为其他解释设置额外声明字段。宿主按照输出的结构、数值范围和初始化时确定的表示解析结果。

## 握手与输出能力

宿主启动进程后首先调用 `engine.hello`：

```json
{
  "jsonrpc": "2.0",
  "id": "host-1",
  "method": "engine.hello",
  "params": {
    "protocol": {
      "name": "riichi-engine-protocol",
      "major": 2,
      "minor": 2
    },
    "host": {
      "id": "example.host",
      "version": "1.0.0"
    }
  }
}
```

`params.protocol` 是宿主支持的最高协议版本。`params.host.id` 是宿主稳定 ID，格式与引擎 ID 相同；`params.host.version` 使用 Semantic Versioning。同一进程中重复调用 `engine.hello` 必须得到相同的身份、能力上限、权重槽位和参数 Schema。

成功结果：

```json
{
  "protocol": {
    "name": "riichi-engine-protocol",
    "major": 2,
    "minor": 2
  },
  "engine": {
    "id": "example.opponent-engine",
    "name": "Example Opponent Engine",
    "version": "1.0.0"
  },
  "outputContracts": [
    {
      "id": "opponent-shanten",
      "version": 1
    },
    {
      "id": "opponent-deal-in-probability",
      "version": 1
    }
  ],
  "weightSlots": [],
  "devices": [
    {
      "type": "cpu",
      "title": {"default": "CPU"}
    }
  ],
  "runtimeCapabilities": {
    "multipleSessions": true,
    "concurrentRequests": false,
    "cancellation": true
  },
  "optionsSchema": {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {},
    "additionalProperties": false
  }
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `protocol` | 是 | 协商后的协议版本。 |
| `engine.id` | 是 | 必须与 `engine.json.id` 完全一致。 |
| `engine.name` | 是 | 面向用户的引擎名称。 |
| `engine.version` | 是 | 必须与 `engine.json.version` 完全一致。 |
| `outputContracts` | 是 | 引擎可能提供的非空输出声明数组，不得重复。 |
| `weightSlots` | 是 | 权重槽位数组；不需要权重时使用空数组。 |
| `devices` | 是 | 非空设备数组，列出可以传给初始化请求的设备类型。 |
| `devices[].type` | 是 | 稳定设备 ID，使用小写 ASCII 字母、数字和连字符。 |
| `devices[].title` | 是 | 多语言设备名称。 |
| `runtimeCapabilities` | 是 | 进程运行能力。 |
| `optionsSchema` | 是 | JSON Schema Draft 2020-12 对象 Schema；没有参数时使用示例中的空对象 Schema。 |

每个输出声明包含：

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 输出契约 ID。 |
| `version` | 是 | 输出契约主版本。 |
| `representations` | 条件必需 | 数值预测可以使用的表示，允许值为 `distribution`、`expected-value`、`point-estimate`。 |
| `supportsRevealedHands` | 否 | 是否接受明牌输入，默认 `false`。 |
| `metrics` | 条件必需 | `action-recommendation` 可以提供的评估指标；没有指标时使用空数组。 |

`representations` 只用于允许数值预测表示的输出，必须是无重复项的非空数组。其他输出不得提供该字段。`metrics` 只用于 `action-recommendation`。

`engine.hello` 返回引擎程序的能力上限。初始化结果必须根据当前权重和有效参数返回实际能力，不得增加握手中没有声明的输出、表示、评估指标或明牌支持。

`runtimeCapabilities` 的三个字段都是必需布尔值：

| 字段 | 意义 |
| --- | --- |
| `multipleSessions` | 是否可以在一个初始化实例中隔离多个 `sessionId`。为 `false` 时宿主一次只使用一个会话。 |
| `concurrentRequests` | 是否允许多个分析请求同时执行。为 `false` 时宿主串行发送。 |
| `cancellation` | 是否处理 `request.cancel` 通知。 |

宿主不得从输出契约推断运行能力。宿主不认识 `optionsSchema` 中的界面扩展时仍可保存原始参数，但不得绕过标准 JSON Schema 校验。

## 正常视角与明牌输入

分析请求使用两种输入模式：

| `inputMode` | 传递内容 |
| --- | --- |
| `standard` | 受控座位正常能够获知的信息，包括自己的暗牌；其他座位的暗牌保持未知。 |
| `revealed` | 牌谱中实际记录的完整手牌信息。只有牌谱确有这些信息时才能使用。 |

所有输出都必须接受 `standard`。`supportsRevealedHands: true` 表示该输出也接受 `revealed`。

界面未开启明牌时，宿主始终使用 `standard`。界面开启明牌时，只有同时满足以下条件的输出使用 `revealed`：

- 初始化结果声明该输出支持明牌；
- 当前牌谱具有完整的明牌信息。

不满足任一条件时，宿主仍向该输出传递 `standard` 数据。同一引擎的不同输出可以具有不同的明牌支持。需要不同输入模式的输出不得合并到同一次 `analysis.run` 请求中。

## 权重槽位

引擎在 `engine.hello` 中通过 `weightSlots` 声明需要用户配置的权重文件。一个引擎可以声明多个槽位，也可以不需要权重。每个槽位接收一个文件；需要多个文件时声明多个槽位。

```json
{
  "weightSlots": [
    {
      "id": "backbone",
      "title": {
        "default": "Backbone weights",
        "zh-CN": "主模型权重"
      },
      "description": {
        "default": "Shared feature extractor used by the selected outputs.",
        "zh-CN": "所选输出共用的特征提取权重。"
      },
      "formats": [
        {
          "id": "example-backbone-onnx",
          "extensions": [".onnx"]
        }
      ],
      "requiredForOutputs": [
        {"id": "action-recommendation", "version": 1},
        {"id": "opponent-dora-count", "version": 1}
      ]
    }
  ]
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 引擎内部稳定槽位 ID。使用小写 ASCII 字母、数字和连字符，长度为 `1..64`。 |
| `title` | 是 | 多语言槽位标题。 |
| `description` | 否 | 多语言槽位说明。 |
| `formats` | 是 | 非空数组，列出槽位接受的权重格式。 |
| `formats[].id` | 是 | 引擎定义的稳定格式 ID。 |
| `formats[].extensions` | 是 | 非空扩展名数组，例如 `.onnx`、`.pth`。只用于文件选择提示。 |
| `requiredForOutputs` | 是 | 非空输出引用数组。启用其中任一输出时必须提供该槽位。 |

一个输出可以要求多个槽位，一个槽位也可以被多个输出共用。宿主根据当前交给该引擎配置的输出决定哪些槽位需要选择文件；不需要的槽位可以淡化显示。扩展名不能替代引擎对文件内容和结构的校验。

## 初始化

`engine.initialize` 加载当前配置。进程启动后不得自行选择默认权重；初始化成功前不得接受 `analysis.run`。再次初始化会先结束当前任务、清除全部会话，然后以新配置替换旧配置。

### 初始化请求

```json
{
  "enabledOutputs": [
    {"id": "action-recommendation", "version": 1},
    {"id": "opponent-dora-count", "version": 1}
  ],
  "weights": [
    {
      "slotId": "backbone",
      "format": "example-backbone-onnx",
      "path": "C:\\Models\\Example\\backbone.onnx"
    }
  ],
  "device": {
    "type": "cpu"
  },
  "options": {}
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `enabledOutputs` | 是 | 本次加载需要提供的非空输出引用数组，不得重复。 |
| `weights` | 是 | 当前启用输出要求的权重槽位。没有必需槽位时使用空数组。 |
| `weights[].slotId` | 是 | `engine.hello.weightSlots[].id` 中当前必需的槽位。 |
| `weights[].format` | 是 | 当前槽位声明的格式 ID。 |
| `weights[].path` | 是 | 宿主解析后的本机绝对路径。 |
| `device` | 是 | 设备选择；`device.type` 必须来自 `engine.hello.devices`。 |
| `options` | 是 | 按引擎声明的选项结构校验的参数对象。 |

请求必须为每个当前必需的槽位提供一个文件，且不得包含未知、重复或当前不需要的槽位。引擎必须验证文件格式和内容，不能只依赖扩展名。

文件摘要由宿主在需要识别结果来源时计算，不通过初始化请求要求引擎代为校验或回显。

### 初始化结果

```json
{
  "outputs": [
    {
      "id": "action-recommendation",
      "version": 1,
      "metrics": [
        {
          "id": "q-value",
          "title": {"default": "Q value"},
          "format": "number",
          "fractionDigits": 3,
          "preferredDirection": "higher"
        },
        {
          "id": "policy",
          "title": {"default": "Policy"},
          "format": "percentage",
          "fractionDigits": 2,
          "preferredDirection": "higher"
        },
        {
          "id": "expected-placement",
          "title": {"default": "Expected placement"},
          "format": "number",
          "preferredDirection": "lower"
        }
      ],
      "primaryMetricId": "q-value",
      "recommendationMetricId": "policy"
    },
    {
      "id": "opponent-dora-count",
      "version": 1,
      "representations": ["distribution", "point-estimate"],
      "supportsRevealedHands": true
    }
  ],
  "device": {
    "type": "cpu"
  },
  "effectiveOptions": {}
}
```

`outputs` 必须为请求中的每个输出提供且只提供一个同 ID、同版本的结果，数组顺序不具有协议意义。初始化结果可以把握手中声明的表示、评估指标或明牌能力收窄，但不得增加能力。无法提供任一请求输出时，初始化整体失败，不得静默删除输出。

对于数值预测，初始化结果中的 `representations` 是当前配置之后每次返回结果时必须使用的固定表示。对于动作推荐，`metrics`、`primaryMetricId` 和 `recommendationMetricId` 的规则见“评估指标声明”。宿主根据这些固定声明安排界面；单次结果缺少数据时不得改变界面结构。

`device` 是引擎实际采用的设备，必须来自握手声明。`effectiveOptions` 必须通过握手中的 `optionsSchema`，并包含应用默认值后的最终参数。修改已启用输出、权重文件、设备或参数后必须重新初始化。

## 统一分析请求

引擎使用 `analysis.run` 接收业务请求：

```json
{
  "jsonrpc": "2.0",
  "id": "host-41",
  "method": "analysis.run",
  "params": {
    "sessionId": "game-17:seat-0:standard",
    "controlledSeat": 0,
    "inputMode": "standard",
    "events": [
      {
        "type": "start_kyoku",
        "bakaze": "E",
        "kyoku": 1,
        "honba": 0,
        "kyotaku": 0,
        "oya": 0,
        "dora_marker": "3p",
        "scores": [25000, 25000, 25000, 25000],
        "tehais": [
          ["1m", "2m", "3m", "4p", "5p", "6p", "7s", "8s", "9s", "E", "E", "P", "P"],
          ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"],
          ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"],
          ["?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?", "?"]
        ]
      }
    ],
    "outputs": [
      {
        "id": "action-recommendation",
        "version": 1,
        "parameters": {
          "candidates": [
            {
              "candidateId": "candidate:0",
              "action": {
                "type": "dahai",
                "actor": 0,
                "pai": "1m",
                "tsumogiri": false
              }
            }
          ]
        }
      },
      {
        "id": "opponent-dora-count",
        "version": 1,
        "parameters": {}
      }
    ]
  }
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `sessionId` | 是 | 增量状态隔离键。不同牌局、受控座位或输入模式不得共用。 |
| `controlledSeat` | 是 | 受控绝对座位，整数 `0..3`。 |
| `inputMode` | 是 | `standard` 或经过能力协商的 `revealed`。 |
| `events` | 是 | 到当前位置为止、符合输入模式的规范事件数组。 |
| `outputs` | 是 | 本次请求的非空输出数组，不得重复。 |
| `outputs[].id` | 是 | 已初始化的输出契约 ID。 |
| `outputs[].version` | 是 | 已初始化的输出契约主版本。 |
| `outputs[].parameters` | 是 | 输出契约定义的请求参数，没有专用参数时使用 `{}`。 |

同一请求中的所有输出使用相同的历史、受控座位和输入模式。只有交给同一个已初始化引擎配置的输出才能合并。引擎必须返回请求中的全部输出且不得增加额外输出；任一输出失败时，整个 JSON-RPC 请求返回错误，不返回部分结果。

同一 `sessionId` 的后续请求可以扩展、回退或改写历史。引擎可以在内部复用不变的共同前缀，但必须以本次完整 `events` 为准，在回退或分支后丢弃不再匹配的状态。是否以及如何复用历史属于引擎实现，不需要向宿主声明。宿主使用请求 ID 和自己的运行代次判断结果是否仍适用于当前位置，过时结果不得覆盖当前数据。

分析结果：

```json
{
  "outputs": [
    {
      "id": "action-recommendation",
      "version": 1,
      "data": {}
    },
    {
      "id": "opponent-dora-count",
      "version": 1,
      "data": {}
    }
  ],
  "timing": {
    "totalMs": 70.3
  }
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `outputs` | 是 | 与请求的输出引用恰好一一对应；数组顺序不具有协议意义。 |
| `outputs[].data` | 是 | 对应输出契约定义的结果对象。 |
| `timing` | 否 | 本次请求的耗时；`totalMs` 为非负有限数值，单位为毫秒。 |

请求和结果由 JSON-RPC 的 `id` 关联。结果不重复回显会话、历史、输入模式或来源指纹。

## `opponent-shanten`

```json
{
  "players": [
    {
      "seat": 1,
      "shanten": [
        {"value": 0, "probability": 0.12},
        {"value": 1, "probability": 0.28},
        {"value": 2, "probability": 0.31},
        {"value": 3, "probability": 0.16},
        {"value": 4, "probability": 0.08},
        {"value": 5, "probability": 0.04},
        {"value": 6, "probability": 0.01}
      ],
      "furitenOrNoYaku": 0.03
    }
  ]
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `players` | 是 | “座位”一节定义的其他座位。 |
| `players[].seat` | 是 | 对应玩家的绝对座位。 |
| `players[].shanten` | 是 | 取值为整数 `0..6` 的概率分布；未列出的取值概率为 `0`，`0` 表示听牌。 |
| `players[].furitenOrNoYaku` | 是 | `P(振听或无役 \| 0向听)`。 |

`furitenOrNoYaku` 固定属于 `opponent-shanten`，不是独立输出契约。宿主需要拆分听牌显示时可以计算：

```text
可荣和听牌 = P(0向听) × (1 - furitenOrNoYaku)
振听或无役 = P(0向听) × furitenOrNoYaku
```

## `opponent-deal-in-probability`

```json
{
  "players": [
    {
      "seat": 1,
      "tiles": {
        "1m": 0.0,
        "2m": 0.0012,
        "3m": 0.04
      }
    }
  ]
}
```

`players` 使用“座位”一节定义的其他座位。每个 `tiles` 必须恰好包含34种牌，值表示受控座位打出该牌时被对应玩家荣和的概率。示例中的牌种为节选，实际结果不得省略。

## `opponent-concealed-tile-count`

```json
{
  "players": [
    {
      "seat": 1,
      "tiles": {
        "1m": {
          "distribution": [
            {"value": 0, "probability": 0.55},
            {"value": 1, "probability": 0.35},
            {"value": 2, "probability": 0.09},
            {"value": 3, "probability": 0.01},
            {"value": 4, "probability": 0.0}
          ],
          "expectedValue": 0.56
        }
      },
      "redTiles": {
        "5mr": {
          "distribution": [
            {"value": 0, "probability": 0.7},
            {"value": 1, "probability": 0.3}
          ],
          "expectedValue": 0.3
        }
      }
    }
  ]
}
```

`players` 使用“座位”一节定义的其他座位。每个 `tiles` 必须恰好包含34种牌。离散分布存在时，取值必须是整数 `0..4`；未列出的取值概率为 `0`。`expectedValue` 或 `pointEstimate` 存在时，必须位于 `[0, 4]`。宿主可以从分布派生“至少持有一张”的概率 `1 - P(0)`。

`redTiles` 可以省略；提供时必须恰好包含 `5mr`、`5pr`、`5sr`。离散分布的取值必须是整数 `0..1`，`expectedValue` 或 `pointEstimate` 必须位于 `[0, 1]`。

## `wall-tile-count`

```json
{
  "tiles": {
    "1m": {
      "distribution": [
        {"value": 0, "probability": 0.10},
        {"value": 1, "probability": 0.35},
        {"value": 2, "probability": 0.40},
        {"value": 3, "probability": 0.12},
        {"value": 4, "probability": 0.03}
      ],
      "expectedValue": 1.63
    }
  },
  "redTiles": {
    "5mr": {
      "distribution": [
        {"value": 0, "probability": 0.4},
        {"value": 1, "probability": 0.6}
      ],
      "expectedValue": 0.6
    }
  }
}
```

输出表示当前事件完成后，尚未公开且仍留在牌山中的各种牌的数量。它只表示整个未公开牌山 `all-unrevealed-wall`，不区分活牌区域和王牌区域，也不提供区域字段。

`tiles` 必须恰好包含34种牌。离散分布存在时，取值必须是整数 `0..4`；未列出的取值概率为 `0`。`expectedValue` 或 `pointEstimate` 存在时，必须位于 `[0, 4]`。

`redTiles` 可以省略；提供时必须恰好包含 `5mr`、`5pr`、`5sr`。离散分布的取值必须是整数 `0..1`，`expectedValue` 或 `pointEstimate` 必须位于 `[0, 1]`。

## `opponent-dora-count`

```json
{
  "players": [
    {
      "seat": 1,
      "prediction": {
        "distribution": [
          {"value": 0, "probability": 0.20},
          {"value": 1, "probability": 0.40},
          {"value": 2, "probability": 0.25},
          {"value": 3, "probability": 0.10},
          {"value": "4+", "probability": 0.05}
        ],
        "pointEstimate": 1.4
      }
    }
  ]
}
```

推荐的统计解释是：条件于对应玩家最终在当前牌局中和牌，预测其和牌结算时实际击中的宝牌总数，不区分荣和与自摸。计数包括规则认定的普通宝牌和赤牌；玩家立直和牌时，也包括结算时翻开的里宝牌。尚未确定的宝牌指示牌作为预测的一部分。

按照这一解释，输出不表示玩家当前已经确定持有的宝牌数量，也不乘以最终和牌概率。

协议只要求 `players` 符合“座位”一节，离散值为非负整数或形如 `N+` 的字符串，`expectedValue` 和 `pointEstimate` 不得小于 `0`；不要求引擎采用上述统计解释。`N` 使用不含多余前导零的十进制非负整数，`N+` 表示数量不小于 `N`。同一分布最多使用一个 `N+`，并且不得再列出不小于 `N` 的数值。引擎可以用该输出表示其他宝牌数量预测，宿主仍按相同数据结构解析。

## `opponent-score`

```json
{
  "players": [
    {
      "seat": 1,
      "prediction": {
        "distribution": [
          {"value": 1000, "probability": 0.10},
          {"value": 2000, "probability": 0.25},
          {"value": 3900, "probability": 0.45},
          {"value": 8000, "probability": 0.20}
        ],
        "expectedValue": 3955
      }
    }
  ]
}
```

推荐的统计解释是：条件于对应玩家最终在当前牌局中和牌，预测其和牌结算时由该手牌产生的打点，不区分荣和与自摸。数值不包括本场加分、立直棒、供托或其他场供。

按照这一解释，荣和时的打点为放铳者就该手牌支付的点数；自摸时为另外三名玩家就该手牌支付的点数总和。离散分布使用实际点数档位；`expectedValue` 和 `pointEstimate` 可以位于离散档位之间。输出不乘以最终和牌概率。

协议只要求 `players` 符合“座位”一节，离散值为非负整数点数，`expectedValue` 和 `pointEstimate` 不得小于 `0`；不要求引擎采用上述统计解释。引擎可以用该输出表示其他打点预测，宿主仍按相同数据结构解析。

## `kyoku-outcome` v2

```json
{
  "drawProbability": 0.25,
  "players": [
    {"seat": 0, "winProbability": 0.15, "dealInProbability": 0.50},
    {"seat": 1, "winProbability": 0.20, "dealInProbability": 0.10},
    {"seat": 2, "winProbability": 0.40, "dealInProbability": 0.00},
    {"seat": 3, "winProbability": 0.30, "dealInProbability": 0.00}
  ],
  "outcomes": [
    {"type": "draw", "probability": 0.25},
    {"type": "tsumo", "winner": 0, "probability": 0.15},
    {"type": "ron", "winners": [1], "target": 0, "probability": 0.20},
    {"type": "ron", "winners": [2], "target": 1, "probability": 0.10},
    {"type": "ron", "winners": [2, 3], "target": 0, "probability": 0.30}
  ]
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `drawProbability` | 条件必需 | 直接预测 `P(当前小局流局)`；包括荒牌流局和中途流局。与 `players` 同时提供。 |
| `players` | 条件必需 | 直接预测四家的和牌和放铳概率；恰好包含绝对座位 `0..3` 各一次。与 `drawProbability` 同时提供。 |
| `players[].seat` | 是 | 对应玩家的绝对座位。 |
| `players[].winProbability` | 是 | `P(该玩家在当前小局中和牌)`。 |
| `players[].dealInProbability` | 是 | `P(该玩家在当前小局中放铳)`。 |
| `outcomes` | 条件必需 | 当前小局互斥最终结果的概率分布。 |
| `outcomes[].type` | 是 | `draw`、`tsumo` 或 `ron`。 |
| `outcomes[].probability` | 是 | 对应最终结果的概率。 |
| `outcomes[].winner` | `type = "tsumo"` 时必需 | 自摸玩家的绝对座位。 |
| `outcomes[].winners` | `type = "ron"` 时必需 | 荣和玩家的非空绝对座位数组，不得重复或包含 `target`。多个玩家表示双响或三响。 |
| `outcomes[].target` | `type = "ron"` 时必需 | 放铳玩家的绝对座位。 |

`drawProbability` 与 `players` 组成直接摘要。直接摘要和 `outcomes` 至少提供一种，也可以同时提供。两种表示是独立预测，协议不要求数值一致。

`outcomes` 不得重复同一种最终结果。流局、自摸及不同和牌者组合的荣和均为不同结果；其余座位字段不得出现。

## `kyoku-score-delta`

```json
{
  "players": [
    {
      "seat": 0,
      "prediction": {
        "expectedValue": 4760
      }
    }
  ]
}
```

`players` 必须恰好包含绝对座位 `0..3` 各一次。`prediction` 使用“数值预测”容器，表示从最后一个输入事件后的当前分数，到本局结算后分数的变化。输入历史中已经发生的分数变化不再重复计算。

离散分布的值必须是整数点数，可以为负数。

## `match-placement`

```json
{
  "players": [
    {
      "seat": 0,
      "prediction": {
        "distribution": [
          {"value": 1, "probability": 0.36},
          {"value": 2, "probability": 0.31},
          {"value": 3, "probability": 0.21},
          {"value": 4, "probability": 0.12}
        ],
        "expectedValue": 2.09
      }
    }
  ]
}
```

`players` 必须恰好包含绝对座位 `0..3` 各一次。`prediction` 使用“数值预测”容器，表示当前对局结束时的顺位。

离散分布的值必须是整数 `1..4`，`expectedValue` 和 `pointEstimate` 必须位于 `[1, 4]`。

## `match-score`

```json
{
  "players": [
    {
      "seat": 0,
      "prediction": {
        "expectedValue": 29750
      }
    }
  ]
}
```

`players` 必须恰好包含绝对座位 `0..3` 各一次。`prediction` 使用“数值预测”容器，表示当前对局结束时的分数。

离散分布的值必须是整数点数，可以为负数。

## `action-recommendation`

### 请求参数

```json
{
  "candidates": [
    {
      "candidateId": "candidate:0",
      "action": {}
    }
  ]
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `candidates` | 是 | 宿主已经完成规则校验的非空合法动作候选数组。 |
| `candidates[].candidateId` | 是 | 本次请求内唯一的不透明关联 ID。 |
| `candidates[].action` | 是 | 规范动作对象。 |

### 评估指标声明

动作推荐可以声明任意数量的评估指标。指标由 `engine.hello` 列出能力上限，并由初始化结果确定当前配置使用的固定集合和顺序。

```json
{
  "id": "expected-placement",
  "title": {
    "default": "Expected placement",
    "zh-CN": "期望顺位"
  },
  "description": {
    "default": "Expected final placement after choosing this action."
  },
  "format": "number",
  "fractionDigits": 2,
  "preferredDirection": "lower"
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 引擎定义的稳定指标 ID。使用小写 ASCII 字母、数字和连字符，长度为 `1..64`。 |
| `title` | 是 | 多语言短标题。 |
| `description` | 否 | 多语言说明。 |
| `format` | 是 | `number`、`percentage` 或 `points`，用于宿主格式化数值。 |
| `fractionDigits` | 否 | `0..12` 的整数，指定显示时保留的小数位数。`percentage` 在换算为百分数后应用该精度。 |
| `preferredDirection` | 是 | `higher`、`lower` 或 `none`，表示数值的偏好方向。 |

`format` 只规定显示格式，不规定指标的统计意义。指标的意义由稳定 ID、标题和说明共同给出。相同引擎主版本内，相同指标 ID 的格式、方向和意义不得改变。 `fractionDigits` 只影响显示，不改变引擎返回的数值。未提供时，宿主使用常规数值格式，并且不得根据指标 ID 猜测小数位数。

初始化结果可以提供 `primaryMetricId`，其值必须是当前 `metrics` 中的一个 ID。宿主可以用主要指标排序评估明细。没有主要指标时，宿主不得根据指标 ID 猜测用于排序的指标。

初始化结果可以提供 `recommendationMetricId`，其值必须指向当前 `metrics` 中 `format` 为 `percentage`、`preferredDirection` 为 `higher` 的指标。该指标的 `[0, 1]` 数值直接表示各合法动作的相对推荐强度，宿主可以据此绘制推荐条。引擎负责把 Q 值、期望得点或其他内部评估换算为推荐强度；宿主不得根据指标 ID 猜测推荐强度，也不得自行把未声明的指标归一化为推荐条。没有 `recommendationMetricId` 时，宿主只标示 `bestCandidateId`，不根据评估指标绘制推荐条。

`bestCandidateId` 始终是引擎最终选择的推荐动作。`primaryMetricId` 和 `recommendationMetricId` 只控制评估明细与推荐强度的显示，不得用于推翻该选择。

### 结果

```json
{
  "bestCandidateId": "candidate:0",
  "candidates": [
    {
      "candidateId": "candidate:0",
      "metrics": {
        "q-value": 0.284,
        "policy": 0.423,
        "expected-placement": 2.18
      }
    },
    {
      "candidateId": "candidate:1",
      "metrics": {
        "q-value": 0.251,
        "policy": null,
        "expected-placement": 2.24
      }
    }
  ]
}
```

`bestCandidateId` 必须是请求候选之一。即使引擎不提供任何评估指标，也必须提供 `bestCandidateId`。

当前配置的 `metrics` 为空时，结果不得提供 `candidates`。`metrics` 非空时，结果必须提供 `candidates`，并恰好覆盖请求中的全部候选。每个候选的 `metrics` 必须恰好包含初始化时声明的全部指标 ID；值为符合指标格式的有限数值，暂时没有该候选的指标值时使用 `null`。单个值为 `null` 不改变宿主已经确定的指标列和界面布局。

`percentage` 指标的非空值必须位于 `[0, 1]`。协议不要求不同候选的 `percentage` 数值之和为 `1`，也不根据 `preferredDirection` 验证 `bestCandidateId`。推荐动作由引擎直接决定。

## 会话、状态与关闭

引擎使用以下状态：

| 状态 | 意义 |
| --- | --- |
| `starting` | 进程已启动，尚未完成握手。 |
| `uninitialized` | 握手完成，尚未初始化。 |
| `loading` | 正在加载或替换配置。 |
| `ready` | 可以接受分析请求。 |
| `busy` | 正在执行分析；不支持并发时不得再接受新的分析请求。 |
| `error` | 当前配置不可用。重新初始化可以恢复。 |
| `stopping` | 正在关闭。 |

状态变化时，引擎发送 `engine.status` 通知：

```json
{
  "jsonrpc": "2.0",
  "method": "engine.status",
  "params": {
    "state": "loading",
    "message": "Loading model weights",
    "error": null
  }
}
```

`state` 必需；`message` 和 `error` 可选。`message` 只用于显示，不得承载宿主必须解析的数据。

`engine.getStatus` 用于恢复同步和诊断，成功结果为：

```json
{
  "state": "ready",
  "activeTasks": 0,
  "queuedTasks": 0,
  "lastError": null
}
```

`activeTasks` 和 `queuedTasks` 是非负整数。宿主不得依赖高频轮询；正常变化由通知推送。

引擎开始或结束分析请求时可以发送 `task.status`：

```json
{
  "jsonrpc": "2.0",
  "method": "task.status",
  "params": {
    "requestId": "host-41",
    "state": "running",
    "outputs": [
      {"id": "action-recommendation", "version": 1}
    ]
  }
}
```

任务状态允许值为 `queued`、`running`、`completed`、`canceled`、`error`。通知不替代原请求的 JSON-RPC 响应。

`session.reset` 和 `session.close` 都接收：

```json
{
  "sessionId": "game-17:seat-0:standard"
}
```

两者成功结果均为 `{"ok": true}`。`session.reset` 清除指定会话的增量状态，但允许之后继续使用相同 ID；`session.close` 释放该会话。未知会话也视为成功，不得影响其他会话。

支持取消的引擎接收 `request.cancel` 通知：

```json
{
  "jsonrpc": "2.0",
  "method": "request.cancel",
  "params": {
    "requestId": "host-41"
  }
}
```

排队中的请求应当立即取消；运行中的请求可以在安全点取消。成功取消后，原请求返回 `REQUEST_CANCELED` 错误。不支持取消或无法及时中断时，引擎可以完成原请求，宿主负责丢弃已经过时的结果。

`engine.shutdown` 接收空对象 `{}`，先返回 `{"ok": true}`，随后发送 `stopping` 状态并正常退出。宿主在超时、通信损坏或进程无响应时可以直接终止进程。

## 错误

协议错误使用 JSON-RPC 错误响应：

```json
{
  "jsonrpc": "2.0",
  "id": "host-41",
  "error": {
    "code": -32000,
    "message": "The requested output is not enabled.",
    "data": {
      "errorCode": "UNSUPPORTED_OUTPUT",
      "recoverable": false
    }
  }
}
```

`message` 是简短纯文本。`data.errorCode` 是宿主可以判断的稳定 ASCII 字符串； `data.recoverable` 表示不重启进程是否可能通过新请求恢复。附加诊断数据只能放在 `data` 中。

使用 JSON-RPC 标准数值错误码 `-32700`、`-32600`、`-32601`、`-32602` 和 `-32603` 表示解析错误、无效请求、未知方法、无效参数和内部错误。引擎业务错误使用 `-32000`，并使用以下 `errorCode`：

| `errorCode` | 意义 |
| --- | --- |
| `PROTOCOL_MISMATCH` | 协议名称或主版本不兼容。 |
| `ENGINE_NOT_INITIALIZED` | 尚未成功初始化。 |
| `INITIALIZATION_FAILED` | 初始化未能完成。 |
| `INVALID_WEIGHT` | 权重缺失、格式错误或内容不兼容。 |
| `UNSUPPORTED_OUTPUT` | 输出未知、未启用或不支持当前输入模式。 |
| `INVALID_HISTORY` | 牌局事件缺失、顺序错误或内容非法。 |
| `INVALID_CANDIDATES` | 动作候选为空、重复或非法。 |
| `INVALID_MODEL_OUTPUT` | 模型产生缺失、非有限或不符合输出契约的数据。 |
| `REQUEST_CANCELED` | 请求已取消。 |
| `ENGINE_BUSY` | 当前运行能力不允许接受新任务。 |

分析请求中的任一输出失败时，整个请求返回一个错误，不得把部分业务结果放入错误响应。

## 安全边界

协议兼容不代表引擎可信。宿主必须把引擎程序、清单、文本、路径和所有进程输出视为不可信输入，限制消息大小和等待时间，校验程序包路径，且不得通过 Shell 执行清单内容。宿主应当在独立进程中运行引擎，并能够在通信损坏、超时或退出异常时终止它。

## 宿主生成的结果来源标识

协议不要求引擎生成或返回来源指纹。需要缓存、比较或展示结果来源时，宿主根据自己实际启动和传入的内容生成稳定标识。标识必须覆盖所有可能改变结果的数据，至少包括：

- 会影响执行的引擎程序包文件或可执行文件摘要；
- 当前使用的全部权重文件摘要；
- 实际设备类型、有效参数以及会影响数值精度的运行配置；
- 输出契约 ID 和版本；
- 初始化结果确定的表示、指标 ID、指标格式和偏好方向；
- 会改变结果数值的宿主后处理版本。

宿主为每个输出分别生成来源标识。同一引擎配置提供多个输出时，共享的程序、权重和参数部分可以复用。本机文件路径、多语言标题和说明不得进入稳定标识。进程重启次数、请求序号等临时状态使用单独的运行代次管理，不属于稳定来源标识。协议不规定宿主内部标识的字段名、保存位置或摘要算法。

</div>
