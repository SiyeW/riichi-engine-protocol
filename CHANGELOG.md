# Changelog

## [Unreleased]

<div lang="zh-CN">

### 中文

- `kyoku-outcome` v2 可以提供四家的直接和牌、放铳概率以及包含双响、三响的互斥最终结果分布。
- 数值预测新增 `point-estimate` 表示，可以同时提供离散分布和独立的标量预测。
- 数值分布可以使用输出契约规定的字符串区间；宝牌数量支持以 `N+` 表示不小于 `N` 的数量。
- 补充暗牌数量、牌山剩余数量等标量预测的取值范围。
- 暗牌和牌山枚数预测可以分别输出三种赤五的数量。
- 协商到较低 `minor` 时，引擎不会使用更高版本新增的协议内容。

</div>

<div lang="ja-JP">

### 日本語

- `kyoku-outcome` v2 で、4 人の和了率・放銃率を直接出力できるほか、ダブロンやトリプルロンを含む排他的な局結果分布も出力できるようにしました。
- 数値予測に `point-estimate` を追加し、離散分布と独立したスカラー予測値を同時に出力できるようにしました。
- 出力契約で定義された文字列の範囲を数値分布で使用できるようにし、ドラ数では `N` 以上を `N+` で表せるようにしました。
- 手牌枚数や牌山の残り枚数など、スカラー予測値の範囲を明記しました。
- 手牌と牌山の枚数予測で、3種類の赤五を個別に出力できるようにしました。
- 低い `minor` で合意した場合、エンジンはそれより新しいバージョンで追加されたプロトコル要素を使用しません。

</div>

<div lang="en-US">

### English

- Allow `kyoku-outcome` v2 to provide direct win and deal-in probabilities for all four players, an exclusive outcome distribution including double and triple ron, or both.
- Add `point-estimate` to numeric predictions so an engine can provide a discrete distribution and an independent scalar prediction together.
- Allow numeric distributions to use string ranges defined by their output contract, including `N+` for dora counts of at least `N`.
- Specify scalar ranges for concealed-hand tile counts, remaining wall tile counts, and related outputs.
- Allow concealed-hand and wall count predictions to report each of the three red fives separately.
- Prevent engines from using protocol additions from a higher `minor` after negotiating a lower version.

</div>

## [2.1.0] - 2026-08-15

<div lang="zh-CN">

### 中文

- 新增 `kyoku-outcome` v1，可输出当前小局的流局概率，以及各玩家的和牌概率、放铳概率和和牌目标的条件概率。
- 新增 `kyoku-score-delta` v1，可输出本局结算时各玩家相对当前分数的期待点数变化。
- 新增 `match-placement` v1，可输出各玩家的终局顺位分布和期待顺位。
- 新增 `match-score` v1，可输出各玩家的终局点数分布和期待点数。

</div>

<div lang="ja-JP">

### 日本語

- 現在の局の流局確率と、各プレイヤーの和了確率、放銃確率、和了時の対象確率を出力する `kyoku-outcome` v1 を追加しました。
- 現在の持ち点から局の精算後までに見込まれる各プレイヤーの持ち点変化を出力する `kyoku-score-delta` v1 を追加しました。
- 各プレイヤーの最終順位の分布と期待順位を出力する `match-placement` v1 を追加しました。
- 各プレイヤーの最終持ち点の分布と期待値を出力する `match-score` v1 を追加しました。

</div>

<div lang="en-US">

### English

- Add `kyoku-outcome` v1 for the current kyoku's draw probability and each player's win, deal-in, and conditional win-target probabilities.
- Add `kyoku-score-delta` v1 for each player's expected score change through settlement of the current kyoku.
- Add `match-placement` v1 for each player's final placement distribution and expected placement.
- Add `match-score` v1 for each player's final score distribution and expected score.

</div>
