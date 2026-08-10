[English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

### Riichi Engine Protocol

An open protocol for connecting Riichi Mahjong applications with independently
distributed engines and models.

Engines declare the outputs they provide. A single engine can combine action
recommendations, opponent predictions, wall predictions, and other compatible
outputs. Messages use JSON-RPC 2.0 over JSONL.

The protocol is under development and may change before its first stable release.

### Specification

[Engine outputs and analysis requests](protocol.md)

### License

Licensed under the Apache License 2.0. Third-party code and materials retain
their respective licenses; see
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).

---

## 中文

### Riichi Engine Protocol

一套连接立直麻将程序与独立发布的引擎和模型的开放协议。

引擎通过输出契约声明自己能够提供的数据。同一个引擎可以同时提供动作推荐、对手预测、牌山预测或其他兼容输出。协议通过 JSONL 传输 JSON-RPC 2.0 消息。

协议目前仍在开发，首个稳定版本发布前可能继续调整。

### 协议文档

[引擎输出与分析请求](protocol.md)

### 许可证

采用 Apache License 2.0。第三方代码和素材适用各自的许可条款，详见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。

---

## 日本語

### Riichi Engine Protocol

リーチ麻雀アプリケーションと、個別に配布されるエンジンおよびモデルを接続するための
オープンプロトコルです。

エンジンは出力契約を通じて、提供できるデータを宣言します。1つのエンジンで、行動の
推奨、対戦相手の予測、牌山の予測など、互換性のある複数の出力を提供できます。
メッセージは JSONL 形式で JSON-RPC 2.0 を送受信します。

本プロトコルは開発中であり、最初の安定版を公開するまで変更される可能性があります。

### 仕様書

[エンジンの出力と解析リクエスト](protocol.md)

### ライセンス

Apache License 2.0 で提供されます。第三者のコードと素材には、それぞれの
ライセンス条件が適用されます。詳しくは
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) を参照してください。
