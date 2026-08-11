### [中文](#%E4%B8%AD%E6%96%87) | [日本語](#%E6%97%A5%E6%9C%AC%E8%AA%9E) | [English](#english)

---

<div lang="zh-CN">

## 中文

### Riichi Engine Protocol

一套连接立直麻将程序与独立引擎和模型的开放协议。

引擎声明自己能够提供的输出。同一个引擎可以同时提供动作推荐、对手预测、牌山预测及其他兼容输出，主程序也可以将不同输出分别交给不同的引擎。通信采用通过 JSONL 传输的 JSON-RPC 2.0 消息。

### 协议规范

[阅读中文协议规范](protocol.zh-CN.md)

另有[日文版](protocol.ja-JP.md)和[英文版](protocol.en-US.md)。

### 相关项目与许可证

- [riichi-mahjong-studio](https://github.com/SiyeW/riichi-mahjong-studio)：一款使用本协议的立直麻将牌谱研究和对局练习桌面程序

本项目采用 [Apache License 2.0](LICENSE)。

</div>

---

<div lang="ja-JP">

## 日本語

### Riichi Engine Protocol

リーチ麻雀アプリケーションと、独立したエンジンやモデルを接続するためのオープンプロトコルです。

エンジンは、自身が提供できる出力を宣言します。1 つのエンジンで行動の推奨、対戦相手の予測、牌山の予測など複数の出力を提供できるほか、アプリケーション側で出力ごとに別のエンジンを割り当てることもできます。通信には、JSONL で送受信する JSON-RPC 2.0 メッセージを使用します。

### プロトコル仕様

[日本語のプロトコル仕様を読む](protocol.ja-JP.md)

[中国語版](protocol.zh-CN.md)と[英語版](protocol.en-US.md)もあります。

### 関連プロジェクトとライセンス

- [riichi-mahjong-studio](https://github.com/SiyeW/riichi-mahjong-studio)：本プロトコルに対応する、リーチ麻雀の牌譜検討と対局練習のためのデスクトップアプリケーション

本プロジェクトは [Apache License 2.0](LICENSE) で提供されます。

</div>

---

<div lang="en-US">

## English

### Riichi Engine Protocol

An open protocol for connecting Riichi Mahjong applications with independent engines and models.

Each engine declares the outputs it can provide. One engine may combine action recommendations, opponent predictions, wall predictions, and other compatible outputs, while an application may assign different outputs to different engines. Communication uses JSON-RPC 2.0 messages carried over JSONL.

### Protocol specification

[Read the protocol specification in English](protocol.en-US.md)

[Chinese](protocol.zh-CN.md) and [Japanese](protocol.ja-JP.md) versions are also available.

### Related projects and license

- [riichi-mahjong-studio](https://github.com/SiyeW/riichi-mahjong-studio): a desktop application for studying Riichi Mahjong game records and practicing games using this protocol

This project is licensed under the [Apache License 2.0](LICENSE).

</div>
