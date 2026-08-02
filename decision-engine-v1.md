# 决策引擎规范 v1

本文是 `kind: decision` 与 `outputSchema: decision-v1` 的规范来源。结果结构另有
[机器可读 Schema](schemas/decision-v1.schema.json)。实现者还必须遵守
[公共进程协议](protocol-v1.md)和[公共数据契约](data-contracts-v1.md)。

## 1. 职责边界

宿主负责牌局规则、合法动作枚举、任务优先级、牌局推进、缓存和界面。决策引擎负责：

- 从指定座位的 MJAI 历史构建模型输入；
- 维护互相隔离的增量会话；
- 为宿主给出的每个合法候选评分；
- 返回唯一首选、原始值和最终选择概率；
- 应用温度等引擎参数，并把有效参数计入引擎指纹。

引擎不得自行增加、删除或改写合法候选，也不得执行动作或修改牌局。

## 2. 清单和初始化

`engine.json` 和 `engine.hello` 必须声明：

```json
{
  "kinds": ["decision"],
  "modelFormats": [
    {
      "id": "example-model-format",
      "extensions": [".onnx"],
      "inputSchema": "example-observation-v1",
      "outputSchema": "decision-v1"
    }
  ],
  "capabilities": {
    "multipleSessions": true,
    "incrementalHistory": true,
    "concurrentRequests": false,
    "cancellation": false,
    "reload": true,
    "rawValues": true,
    "probabilities": true
  }
}
```

决策引擎必须支持多个会话。`incrementalHistory` 表示能够复用历史前缀，不表示模型权重
本身具有会话状态。`concurrentRequests: false` 允许引擎串行推理；宿主仍可维护多个会话。

引擎参数由 `optionsSchema` 声明。宿主不得根据参数名称猜测类型或默认值。初始化成功后，
引擎必须返回规范化后的 `effectiveOptions`、`outputSchema: decision-v1` 和稳定指纹。

## 3. `decision.analyze` 请求

```json
{
  "sessionId": "game-17:seat-2:recommendation",
  "positionId": "node-88",
  "historyDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "seat": 2,
  "role": "recommendation",
  "priority": "interactive",
  "events": [],
  "candidates": [
    {
      "candidateId": "candidate:0",
      "action": {
        "type": "dahai",
        "actor": 2,
        "pai": "6s",
        "tsumogiri": false
      }
    }
  ]
}
```

字段要求：

| 字段 | 要求 |
| --- | --- |
| `sessionId` | 同一座位的不同用途必须使用不同会话。 |
| `positionId` | 当前节点的宿主身份，只用于结果关联。 |
| `historyDigest` | `events` 的规范摘要，必须原样回显。 |
| `seat` | 绝对座位 `0..3`。 |
| `role` | `play`、`recommendation` 或 `auto-analysis`。 |
| `priority` | `play`、`interactive` 或 `background`。 |
| `events` | 到当前位置为止的完整 MJAI 历史。 |
| `candidates` | 至少一个、ID 互不重复的权威合法候选。 |

`candidateId` 仅在本次请求中稳定，是不透明关联键。引擎不得依赖其字符串结构；动作语义
必须读取 `action`。

## 4. 候选动作

v1 的候选动作至少包括：

- `dahai`
- `reach`
- `chi`
- `pon`
- `daiminkan`
- `ankan`
- `kakan`
- `hora`
- `ryukyoku`
- `none`

副露必须保留 `target`、`pai`、`consumed` 和必要的 `variant`。暗杠没有 `target`。
加杠的动作内容必须能区分追加牌与原碰牌组。

立直后的暗杠选择中，放弃暗杠仍使用 `type: "none"`、`variant: "skip_ankan"`，
并携带强制摸切的 `pai` 与 `tsumogiri: true`。引擎应按该弃牌的模型动作评价它，
而不是按副露响应阶段的普通 `none` 评价。

宿主可以同时提供看似相同但实体不同的候选，例如同一张牌的摸切与手切，或使用红五、
黑五的不同副露组合。引擎必须保留全部候选。

## 5. `decision.analyze` 结果

```json
{
  "sessionId": "game-17:seat-2:recommendation",
  "positionId": "node-88",
  "historyDigest": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "engineFingerprint": "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "bestCandidateId": "candidate:0",
  "choices": [
    {
      "candidateId": "candidate:0",
      "scoreGroupId": "model-action:6s",
      "rawValue": 1.284,
      "probability": 0.423
    }
  ],
  "timing": {
    "totalMs": 70.3
  }
}
```

结果必须满足：

- `sessionId`、`positionId` 和 `historyDigest` 原样回显；
- `engineFingerprint` 与本次初始化结果一致；
- `bestCandidateId` 是原请求中的一个候选；
- `choices` 恰好覆盖所有候选，每个候选只出现一次；
- 每项 `rawValue` 是有限数值；
- 每项 `probability` 位于闭区间 `[0, 1]`；
- 按不同 `scoreGroupId` 去重后的概率和在 `1e-4` 容差内等于 `1`。

`timing.totalMs` 应该提供；`preprocessMs`、`queueMs` 和 `inferenceMs` 可以按引擎能力提供。

## 6. 评分组和实体候选

`scoreGroupId` 省略时等于 `candidateId`。当模型无法区分多个实体候选时，可以给它们相同
的评分组，但同组的 `rawValue` 和 `probability` 必须完全一致。概率总和按评分组计算，
不是按 `choices` 行数计算。

例如某个引擎无法分别评价同牌的摸切与手切时，两项可以共享评分。宿主仍通过
`bestCandidateId` 确定首选圆点和实际执行候选，因此首选只能落在其中一个实体候选上。
红五和黑五组成的副露也遵循同一规则。

引擎如果能够区分实体候选，则必须使用不同评分组并分别给值。宿主不会自行合并它们。

## 7. 会话、增量和调度

同一引擎进程可以只加载一份权重，但以下状态必须相互隔离：

- 四个绝对座位；
- `play`、`recommendation` 与 `auto-analysis`；
- 不同牌局；
- 不同历史分支。

请求始终携带完整 `events`。引擎可以在历史为旧历史的后缀扩展时增量更新；发生回退、
分叉或摘要不一致时，必须从共同前缀恢复或完整重放。不能增量的引擎可以每次完整重放。

强制摸切、没有选择的推进节点等由宿主判断，宿主可以不调用决策引擎。

## 8. 缓存、错误和一致性

引擎指纹必须覆盖引擎版本、权重摘要、有效参数、输出 Schema 及会改变结果的后处理语义。
同一位置的旧指纹缓存可以临时预览，但不会被视为当前引擎结果。

无法为任一合法候选给出完整结果时，必须返回错误，例如 `INVALID_MODEL_OUTPUT`，不得静默
省略候选或用 `NaN`、无穷大代替。最低一致性测试应覆盖：

- 候选完整性、重复 ID 和未知首选；
- 概率和、非有限数值和评分组一致性；
- 摸切/手切及红五/黑五共享评分；
- 多会话交错、历史回退和分支切换；
- 权重摘要不符、加载失败与重新加载。
