# 引擎输出与分析请求

引擎通过输出契约声明自己能够提供的数据。一个引擎可以同时提供多个输出，宿主也可以把
不同输出交给不同的引擎配置。引擎的模型结构、训练方法和内部数据结构不属于协议。

引擎进程使用 JSON-RPC 2.0 和 JSONL 与宿主通信。本文定义输出声明、权重要求、初始化、分析
请求和标准输出数据。本文中的牌局数据仅适用于四人立直麻将。

## 1. 通用数据类型

### 1.1 输出引用

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

改变字段含义、概率条件、目标定义或删除既有字段时，必须提高 `version`。增加接收方可以
忽略的可选字段不要求提高主版本。

### 1.2 多语言文本

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

宿主依次尝试完整语言标签、主语言标签和 `default`。所有文本按纯文本显示，不解释 HTML、
Markdown 或终端控制字符。

### 1.3 概率与离散分布

概率必须是位于闭区间 `[0, 1]` 的有限 JSON 数值，不得为 `NaN` 或无穷大。概率分布的
概率和在 `1e-4` 容差内必须为 `1`。

离散分布使用以下结构：

```json
[
  {"value": 1000, "probability": 0.10},
  {"value": 2000, "probability": 0.25},
  {"value": 3900, "probability": 0.45},
  {"value": 8000, "probability": 0.20}
]
```

`value` 不得重复，并必须从小到大排列。每项的 `probability` 表示对应取值的概率。

### 1.4 数值预测

牌张数量、宝牌数量和打点使用同一种数值预测容器：

```json
{
  "distribution": [
    {"value": 1000, "probability": 0.10},
    {"value": 2000, "probability": 0.25},
    {"value": 3900, "probability": 0.45},
    {"value": 8000, "probability": 0.20}
  ],
  "expectedValue": 3955
}
```

数值预测允许两种表示：

| 表示 | 对应字段 | 格式与意义 |
| --- | --- | --- |
| `distribution` | `distribution` | 离散概率分布。 |
| `expected-value` | `expectedValue` | 预测值的数学期望，必须是有限 JSON 数值。 |

当前引擎配置在初始化时确定每项输出使用哪些表示。声明的字段必须出现在之后的每个对应
结果中，未声明的字段不得出现。若同时声明两种表示，`expectedValue` 必须在 `1e-4` 的
绝对或相对容差内等于 `distribution` 的加权平均。

数量分布的值必须是非负整数；打点分布的值必须是非负整数点数。数量和打点的
`expectedValue` 不得小于 `0`，也不要求是实际可能出现的离散值。

### 1.5 牌种

按牌种输出的预测使用34种牌，不区分赤五。键名为：

```text
1m..9m, 1p..9p, 1s..9s, E, S, W, N, P, F, C
```

完整结果必须恰好包含这34个键。动作数据中的实体牌仍可保留赤五标记。

### 1.6 其他座位

座位使用绝对编号 `0..3`。以某一受控座位为视角的对手预测中，`players` 必须恰好包含
另外三个互不重复的座位，并不得包含受控座位。

## 2. 标准输出契约

| 输出契约 ID | 意义 |
| --- | --- |
| `action-recommendation` | 从宿主提供的合法动作候选中推荐一个候选，并可提供各候选的评估指标。 |
| `opponent-shanten` | 预测其他座位的向听分布，以及听牌条件下振听或无役的概率。 |
| `opponent-deal-in-probability` | 预测受控座位向各对手打出34种牌时的铳率。 |
| `opponent-concealed-tile-count` | 预测各对手暗牌中34种牌的数量。 |
| `opponent-dora-count` | 提供各对手的宝牌数量预测。 |
| `opponent-score` | 提供各对手的打点预测。 |
| `wall-tile-count` | 预测尚未公开且仍留在牌山中的34种牌的数量。 |

`opponent-dora-count` 和 `opponent-score` 分别在第12节和第13节规定推荐的统计解释。协议
不要求引擎采用该解释，也不为其他解释设置额外声明字段。宿主按照输出的结构、数值范围和
初始化时确定的表示解析结果。

## 3. 输出能力声明

引擎在 `engine.hello` 中通过 `outputContracts` 返回自己可能提供的输出：

```json
{
  "outputContracts": [
    {
      "id": "action-recommendation",
      "version": 1,
      "metrics": [
        {
          "id": "q-value",
          "title": {"default": "Q value"},
          "format": "number",
          "preferredDirection": "higher"
        },
        {
          "id": "policy",
          "title": {"default": "Policy"},
          "format": "percentage",
          "preferredDirection": "higher"
        },
        {
          "id": "expected-placement",
          "title": {"default": "Expected placement"},
          "format": "number",
          "preferredDirection": "lower"
        }
      ]
    },
    {
      "id": "opponent-dora-count",
      "version": 1,
      "representations": ["distribution", "expected-value"],
      "supportsRevealedHands": true
    }
  ]
}
```

每个输出声明包含：

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 输出契约 ID。 |
| `version` | 是 | 输出契约主版本。 |
| `representations` | 条件必需 | 数值预测可以使用的表示，允许值为 `distribution`、`expected-value`。 |
| `supportsRevealedHands` | 否 | 是否接受明牌输入，默认 `false`。 |
| `metrics` | 条件必需 | `action-recommendation` 可以提供的评估指标；没有指标时使用空数组。 |

`representations` 只用于允许数值预测表示的输出，必须是无重复项的非空数组。其他输出不得
提供该字段。`metrics` 只用于 `action-recommendation`。

`engine.hello` 返回引擎程序的能力上限。初始化结果必须根据当前权重和有效参数返回实际
能力，不得增加握手中没有声明的输出、表示、评估指标或明牌支持。

进程运行方式通过独立的 `runtimeCapabilities` 声明，例如多会话、增量历史、并发、取消和
重载。宿主不得从输出契约推断这些运行能力。

## 4. 正常视角与明牌输入

分析请求使用两种输入模式：

| `inputMode` | 传递内容 |
| --- | --- |
| `standard` | 受控座位正常能够获知的信息，包括自己的暗牌；其他座位的暗牌保持未知。 |
| `revealed` | 牌谱中实际记录的完整手牌信息。只有牌谱确有这些信息时才能使用。 |

所有输出都必须接受 `standard`。`supportsRevealedHands: true` 表示该输出也接受 `revealed`。

界面未开启明牌时，宿主始终使用 `standard`。界面开启明牌时，只有同时满足以下条件的输出
使用 `revealed`：

- 初始化结果声明该输出支持明牌；
- 当前牌谱具有完整的明牌信息。

不满足任一条件时，宿主仍向该输出传递 `standard` 数据。同一引擎的不同输出可以具有不同
的明牌支持。需要不同输入模式的输出不得合并到同一次 `analysis.run` 请求中。

## 5. 权重槽位

引擎在 `engine.hello` 中通过 `weightSlots` 声明需要用户配置的权重文件。一个引擎可以声明
多个槽位，也可以不需要权重。每个槽位接收一个文件；需要多个文件时声明多个槽位。

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
          "id": "example-backbone-v1",
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

一个输出可以要求多个槽位，一个槽位也可以被多个输出共用。宿主根据当前交给该引擎配置
的输出决定哪些槽位需要选择文件；不需要的槽位可以淡化显示。扩展名不能替代引擎对文件
内容和结构的校验。

## 6. 初始化

### 6.1 初始化请求

```json
{
  "enabledOutputs": [
    {"id": "action-recommendation", "version": 1},
    {"id": "opponent-dora-count", "version": 1}
  ],
  "weights": [
    {
      "slotId": "backbone",
      "format": "example-backbone-v1",
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
| `device` | 是 | 设备选择。具体允许值由进程协议和引擎能力确定。 |
| `options` | 是 | 按引擎声明的选项结构校验的参数对象。 |

请求必须为每个当前必需的槽位提供一个文件，且不得包含未知、重复或当前不需要的槽位。
引擎必须验证文件格式和内容，不能只依赖扩展名。

文件摘要由宿主在需要识别结果来源时计算，不通过初始化请求要求引擎代为校验或回显。

### 6.2 初始化结果

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
          "preferredDirection": "higher"
        },
        {
          "id": "policy",
          "title": {"default": "Policy"},
          "format": "percentage",
          "preferredDirection": "higher"
        },
        {
          "id": "expected-placement",
          "title": {"default": "Expected placement"},
          "format": "number",
          "preferredDirection": "lower"
        }
      ],
      "primaryMetricId": "q-value"
    },
    {
      "id": "opponent-dora-count",
      "version": 1,
      "representations": ["distribution", "expected-value"],
      "supportsRevealedHands": true
    }
  ],
  "effectiveOptions": {}
}
```

`outputs` 必须与请求中的输出逐项对应。初始化结果可以把握手中声明的表示、评估指标或明牌
能力收窄，但不得增加能力。无法提供任一请求输出时，初始化整体失败，不得静默删除输出。

对于数值预测，初始化结果中的 `representations` 是当前配置之后每次返回结果时必须使用的
固定表示。对于动作推荐，`metrics` 和 `primaryMetricId` 的规则见第13节。宿主根据这些固定
声明安排界面；单次结果缺少数据时不得改变界面结构。

`effectiveOptions` 包含应用默认值后的最终参数。修改已启用输出、权重文件、设备或参数后
需要重新初始化。

## 7. 统一分析请求

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
    "events": [],
    "outputs": [
      {
        "id": "action-recommendation",
        "version": 1,
        "parameters": {
          "candidates": [
            {
              "candidateId": "candidate:0",
              "action": {}
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

同一请求中的所有输出使用相同的历史、受控座位和输入模式。只有交给同一个已初始化引擎
配置的输出才能合并。引擎必须返回请求中的全部输出且不得增加额外输出；任一输出失败时，
整个 JSON-RPC 请求返回错误，不返回部分结果。

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
| `outputs` | 是 | 与请求的输出引用恰好一一对应。 |
| `outputs[].data` | 是 | 对应输出契约定义的结果对象。 |
| `timing` | 否 | 本次请求的耗时；`totalMs` 为非负有限数值，单位为毫秒。 |

请求和结果由 JSON-RPC 的 `id` 关联。结果不重复回显会话、历史、输入模式或来源指纹。

## 8. `opponent-shanten`

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
| `players` | 是 | 第1.6节定义的其他座位。 |
| `players[].seat` | 是 | 对应玩家的绝对座位。 |
| `players[].shanten` | 是 | 恰好包含唯一整数 `0..6` 的七项概率分布；`0` 表示听牌。 |
| `players[].furitenOrNoYaku` | 是 | `P(振听或无役 \| 0向听)`。 |

`furitenOrNoYaku` 固定属于 `opponent-shanten`，不是独立输出契约。宿主需要拆分听牌显示时
可以计算：

```text
可荣和听牌 = P(0向听) × (1 - furitenOrNoYaku)
振听或无役 = P(0向听) × furitenOrNoYaku
```

## 9. `opponent-deal-in-probability`

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

`players` 使用第1.6节定义的其他座位。每个 `tiles` 必须恰好包含34种牌，值表示受控座位
打出该牌时被对应玩家荣和的概率。示例中的牌种为节选，实际结果不得省略。

## 10. `opponent-concealed-tile-count`

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
      }
    }
  ]
}
```

`players` 使用第1.6节定义的其他座位。每个 `tiles` 必须恰好包含34种牌。离散分布存在时
必须包含唯一的 `0..4` 五项；规则上不可能的数量仍保留并使用精确数值 `0`。宿主可以从
分布派生“至少持有一张”的概率 `1 - P(0)`。

## 11. `wall-tile-count`

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
  }
}
```

输出表示当前事件完成后，尚未公开且仍留在牌山中的各种牌的数量。它只表示整个未公开
牌山 `all-unrevealed-wall`，不区分活牌区域和王牌区域，也不提供区域字段。

`tiles` 必须恰好包含34种牌。离散分布存在时必须包含唯一的 `0..4` 五项。

## 12. `opponent-dora-count`

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
          {"value": 4, "probability": 0.05}
        ],
        "expectedValue": 1.4
      }
    }
  ]
}
```

推荐的统计解释是：条件于对应玩家最终在当前牌局中和牌，预测其和牌结算时实际击中的宝牌
总数，不区分荣和与自摸。计数包括规则认定的普通宝牌和赤牌；玩家立直和牌时，也包括结算
时翻开的里宝牌。尚未确定的宝牌指示牌作为预测的一部分。

按照这一解释，输出不表示玩家当前已经确定持有的宝牌数量，也不乘以最终和牌概率。

协议只要求 `players` 符合第1.6节，离散值为非负整数，`expectedValue` 不得小于 `0`；
不要求引擎采用上述统计解释。引擎可以用该输出表示其他宝牌数量预测，宿主仍按相同数据
结构解析。

## 13. `opponent-score`

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

推荐的统计解释是：条件于对应玩家最终在当前牌局中和牌，预测其和牌结算时由该手牌产生的
打点，不区分荣和与自摸。数值不包括本场加分、立直棒、供托或其他场供。

按照这一解释，荣和时的打点为放铳者就该手牌支付的点数；自摸时为另外三名玩家就该手牌
支付的点数总和。离散分布使用实际点数档位，`expectedValue` 可以位于离散档位之间。输出
不乘以最终和牌概率。

协议只要求 `players` 符合第1.6节，离散值为非负整数点数，`expectedValue` 不得小于 `0`；
不要求引擎采用上述统计解释。引擎可以用该输出表示其他打点预测，宿主仍按相同数据结构
解析。

## 14. `action-recommendation`

### 14.1 请求参数

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

### 14.2 评估指标声明

动作推荐可以声明任意数量的评估指标。指标由 `engine.hello` 列出能力上限，并由初始化结果
确定当前配置使用的固定集合和顺序。

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
  "preferredDirection": "lower"
}
```

| 字段 | 必需 | 格式与意义 |
| --- | --- | --- |
| `id` | 是 | 引擎定义的稳定指标 ID。使用小写 ASCII 字母、数字和连字符，长度为 `1..64`。 |
| `title` | 是 | 多语言短标题。 |
| `description` | 否 | 多语言说明。 |
| `format` | 是 | `number`、`percentage` 或 `points`，用于宿主格式化数值。 |
| `preferredDirection` | 是 | `higher`、`lower` 或 `none`，表示数值的偏好方向。 |

`format` 只规定显示格式，不规定指标的统计意义。指标的意义由稳定 ID、标题和说明共同给出。
相同引擎主版本内，相同指标 ID 的格式、方向和意义不得改变。

初始化结果可以提供 `primaryMetricId`，其值必须是当前 `metrics` 中的一个 ID。宿主可以用
主要指标绘制推荐条或排序明细。没有主要指标时，宿主只根据 `bestCandidateId` 标示推荐动作。

### 14.3 结果

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

`bestCandidateId` 必须是请求候选之一。即使引擎不提供任何评估指标，也必须提供
`bestCandidateId`。

当前配置的 `metrics` 为空时，结果不得提供 `candidates`。`metrics` 非空时，结果必须提供
`candidates`，并恰好覆盖请求中的全部候选。每个候选的 `metrics` 必须恰好包含初始化时
声明的全部指标 ID；值为符合指标格式的有限数值，暂时没有该候选的指标值时使用 `null`。
单个值为 `null` 不改变宿主已经确定的指标列和界面布局。

`percentage` 指标的非空值必须位于 `[0, 1]`。协议不要求不同候选的 `percentage` 数值之和
为 `1`，也不根据 `preferredDirection` 验证 `bestCandidateId`。推荐动作由引擎直接决定。

## 15. 宿主生成的结果来源标识

协议不要求引擎生成或返回来源指纹。需要缓存、比较或展示结果来源时，宿主根据自己实际
启动和传入的内容生成稳定标识，可以包括：

- 引擎程序包或可执行文件的摘要；
- 当前使用的全部权重文件摘要；
- 设备无关的有效参数；
- 输出契约 ID 和版本；
- 初始化结果确定的表示、指标 ID、指标格式和偏好方向；
- 会改变结果数值的宿主后处理版本。

宿主不把本机文件路径、多语言标题或说明写入稳定标识。进程重启次数、请求序号等临时状态
使用单独的运行代次管理，不属于稳定来源标识。协议不规定宿主内部标识的字段名、保存位置
或摘要算法。
