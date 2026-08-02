[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

### Riichi Engine Protocol

An open protocol for communication between Riichi Mahjong applications and
third-party engines, including package formats for independently distributed
engines and models.

Messages use JSON-RPC 2.0 over JSONL. Two engine types are currently supported:
decision engines score legal actions and make recommendations, while
opponent-analysis engines predict opponents' shanten states and tile-specific
deal-in risk.

Still in early development, so the specification may change. Feedback,
discussion, and compatible engine implementations are welcome.

### Protocol documents

Recommended reading order:

1. [Architecture and responsibilities](architecture.md)
2. [Process protocol v1](protocol-v1.md)
3. [Shared data contracts v1](data-contracts-v1.md)
4. [Engine and model package format v1](package-format-v1.md)

Then choose the specification for the engine type being implemented:

- [Decision engine v1](decision-engine-v1.md)
- [Opponent-analysis engine v1](opponent-analysis-engine-v1.md)

Also see the [developer guide](developer-guide.md),
[machine-readable schemas](schemas/), and
[minimal decision-engine example](examples/mock-decision-engine/README.md).

### Normative terms

In the Chinese specification, **必须 / 不得** marks requirements,
**应该 / 不应该** marks recommendations, and **可以** marks optional behavior.

### Development

#### Requirements

- Miniconda, Miniforge, or another Conda-compatible environment manager
- Windows PowerShell for building the example engine

#### Create the build environment

```powershell
.\setup-environment.ps1
```

Creates or updates `.conda-build` in the project directory.

#### Run the protocol checks

```powershell
.\.conda-build\python.exe scripts\check_protocol.py
```

#### Build the example engine

```powershell
.\examples\mock-decision-engine\build.ps1
```

Output: `examples/mock-decision-engine/runtime/`

### Terminology

See [`docs/terminology.md`](docs/terminology.md).

### License

Licensed under the Apache License 2.0. Third-party code and materials retain
their respective licenses; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## 中文

### Riichi Engine Protocol

一套供立直麻将程序与第三方引擎通信的开放协议，同时规定了独立发布引擎和模型所需的程序包格式。

协议通过 JSONL 传输 JSON-RPC 2.0 消息。目前支持两类引擎：决策引擎为合法动作评分并给出建议；对手分析引擎预测对手的向听状态和各牌张的放铳风险。

协议仍在早期开发阶段，内容可能继续调整。欢迎通过 Issue 反馈问题、提出建议或参与讨论，也欢迎开发兼容的第三方引擎！

### 协议文档

建议按以下顺序阅读：

1. [架构与职责划分](architecture.md)
2. [进程协议 v1](protocol-v1.md)
3. [共享数据约定 v1](data-contracts-v1.md)
4. [引擎与模型程序包格式 v1](package-format-v1.md)

然后选择需要实现的引擎规范：

- [决策引擎 v1](decision-engine-v1.md)
- [对手分析引擎 v1](opponent-analysis-engine-v1.md)

另可参阅[开发指南](developer-guide.md)、[机器可读 Schema](schemas/)和[最小决策引擎示例](examples/mock-decision-engine/README.md)。

### 规范用语

中文规范中的“必须 / 不得”表示要求，“应该 / 不应该”表示建议，“可以”表示可选行为。

### 开发环境

#### 前置要求

- Miniconda、Miniforge 或其他兼容 Conda 的环境管理工具
- Windows PowerShell，用于构建示例引擎

#### 创建构建环境

```powershell
.\setup-environment.ps1
```

在项目目录内创建或更新 `.conda-build`。

#### 运行协议检查

```powershell
.\.conda-build\python.exe scripts\check_protocol.py
```

#### 构建示例引擎

```powershell
.\examples\mock-decision-engine\build.ps1
```

输出目录：`examples/mock-decision-engine/runtime/`

### 术语表

详见 [`docs/terminology.md`](docs/terminology.md)。

### 许可证

采用 Apache License 2.0。第三方代码和素材适用各自的许可条款，详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

---

## 日本語

### Riichi Engine Protocol

リーチ麻雀アプリケーションとサードパーティー製エンジンを接続するオープンプロトコルです。
エンジンとモデルを個別に配布するためのパッケージ形式も定めています。

JSON-RPC 2.0 メッセージを JSONL 形式で送受信します。現在は、合法な候補手を
評価して推奨を返す意思決定エンジンと、対戦相手のシャンテン状態および牌ごとの
放銃リスクを予測する対戦相手分析エンジンに対応しています。

現在は初期開発段階のため、仕様が変更される可能性があります。Issue での
フィードバック、議論への参加、互換エンジンの開発を歓迎します。

### プロトコル文書

次の順序で読むことをお勧めします。

1. [アーキテクチャと責任分担](architecture.md)
2. [プロセスプロトコル v1](protocol-v1.md)
3. [共有データ規約 v1](data-contracts-v1.md)
4. [エンジンとモデルのパッケージ形式 v1](package-format-v1.md)

続いて、実装するエンジンの仕様を参照してください。

- [意思決定エンジン v1](decision-engine-v1.md)
- [対戦相手分析エンジン v1](opponent-analysis-engine-v1.md)

そのほかに、[開発ガイド](developer-guide.md)、[機械可読スキーマ](schemas/)、
[最小意思決定エンジンのサンプル](examples/mock-decision-engine/README.md)もあります。

### 規範用語

中国語版の仕様では、「必须 / 不得」は必須要件、「应该 / 不应该」は推奨事項、
「可以」は任意の動作を表します。

### 開発環境

#### 必要条件

- Miniconda、Miniforge、または Conda 互換の環境管理ツール
- 現在のサンプルエンジンのパッケージ作成に使用する Windows PowerShell

#### ビルド環境の作成

```powershell
.\setup-environment.ps1
```

プロジェクト内に `.conda-build` を作成または更新します。

#### プロトコルチェックの実行

```powershell
.\.conda-build\python.exe scripts\check_protocol.py
```

#### サンプルエンジンのビルド

```powershell
.\examples\mock-decision-engine\build.ps1
```

出力先：`examples/mock-decision-engine/runtime/`

### 用語集

詳しくは [`docs/terminology.md`](docs/terminology.md) を参照してください。

### ライセンス

Apache License 2.0 で提供されます。第三者のコードと素材には、それぞれの
ライセンス条件が適用されます。詳しくは
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) を参照してください。
