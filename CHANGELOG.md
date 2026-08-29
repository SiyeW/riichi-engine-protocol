# Changelog

## [Unreleased]

<div lang="zh-CN">

### 中文

- `kyoku-outcome` 使用包含自摸、荣和、双响和三响的互斥最终结果分布取代和牌目标条件概率；四家的和牌、放铳概率也可以单独提供。
- 输出引用不再包含单独的 `version`；输出结构由协商后的协议版本确定。
- 数值预测新增 `point-estimate` 表示，可以同时提供离散分布和独立的标量预测。
- 数值分布可以使用输出契约规定的字符串区间；宝牌数量支持以 `N+` 表示不小于 `N` 的数量。
- 补充暗牌数量、牌山剩余数量等标量预测的取值范围。
- 暗牌和牌山枚数预测可以分别输出三种赤五的数量。
- 协商到较低 `minor` 时，引擎不会使用更高版本新增的协议内容。

</div>

<div lang="ja-JP">

### 日本語

- `kyoku-outcome` の和了対象条件確率を、ツモ、ロン、ダブロン、トリプルロンを含む排他的な局結果分布に置き換えました。4人の和了率と放銃率だけを出力することもできます。
- 出力参照から個別の `version` を削除し、合意したプロトコルバージョンで出力構造を決めるようにしました。
- 数値予測に `point-estimate` を追加し、離散分布と独立したスカラー予測値を同時に出力できるようにしました。
- 出力契約で定義された文字列の範囲を数値分布で使用できるようにし、ドラ数では `N` 以上を `N+` で表せるようにしました。
- 手牌枚数や牌山の残り枚数など、スカラー予測値の範囲を明記しました。
- 手牌と牌山の枚数予測で、3種類の赤五を個別に出力できるようにしました。
- 低い `minor` で合意した場合、エンジンはそれより新しいバージョンで追加されたプロトコル要素を使用しません。

</div>

<div lang="en-US">

### English

- Replace `kyoku-outcome`'s conditional win-target probabilities with mutually exclusive outcomes covering tsumo, ron, double ron, and triple ron. Engines may also provide only the four players' direct win and deal-in probabilities.
- Remove the separate `version` from output references; the negotiated protocol version now determines each output's structure.
- Add `point-estimate` to numeric predictions so an engine can provide a discrete distribution and an independent scalar prediction together.
- Allow numeric distributions to use string ranges defined by their output contract, including `N+` for dora counts of at least `N`.
- Specify scalar ranges for concealed-hand tile counts, remaining wall tile counts, and related outputs.
- Allow concealed-hand and wall count predictions to report each of the three red fives separately.
- Prevent engines from using protocol additions from a higher `minor` after negotiating a lower version.

</div>

## [2.1.0] - 2026-08-15

<div lang="zh-CN">

### 中文

- 新增 `kyoku-outcome`，可输出当前小局的流局概率，以及各玩家的和牌概率、放铳概率和和牌目标的条件概率。
- 新增 `kyoku-score-delta`，可输出本局结算时各玩家相对当前分数的期待点数变化。
- 新增 `match-placement`，可输出各玩家的终局顺位分布和期待顺位。
- 新增 `match-score`，可输出各玩家的终局点数分布和期待点数。

</div>

<div lang="ja-JP">

### 日本語

- 現在の局の流局率と、各プレイヤーの和了率、放銃率、和了時の対象確率を出力する `kyoku-outcome` を追加しました。
- 現在の持ち点から局の精算後までに見込まれる各プレイヤーの持ち点変化を出力する `kyoku-score-delta` を追加しました。
- 各プレイヤーの最終順位の分布と期待順位を出力する `match-placement` を追加しました。
- 各プレイヤーの最終持ち点の分布と期待値を出力する `match-score` を追加しました。

</div>

<div lang="en-US">

### English

- Add `kyoku-outcome` for the current kyoku's draw probability and each player's win, deal-in, and conditional win-target probabilities.
- Add `kyoku-score-delta` for each player's expected score change through settlement of the current kyoku.
- Add `match-placement` for each player's final placement distribution and expected placement.
- Add `match-score` for each player's final score distribution and expected score.

</div>
