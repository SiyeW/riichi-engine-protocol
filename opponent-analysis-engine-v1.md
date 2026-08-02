# 读牌引擎规范 v1

本文是 `kind: opponent-analysis` 与 `outputSchema: opponent-analysis-v1` 的规范来源，
结果结构另有[机器可读 Schema](schemas/opponent-analysis-v1.schema.json)。
“读牌引擎”是界面名称，协议类型仍使用稳定标识 `opponent-analysis`。实现者还必须遵守
[进程协议](protocol-v1.md)和[共享数据约定](data-contracts-v1.md)。

## 1. 职责边界

宿主负责生成指定可见性模式的 MJAI 历史、调度、实际值计算、缓存和展示。读牌引擎负责：

- 根据受控座位预测另外三个绝对座位；
- 返回 `0..6` 向听分布、振听/无役概率和 34 种牌的铳率；
- 完成模型需要的规则修饰，返回可以直接缓存和展示的最终概率；
- 声明支持的手牌可见性模式；
- 把规则修饰和其他结果语义计入引擎指纹。

宿主不会再次执行现物、同巡振听、立直后听牌率等统一 mask。

## 2. 清单、能力和初始化

`engine.json` 和 `engine.hello` 必须声明：

```json
{
  "kinds": ["opponent-analysis"],
  "modelFormats": [
    {
      "id": "example-opponent-model",
      "extensions": [".onnx"],
      "inputSchema": "example-public-history-v1",
      "outputSchema": "opponent-analysis-v1"
    }
  ],
  "capabilities": {
    "multipleSessions": true,
    "incrementalHistory": true,
    "concurrentRequests": false,
    "cancellation": false,
    "reload": true,
    "probabilities": true,
    "opponentInputModes": ["public"]
  }
}
```

所有读牌引擎和模型必须支持 `public`。引擎可以额外声明 `full-information`；初始化后的
有效模式是引擎能力与模型元数据 `opponentInputModes` 的交集，以运行时初始化结果为准。

初始化成功后必须返回 `outputSchema: opponent-analysis-v1`、有效能力和稳定指纹。

## 3. 输入可见性

允许的 `inputMode`：

| 模式 | 含义 |
| --- | --- |
| `public` | 只包含 `controlledSeat` 正常可见的信息，其他手牌保持未知。 |
| `full-information` | 可以包含牌谱记录的完整四家手牌。 |

宿主只有在用户开启显示手牌、牌谱确有完整信息且当前引擎和模型都声明支持时，才会发送
`full-information`。否则必须发送 `public`。引擎收到未声明模式时返回
`UNSUPPORTED_CAPABILITY`，不得把暗牌猜测成明牌输入。

不同输入模式必须使用不同会话和缓存身份。

## 4. `opponent.predict` 请求

```json
{
  "sessionId": "game-17:seat-0:opponent-analysis:public",
  "positionId": "node-88",
  "historyDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "controlledSeat": 0,
  "inputMode": "public",
  "priority": "interactive",
  "events": []
}
```

字段要求：

| 字段 | 要求 |
| --- | --- |
| `sessionId` | 必须区分牌局、受控座位和输入模式。 |
| `positionId` | 当前节点的宿主身份，只用于结果关联。 |
| `historyDigest` | `events` 的规范摘要，必须原样回显。 |
| `controlledSeat` | 主视角绝对座位 `0..3`。 |
| `inputMode` | `public` 或已协商的 `full-information`。 |
| `priority` | `interactive` 或 `background`。 |
| `events` | 到当前位置为止、符合输入模式的完整 MJAI 历史。 |

## 5. `opponent.predict` 结果

```json
{
  "sessionId": "game-17:seat-0:opponent-analysis:public",
  "positionId": "node-88",
  "historyDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "engineFingerprint": "sha256:cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "inputMode": "public",
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
      "furitenOrNoYaku": 0.03,
      "ronWaits": {
        "1m": 0.0,
        "2m": 0.0012,
        "3m": 0.04
      }
    }
  ],
  "timing": {
    "preprocessMs": 8.0,
    "inferenceMs": 74.2,
    "totalMs": 82.2
  }
}
```

完整结果必须满足：

- `sessionId`、`positionId`、`historyDigest` 和 `inputMode` 原样回显；
- `engineFingerprint` 与本次初始化结果一致；
- `players` 恰好包含 `controlledSeat` 之外三个不重复的绝对座位；
- 每名玩家的 `shanten` 恰好包含唯一的整数值 `0..6`；
- 七项向听概率和在 `1e-4` 容差内等于 `1`；
- `furitenOrNoYaku` 位于 `[0, 1]`；
- `ronWaits` 恰好覆盖全部 34 种规范牌；
- 所有概率都是有限数值并位于闭区间 `[0, 1]`。

示例中的 `ronWaits` 为节选，实际响应不得省略牌种。`timing.totalMs` 应该提供；其他耗时
分量可选。

## 6. 向听和振听语义

`shanten[value].probability` 是该玩家处于对应向听档的分布，其中 `value: 0` 表示听牌。
`furitenOrNoYaku` 是听牌档内部“振听或无役”的比例，不参加七项向听概率求和。

宿主用于饼图的八项展示概率为：

```text
听牌             = P(shanten=0) * (1 - furitenOrNoYaku)
1..6 向听        = P(shanten=1..6)
振听/无役        = P(shanten=0) * furitenOrNoYaku
```

该换算只改变展示形状，不改变引擎预测。引擎不得直接返回第八个向听类别。

## 7. 精确零和规则修饰

协议允许概率精确等于 `0`。引擎应把规则上确定不可能的事件直接输出为数值 `0.0`，例如
其实现能够确定的现物、同巡振听范围或立直后不可能的向听档。立直后的振听/无役概率仍可
保留，不因听牌率被固定而清零。

`0` 表示引擎确认的不可能事件；非零的小概率表示事件仍有可能。引擎不得用一个任意的极小
正数代替规则上确定的零，也不得为了界面阈值提前截断模型的小概率。

宿主展示规则：

- 精确零显示 `0%`；
- 非零且小于 `0.01%` 显示 `<0.01%`；
- 其他悬浮概率固定显示两位小数。

展示格式不属于引擎协议。宿主缓存可以量化显示精度，但必须保留零与正数的区别。

## 8. 实际值、会话和缓存

引擎只返回预测，不得返回 `groundTruth`。研究模式中的“实际值”由宿主使用完整牌谱独立
计算，不传给预测引擎，也不参与引擎指纹。

同一进程可以加载一份权重，但不同牌局、受控座位和输入模式的增量状态必须隔离。请求始终
携带完整 `events`；历史回退、分叉或摘要不一致时，引擎必须恢复共同前缀或完整重放。

引擎指纹必须覆盖引擎版本、权重摘要、有效参数、输出 Schema 和规则修饰语义。宿主缓存键
还包含位置、受控座位和输入模式。旧指纹缓存可以临时预览，但自动分析进度只承认当前指纹。

## 9. 错误和一致性

结构不完整、概率非有限、向听和不为一或缺少牌种时，宿主会拒绝整次结果。引擎不得用部分
结果更新一个玩家。最低一致性测试应覆盖：

- 三个绝对座位和 34 种牌的完整性；
- 向听概率和、边界漂移、精确零与非零极小概率；
- `public` 输入不泄漏隐藏手牌；
- 立直、现物与振听等引擎规则修饰；
- 多会话交错、历史回退和输入模式切换；
- 权重摘要不符、加载失败与重新加载。
