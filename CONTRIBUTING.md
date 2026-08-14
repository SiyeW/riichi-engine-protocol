### [中文](#中文) | [日本語](#日本語) | [English](#english)

---

<div lang="zh-CN">

## 中文

建议使用中文、日文或英文提交 Issue 和 Pull Request；也欢迎使用其他语言。

### 输出契约

新增或修改输出契约前，请先提交 Issue，说明现有契约不能满足的使用场景。Pull Request 需要包含：

- 字段和概率条件的准确定义
- 取值范围、单位和必要的特殊情况
- 完整的请求与结果示例
- 兼容性影响
- 主程序中的显示方式

协议与 Riichi Mahjong Studio 分别提交 Pull Request。需要尽快获得主程序支持时，可以同时向两个仓库提交修改。

### 版本发布

`main` 只保留当前规范。正式版本使用 Git tag 和 GitHub Release 保存；Release 附带当时的三语规范、Schema 和示例。当前仍支持的多个输出契约版本继续保留在现行规范中。

### 提交前检查

- 同步相应的中文、日文和英文规范；无法完成全部翻译时，请在 Pull Request 中注明
- 更新 `CHANGELOG.md`
- 检查 JSON 示例
- 不提交模型权重、训练数据或构建产物

</div>

---

<div lang="ja">

## 日本語

Issue と Pull Request では、中国語、日本語、英語の使用を推奨します。その他の言語も歓迎します。

### 出力契約

出力契約を追加または変更する前に、既存の契約では対応できない用途を Issue で説明してください。Pull Request には次の内容を含めます。

- フィールドと確率条件の明確な定義
- 値の範囲、単位、必要な例外
- 完全なリクエスト例と結果例
- 互換性への影響
- アプリケーション上の表示方法

プロトコルと Riichi Mahjong Studio の変更は、それぞれのリポジトリへ Pull Request を提出してください。アプリケーション側の対応を急ぐ場合は、両方を同時に提出できます。

### バージョンの公開

`main` には現在の仕様だけを置きます。正式版は Git tag と GitHub Release で保存し、Release には当時の3言語の仕様、Schema、サンプルを添付します。現在も対応する複数の出力契約バージョンは、現行仕様に残します。

### 提出前の確認

- 中国語、日本語、英語の該当箇所を更新する。すべての翻訳が難しい場合は、Pull Request にその旨を記載する
- `CHANGELOG.md` を更新する
- JSON サンプルを検証する
- モデルの重み、学習データ、ビルド成果物を含めない

</div>

---

<div lang="en">

## English

Chinese, Japanese, or English is recommended for issues and pull requests. Other languages are equally welcome.

### Output contracts

Before adding or changing an output contract, open an issue describing the use case that the current contracts do not cover. The pull request should include:

- precise definitions for fields and conditional probabilities;
- value ranges, units, and necessary edge cases;
- complete request and result examples;
- compatibility impact; and
- the intended presentation in the host application.

Submit protocol and Riichi Mahjong Studio changes to their respective repositories. If host support is needed immediately, both pull requests may be submitted together.

### Releases

`main` contains only the current specification. Stable versions are preserved with Git tags and GitHub Releases. Each Release includes the three language specifications, schemas, and examples from that version. Output contract versions that remain supported stay in the current specification.

### Before submitting

- Update the corresponding Chinese, Japanese, and English specifications. If you cannot provide every translation, note that in the pull request.
- Update `CHANGELOG.md`.
- Validate the JSON examples.
- Do not add model weights, training data, or build output.

</div>
