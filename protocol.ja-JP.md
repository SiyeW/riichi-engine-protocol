### [中文](protocol.zh-CN.md) | [日本語](protocol.ja-JP.md) | [English](protocol.en-US.md)

<div lang="ja-JP">

# Riichi Engine Protocol

エンジンは、自身が提供できるデータを出力契約によって宣言します。1つのエンジンで複数の出力を同時に提供できるほか、ホスト側で出力ごとに別のエンジン構成を割り当てることもできます。エンジンのモデル構造、学習方法、内部データ構造は本プロトコルの対象外です。

エンジンプロセスは JSON-RPC 2.0 と JSONL を使用してホストと通信します。本稿では、エンジンプログラムパッケージ、プロセス通信、局入力、出力宣言、重みの要件、初期化、解析リクエスト、および標準出力データを定義します。局データは四人リーチ麻雀にのみ適用されます。

## プロトコルのバージョン

プロトコル識別子は固定されます：

```json
{
  "name": "riichi-engine-protocol",
  "major": 2,
  "minor": 2
}
```

`major` 異なる双方は通信を継続してはならない。ホストは `engine.hello` リクエストで自分がサポートする最高の `minor` を提示する；エンジンは双方が共通でサポートする最高の `minor` を返し、ホストのリクエスト値を超えてはならない。`minor` を引き上げることは、無視可能なフィールド、メソッド、または能力を増やすことしかできず、既存のフィールドやメソッドの意味を変更してはならない。

`engine.hello` の結果とそれ以降のメッセージは、合意した `minor` に従う必要があります。エンジンは、それより新しい `minor` で追加されたフィールド、値、メソッド、機能を使用してはいけません。

出力契約は独立したバージョンを持っています。プロトコルのバージョンが同じだからといって、双方が同じ出力をサポートするとは限りません；ホストは、自身が認識しており、かつエンジンが宣言した出力のみを使用します。エンジンが追加の出力を宣言しても、ホストがエンジン全体を拒否する原因にはなりません。

## プロセスと通信

ホストはシェルでコマンドを連結せず、直接エンジンの実行ファイルを起動する。エンジンは標準入力からメッセージを読み取り、標準出力にメッセージを書き込み、ログを標準エラーに書き込む。標準入力と標準出力は UTF-8 を使用する；各行は正確に 1 つの完全な JSON オブジェクトを含み、`\n` で終了する必要がある。プロトコル行は 8 MiB を超えてはならず、空行は無視できる。

すべてのメッセージは JSON-RPC 2.0 に従います：

| メッセージ | 必須フィールド | 説明 |
| --- | --- | --- |
| リクエスト | `jsonrpc`、`id`、`method`、`params` | `jsonrpc` は `"2.0"` に固定。`id` はホストが生成する空でない文字列または整数。 |
| 成功応答 | `jsonrpc`、`id`、`result` | `id` はリクエストと一致する必要があります。 |
| エラー応答 | `jsonrpc`、`id`、`error` | `error` の構造は「エラー」の節を参照してください。 |
| 通知 | `jsonrpc`、`method`、`params` | `id`を含まず、受信者は返信してはいけません。 |

ホストはエンジンにリクエストと通知を送信します。エンジンはホストに対して応答と通知のみを送信し、ホストのメソッドを逆方向で呼び出すことはありません。リクエストは正確に1つの成功応答またはエラー応答を受け取る必要があります。JSON の数値は有限でなければならず、ブール値は数値と見なされません。

解析エラーや無効なリクエストにより、受信側がリクエスト ID を取得できない場合、エラー応答の `id` は `null` を使用します。それ以外の場合、応答 ID はリクエストと完全に一致する必要があります。

## エンジンパッケージ

エンジンプログラムパッケージは `engine.json` をエントリーポイントとして使用します。プログラムパッケージは読み取り専用のディレクトリに配置できます；重みファイルとユーザー設定はエンジンプログラムパッケージに含まれず、このディレクトリには書き戻されません。

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `schemaVersion` | はい | `2` に固定されています。 |
| `id` | はい | エンジンの安定 ID で、小文字の ASCII 文字、数字、ドットおよびハイフンを使用し、長さは `3..128` です。 |
| `name` | はい | ユーザー向けのデフォルト名で、長さは `1..128` です。 |
| `version` | はい | エンジンのバージョンで、セマンティックバージョニングを使用しています。 |
| `sourceUrl` | いいえ | 現在のパッケージに対応する公開ソースコードのアドレス。 |
| `protocol` | はい | エンジンが実装するプロトコルの名前と最高バージョンです。 |
| `entrypoints` | はい | 非空のプラットフォーム入口オブジェクトです。プラットフォームキーは小文字の ASCII 文字、数字、およびハイフンを使用します。 |
| `entrypoints.*.executable` | はい | `engine.json` に対する実行可能ファイルのパスです。 |
| `entrypoints.*.arguments` | はい | 文字列パラメータの配列；各項目は独立したパラメータとして渡されます。 |
| `licenses` | はい | 空でないライセンスファイルの配列です。 |
| `licenses[].name` | はい | ライセンス名です。 |
| `licenses[].path` | はい | `engine.json` に対するライセンスファイルのパスです。 |
| `notices` | いいえ | 第三者通知などの追加ファイルの配列で、フィールドは `licenses` と同じです。 |

パッケージ内のパスはすべて `/` を使用しなければならず、絶対パスであってはならず、空のセグメント、`.` または `..` を含んではいけません。解析後もパッケージディレクトリ内にある必要があります。ホストは現在のプラットフォームと完全に一致するエントリのみを選択し、パッケージディレクトリをプロセスの作業ディレクトリとして使用します。

`engine.json` はエンジンの種類、出力、重みの形式、パラメータ、または実行能力を明示しません。ホストがプロセスを起動した後、これらの情報の唯一の根拠として `engine.hello` を使用し、ハンドシェイクで返されるエンジン ID とバージョンがパッケージと一致することを確認する必要があります。

## 共通データ型

### 出力参照

ハンドシェイク、初期化、リクエストの解析に使用される出力参照を使用します：

```json
{
  "id": "opponent-shanten",
  "version": 1
}
```

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `id` | はい | 出力契約の安定した ID です。小文字の ASCII 文字、数字、ハイフンを使用し、長さは `3..128` です。 |
| `version` | はい | 出力契約のメジャーバージョンで、値は `1` 以上の整数です。 |

フィールドの意味、確率条件、目標定義を変更したり既存のフィールドを削除する場合は、`version`を上げる必要があります。受信側が無視できるオプションのフィールドを追加する場合、メジャーバージョンを上げる必要はありません。

### 多言語テキスト

エンジンがユーザーに表示するタイトルと説明には、多言語テキストオブジェクトを使用します：

```json
{
  "default": "Backbone weights",
  "en": "Backbone weights",
  "zh-CN": "主模型权重",
  "ja": "基盤モデルの重み"
}
```

| キー | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `default` | はい | 一致する言語が見つからない場合に使用されるテキストで、長さは `1..256` です。 |
| その他のキー | いいえ | BCP 47 言語タグおよびそのテキスト、長さは `1..256`。 |

ホストは順番に完全な言語タグ、メイン言語タグ、そして `default` を試します。すべてのテキストはプレーンテキストとして表示され、HTML、Markdown、または端末の制御文字は解釈されません。

### 確率と離散分布

確率は閉区間 `[0, 1]` にある有限の JSON 数値でなければならず、`NaN` や無限大であってはいけません。確率分布の確率の合計は `1e-4` の許容範囲内で `1` でなければなりません。

離散分布は次の構造を使用します：

```json
[
  {"value": 1000, "probability": 0.10},
  {"value": 2000, "probability": 0.25},
  {"value": 3900, "probability": 0.45},
  {"value": 8000, "probability": 0.20}
]
```

`value` は文字列または有限の JSON 数値でなければならず、同じ分布内で重複してはなりません。配列の順序はプロトコル上の意味を持ちません。ホストは出力契約および表示の必要に応じて順序を再配置できます。それぞれの項目の `probability` は対応する値の確率を示し、明示されていない値は確率 `0` と見なされます。具体的な出力契約は `value` の型および値の範囲をさらに制限することができます。

### 数値予測

数値予測は次の形式を使用します。

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

数値予測では、次の3つの表現を使用できます。

| 表示 | 対応フィールド | 形式と意味 |
| --- | --- | --- |
| `distribution` | `distribution` | 離散確率分布。 |
| `expected-value` | `expectedValue` | 予測値の数学的期待値。有限の JSON 数値でなければなりません。 |
| `point-estimate` | `pointEstimate` | エンジンが直接出力するスカラー予測値。有限の JSON 数値でなければなりません。 |

数値予測の `distribution` では、個別の出力契約で文字列の範囲を定義している場合を除き、`value` は有限の JSON 数値でなければなりません。文字列の範囲を含む分布は `expected-value` と併用できず、スカラー値の算出にも使用できません。

現在のエンジン構成では、初期化時に各出力がどの表現を使用するかが決定されます。宣言されたフィールドは、その後の対応するすべての結果に含め、宣言していないフィールドは含めてはいけません。`distribution` と `expected-value` の両方を宣言する場合、`expectedValue` は `distribution` の加重平均と一致しなければなりません。絶対誤差または相対誤差 `1e-4` まで許容されます。`pointEstimate` は独立した表現であり、`expectedValue` や分布の加重平均と一致する必要はありません。

ホストは、利用可能な表現をどのように使用するかを独自に決められます。数値だけの `distribution` が提供される場合、その加重平均をスカラー値として使用できます。`point-estimate` も提供される場合は、`pointEstimate` を優先することもできます。

枚数分布の値は非負整数、打点分布の値は非負の整数点でなければなりません。枚数と打点の `expectedValue` および `pointEstimate` は `0` 以上とし、実際に取り得る離散値と一致する必要はありません。

### 牌

物理牌は次の文字列で表します。

```text
1m..9m, 1p..9p, 1s..9s, 5mr, 5pr, 5sr, E, S, W, N, P, F, C
```

`5mr`、`5pr`、`5sr` は赤五を表します。`?` は現在の入力モードから見えない暗牌を表し、対局イベントにのみ使用できます。候補アクションや出力結果には使用できません。

牌の種類ごとの予測出力には34種類の牌を使用し、赤ドラは区別しません。キー名は：

```text
1m..9m, 1p..9p, 1s..9s, E, S, W, N, P, F, C
```

完全な結果には、この34個のキーを過不足なく含める必要があります。アクションデータの物理牌には赤五の表記を残すことができます。

### 座席

座席には絶対番号 `0..3` を使用し、現在の親や画面の視点に合わせて回転させません。制御対象の座席から見た対戦相手の予測では、`players` に他の3席を過不足なく一度ずつ含め、制御対象の座席は含めてはいけません。

### 対局イベント

`analysis.run.events` は、発生順に並べられた MJAI イベントオブジェクトを使用します。各リクエストは現在の局の完全な履歴を携帯し、最初の項目は `start_kyoku` でなければなりませんが、その前に `start_game` を含めることもできます。エンジンは共通の接頭辞をキャッシュすることができますが、ホストに増分サフィックスのみを送信するよう要求してはいけません。

各イベントには文字列フィールド `type` があります。プロトコルは以下のイベントを定義しています：

| `type` | 必須フィールド | 意味 |
| --- | --- | --- |
| `start_game` | なし | 対局が始まる。 |
| `start_kyoku` | `bakaze`、`kyoku`、`honba`、`kyotaku`、`oya`、`dora_marker`、`scores`、`tehais` | 局の開始。`scores` は4人の持ち点、`tehais` は4人分の配牌配列。 |
| `tsumo` | `actor`、`pai` | 対応する席で牌をツモる。 |
| `dahai` | `actor`、`pai`、`tsumogiri` | 対応する座席が牌を捨てる。`tsumogiri` はブール値。 |
| `chi` | `actor`、`target`、`pai`、`consumed` | チー。`consumed` は手牌から使用する2枚の物理牌を過不足なく含む。 |
| `pon` | `actor`、`target`、`pai`、`consumed` | ポン。`consumed` は手牌から使用する2枚の物理牌を過不足なく含む。 |
| `daiminkan` | `actor`、`target`、`pai`、`consumed` | 大明槓。`consumed` は手牌から使用する3枚の物理牌を過不足なく含む。 |
| `ankan` | `actor`、`consumed` | 暗槓。`consumed` は4枚の物理牌を過不足なく含む。 |
| `kakan` | `actor`、`pai`、`consumed` | 加槓。`pai` は加える牌、`consumed` は元のポンを構成する3枚の物理牌。 |
| `reach` | `actor` | 対応する席がリーチを宣言します。 |
| `reach_accepted` | `actor` | リーチ成立およびリーチ棒の支払い。 |
| `dora` | `dora_marker` | 新しいドラ表示牌が公開される。 |
| `hora` | `actor`、`target`、`pai` | 和了；ツモ時 `target` は `actor` に等しい。 |
| `ryukyoku` | なし | 流局。 |
| `end_kyoku` | なし | 現在の局が終了する。 |
| `end_game` | なし | 現在のゲームは終了しました。 |

`actor`、`target`、`oya` には絶対座席を使用します。`bakaze`、`dora_marker`、`pai`、`consumed`、`tehais` には「牌」の節で定義した文字列を使用します。`kyoku` は整数 `1..4`、`honba` と `kyotaku` は非負整数、`scores` は4個の整数です。イベントには精算、表示、出典などの追加フィールドを含めることができます。受信側は使用しない既知の追加フィールドを無視する必要がありますが、未知の `type` を無視して推論を続けてはいけません。

`standard` 入力では、制御対象の座席の配牌に実際の牌を使用し、他の座席の配牌は同じ枚数の `?` で表します。他の座席の未公開のツモ牌にも `?` を使用します。打牌、副露、ドラ表示牌、精算などですでに公開された牌には実際の牌を使用します。`revealed` 入力では、牌譜に記録された暗牌とツモ牌にも実際の牌を使用します。

### 候補アクション

`action-recommendation` の候補アクションはホストによってルールの検証が行われます。各アクションは `type` と `actor` を含み、`actor` はリクエストされた `controlledSeat` と等しくなければなりません。

| `type` | その他必須フィールド | 意味 |
| --- | --- | --- |
| `dahai` | `pai`、`tsumogiri` | 物理牌を1枚出す。 |
| `reach` | なし | リーチを宣言する。 |
| `chi` | `target`、`pai`、`consumed` | チー。 |
| `pon` | `target`、`pai`、`consumed` | ポン。 |
| `daiminkan` | `target`、`pai`、`consumed` | 大明槓。 |
| `ankan` | `consumed` | 暗槓。 |
| `kakan` | `pai`、`consumed` | 加槓。 |
| `hora` | `target`、`pai` | ロンまたはツモ。ツモの場合、`target` は `actor` と等しい。 |
| `ryukyoku` | なし | プレイヤーが選択できる流局を宣言する。 |
| `none` | なし | 現在の選択可能な行動を放棄する。 |

アクション中の牌と配列は、同名の対局イベントと同じ規則に従います。`none` には、見送ったアクションを示す安定した `variant` を追加できます。リーチ後に暗槓を見送る場合は `variant: "skip-ankan"` を使用し、強制されるツモ切りの `pai` と `tsumogiri: true` も指定します。

ホストは、同じ牌のツモ切りと手出し、異なる赤五の組み合わせなど、すべての物理的な候補を保持する必要があります。`candidateId` は1回のリクエスト内での対応付けにのみ使用します。エンジンはその文字列構造を解釈したり、アクションの内容から候補を独自に統合したりしてはいけません。

## 標準出力契約

| 出力契約ID | 意味 |
| --- | --- |
| `action-recommendation` | ホストが提供する合法的なアクション候補の中から1つの候補を推薦でき、各候補の評価指標を提供することも可能です。 |
| `opponent-shanten` | 他の座席の向聴分布や、聴牌の条件下での振聴または無役の確率を予測する。 |
| `opponent-deal-in-probability` | 各対戦相手に34種の牌を打ったときの制御された座席の放銃率を予測。 |
| `opponent-concealed-tile-count` | 各対戦相手の暗牌における34種の牌の数を予測する。 |
| `opponent-dora-count` | 各対戦相手のドラ数を予測する。 |
| `opponent-score` | 各対戦相手の打点予測を提供します。 |
| `wall-tile-count` | まだ公開されておらず、牌山に残っている34種の牌の枚数を予測する。 |
| `kyoku-outcome` | 現在の局が流局する確率と、4人それぞれの和了、放銃、および条件付き target 確率を予測する。 |
| `kyoku-score-delta` | 現在の局面から現在の局の精算完了までの各プレイヤーの持ち点変化を予測する。 |
| `match-placement` | 現在の対局終了時における各プレイヤーの最終順位を予測する。 |
| `match-score` | 現在の対局終了時における各プレイヤーの最終持ち点を予測する。 |

`opponent-dora-count` と `opponent-score` はそれぞれ推奨される統計的解釈を規定しています。プロトコルはエンジンにその解釈を採用することを要求せず、他の解釈のために追加の宣言フィールドを設定することもありません。ホストは出力の構造、数値範囲、および初期化時に決定された表現に従って結果を解析します。

## ハンドシェイクと出力能力

ホストがプロセスを起動した後、まず `engine.hello` を呼び出す：

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

`params.protocol` はホストがサポートする最高のプロトコルバージョンです。`params.host.id` はホストの安定 ID で、フォーマットはエンジン ID と同じです；`params.host.version` はセマンティックバージョニングを使用します。同じプロセス内で `engine.hello` を繰り返し呼び出す場合、同じアイデンティティ、能力上限、重みスロットおよびパラメータスキーマが得られなければなりません。

成功結果：

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `protocol` | はい | 協議の後の合意版です。 |
| `engine.id` | はい | `engine.json.id` と完全に一致する必要があります。 |
| `engine.name` | はい | ユーザー向けのエンジン名です。 |
| `engine.version` | はい | `engine.json.version` と完全に一致する必要があります。 |
| `outputContracts` | はい | エンジンが提供する可能性のある非空の出力宣言配列であり、重複してはなりません。 |
| `weightSlots` | はい | 重みスロット配列です；重みが不要な場合は空の配列を使用します。 |
| `devices` | はい | 空でないデバイス配列で、初期化リクエストに渡すことができるデバイスタイプを列挙します。 |
| `devices[].type` | はい | 安定デバイスIDで、小文字のASCII文字、数字、ハイフンを使用します。 |
| `devices[].title` | はい | 多言語デバイス名です。 |
| `runtimeCapabilities` | はい | プロセスの実行能力です。 |
| `optionsSchema` | はい | JSON Schema Draft 2020-12 のオブジェクトスキーマです。パラメータがない場合は、例にある空のオブジェクトスキーマを使用します。 |

各出力宣言には以下が含まれます：

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `id` | はい | 出力契約 ID。 |
| `version` | はい | 出力契約のメジャーバージョンです。 |
| `representations` | 条件必須 | 数値予測で使用できる表現。許容値は `distribution`、`expected-value`、`point-estimate` です。 |
| `supportsRevealedHands` | いいえ | 明示された入力を受け入れるかどうか、デフォルトは `false`。 |
| `metrics` | 条件必須 | `action-recommendation` が提供できる評価指標；指標がない場合は空の配列を使用。 |

`representations` は数値予測表現の出力のみで使用され、重複のない空でない配列でなければなりません。他の出力にはこのフィールドを提供してはいけません。`metrics` は `action-recommendation` のみで使用されます。

`engine.hello` はエンジンプログラムの能力上限を返します。初期化結果は、現在の重みと有効なパラメータに基づく実際の能力を返す必要があり、ハンドシェイクで宣言していない出力、表現、評価指標、明牌対応を追加してはいけません。

`runtimeCapabilities` の三つのフィールドはすべて必須のブール値です：

| フィールド | 意味 |
| --- | --- |
| `multipleSessions` | 1つの初期化インスタンスで複数の `sessionId` を分離できますか。`false` の場合、ホストは一度に1つのセッションしか使用しません。 |
| `concurrentRequests` | 複数の分析リクエストを同時に実行することを許可するかどうか。`false` の場合は、ホストが順次送信します。 |
| `cancellation` | `request.cancel` の通知を処理するかどうか。 |

ホストは、出力契約から実行能力を推測してはならない。ホストは `optionsSchema` のインターフェース拡張を認識していない場合でも、元のパラメータを保存できるが、標準の JSON Schema 検証を回避してはならない。

## 通常視点と明牌入力

分析リクエストは2つの入力モードを使用します:

| `inputMode` | 伝達内容 |
| --- | --- |
| `standard` | 制御された座席が通常知ることのできる情報には、自分の暗牌が含まれます；他の座席の暗牌は未知のままです。 |
| `revealed` | 対局記録に実際に記録された完全な手牌情報。対局記録にこれらの情報が確かにある場合にのみ使用可能。 |

すべての出力は `standard` を受け入れなければなりません。`supportsRevealedHands: true` はその出力が `revealed` も受け入れることを示します。

インターフェースで明牌が有効でない場合、ホストは常に `standard` を使用します。インターフェースで明牌が有効な場合、次の条件がすべて満たされた場合にのみ出力は `revealed` を使用します：

- 初期化結果は、この出力が明牌入力をサポートしていることを宣言します；
- 現在の牌譜に完全な明牌情報が記録されている。

いずれの条件も満たさない場合、ホストは引き続きその出力に `standard` データを送信します。同じエンジンの異なる出力は、異なる明牌サポートを持つことができます。異なる入力モードを必要とする出力は、同じ `analysis.run` リクエストにまとめてはいけません。

## 重みスロット

エンジンは `engine.hello` の中で `weightSlots` を通じて、ユーザーが設定する必要のある重みファイルを宣言します。1つのエンジンは複数のスロットを宣言することも、重みを必要としないこともできます。各スロットは1つのファイルを受け取ります。複数のファイルが必要な場合は、複数のスロットを宣言します。

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `id` | はい | エンジン内部の安定スロットIDです。小文字のASCII文字、数字、ハイフンを使用し、長さは `1..64` です。 |
| `title` | はい | 多言語スロットタイトルです。 |
| `description` | いいえ | 多言語スロットの説明。 |
| `formats` | はい | 空でない配列で、スロットが受け入れる重みの形式を列挙します。 |
| `formats[].id` | はい | エンジンによって定義された安定したフォーマット ID です。 |
| `formats[].extensions` | はい | 空でない拡張子の配列、例えば `.onnx`、`.pth`。ファイル選択のヒントのみに使用されます。 |
| `requiredForOutputs` | はい | 空でない出力参照配列です。いずれかの出力を有効にする場合、このスロットを提供する必要があります。 |

1つの出力は複数のスロットを要求することができ、1つのスロットも複数の出力で共有することができます。ホストは、現在そのエンジンに設定された出力に基づいて、どのスロットでファイルを選択する必要があるかを決定します。必要ないスロットは淡く表示することができます。拡張子は、エンジンによるファイルの内容および構造の検証を置き換えることはできません。

## 初期化

`engine.initialize` 現在の設定をロードします。プロセスが起動した後は、自らデフォルトの重みを選択してはいけません；初期化が成功する前に `analysis.run` を受け入れてはいけません。再度初期化すると、まず現在のタスクを終了し、すべてのセッションをクリアした後、新しい設定で以前の設定を置き換えます。

### 初期化リクエスト

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `enabledOutputs` | はい | 今回の読み込みで提供する必要がある空でない出力参照配列であり、重複してはいけません。 |
| `weights` | はい | 現在有効な出力要求の重みスロットです。必須スロットがない場合は空の配列を使用します。 |
| `weights[].slotId` | はい | `engine.hello.weightSlots[].id` の現在必要なスロットです。 |
| `weights[].format` | はい | 現在のスロットで宣言されたフォーマットIDです。 |
| `weights[].path` | はい | ホストが解析した後のローカル絶対パスです。 |
| `device` | はい | デバイスの選択です；`device.type` は `engine.hello.devices` から来る必要があります。 |
| `options` | はい | エンジンの宣言したオプション構造体を検証するパラメーターオブジェクトです。 |

リクエストは、現在必要な各スロットごとに1つのファイルを提供する必要があり、不明なスロット、重複したスロット、または現在不要なスロットを含めてはいけません。エンジンはファイルの形式と内容を検証する必要があり、拡張子だけに依存してはいけません。

ドキュメントの要約は、ホストが結果の出所を識別する必要があるときに計算され、初期化リクエストを通じてエンジンに代わりに検証やエコーを要求することはありません。

### 初期化結果

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

`outputs` は、リクエスト内の各出力に対して、同じ ID、同じバージョンの結果を 1つだけ提供する必要があり、配列の順序にはプロトコル上の意味はありません。初期化結果は、手元で宣言された表現、評価指標、または既知能力を絞り込むことはできますが、能力を増やしてはいけません。いずれのリクエスト出力も提供できない場合、初期化は全体として失敗とみなし、出力を黙って削除してはいけません。

数値予測において、初期化結果の中の `representations` は、現在の設定後に毎回結果を返す際に必ず使用しなければならない固定表示です。アクション推薦においては、`metrics`、`primaryMetricId`、および `recommendationMetricId` のルールは「評価指標の宣言」を参照してください。ホストはこれらの固定された宣言に基づいてインターフェースを配置します。単一の結果にデータが欠けている場合でもインターフェース構造を変更してはいけません。

`device` はエンジンが実際に使用するデバイスで、ハンドシェイク宣言から取得する必要があります。`effectiveOptions` はハンドシェイク中の `optionsSchema` を経由し、アプリケーションのデフォルト値を適用した最終パラメータを含む必要があります。出力、重みファイル、デバイス、またはパラメータを変更した場合は、再初期化が必要です。

## 分析リクエスト

エンジンは `analysis.run` を使用して業務リクエストを受信します：

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `sessionId` | はい | 増分ステート分離キーです。異なるゲーム、制御された座席、または入力モードでは共有してはいけません。 |
| `controlledSeat` | はい | 制御対象の絶対座席。整数 `0..3`。 |
| `inputMode` | はい | `standard` または能力協議を経た `revealed` です。 |
| `events` | はい | 現在の位置までの、入力パターンに一致する標準イベント配列です。 |
| `outputs` | はい | 今回のリクエストの非空出力配列で、重複してはいけません。 |
| `outputs[].id` | はい | 初期化済みの出力契約 ID です。 |
| `outputs[].version` | はい | 初期化済みの出力契約メジャーバージョンです。 |
| `outputs[].parameters` | はい | 出力契約定義のリクエストパラメータであり、専用パラメータがない場合は `{}` を使用します。 |

同一リクエスト内のすべての出力は、同じ履歴、制御された座席、および入力パターンを使用します。初期化済みエンジン設定に渡された出力のみがマージ可能です。エンジンはリクエスト内のすべての出力を返し、追加の出力を増やしてはなりません。いずれかの出力が失敗した場合、JSON-RPCリクエスト全体がエラーを返し、部分的な結果は返されません。

同一 `sessionId` の後続リクエストは履歴を拡張、巻き戻し、または書き換えることができます。エンジンは内部的に不変の共通プレフィックスを再利用することができますが、今回の完全な `events` を基準とし、巻き戻しや分岐の後に一致しなくなった状態は破棄しなければなりません。歴史を再利用するかどうか、およびその方法はエンジンの実装に属し、ホストに宣言する必要はありません。ホストはリクエスト ID と自身の実行世代を使用して結果が現在の位置に依然として適用可能かどうかを判断し、古い結果が現在のデータを上書きしてはなりません。

分析結果：

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `outputs` | はい | リクエストの出力参照とちょうど一対一で対応しています；配列の順序にはプロトコル上の意味はありません。 |
| `outputs[].data` | はい | 対応する出力契約定義の結果オブジェクトです。 |
| `timing` | いいえ | 今回のリクエストの所要時間；`totalMs` は非負の有限な数値で、単位はミリ秒です。 |

リクエストと結果は JSON-RPC の `id` に関連付けられています。結果はセッション、履歴、入力モード、またはソースの指紋を重複して表示しません。

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `players` | はい | 「座席」セクションで定義される他の座席です。 |
| `players[].seat` | はい | 対応するプレイヤーの絶対座席です。 |
| `players[].shanten` | はい | 整数 `0..6` を取る確率分布である；記載されていない値の確率は `0` で、`0` は聴牌を表す。 |
| `players[].furitenOrNoYaku` | はい | `P(振聴または役なし \| 0シャンテン)`。 |

`furitenOrNoYaku` は `opponent-shanten` に含まれる値であり、独立した出力契約ではありません。ホストが聴牌表示を分ける場合は、次のように計算できます。

```text
ロン可能な聴牌 = P(0シャンテン) × (1 - furitenOrNoYaku)
振聴または役なし = P(0シャンテン) × furitenOrNoYaku
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

`players` は「座席」章で定義された他の座席を使用します。各 `tiles` は正確に34種類の牌を含める必要があり、値は制御された座席がその牌を打ったときに対応するプレイヤーがロンする確率を表します。例に示した牌の種類は抜粋であり、実際の結果では省略してはいけません。

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
      }
    }
  ]
}
```

`players` には「座席」節で定義された他の座席を使用します。各 `tiles` には34種の牌を過不足なく含めます。離散分布を使用する場合、値は整数 `0..4` とし、記載されていない値の確率は `0` とします。`expectedValue` または `pointEstimate` を使用する場合、値は `[0, 4]` とします。ホストは分布から「1枚以上持っている」確率 `1 - P(0)` を導出できます。

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
  }
}
```

出力は、現在のイベントが完了した時点で、まだ公開されず牌山に残っている各種の牌の枚数を表します。未公開牌山全体を `all-unrevealed-wall` として扱い、ツモ山と王牌を区別するフィールドは設けません。

`tiles` には34種の牌を過不足なく含める必要があります。離散分布を使用する場合、値は整数 `0..4` とし、記載されていない値の確率は `0` とします。`expectedValue` または `pointEstimate` を使用する場合、値は `[0, 4]` とします。

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

推奨される統計的な解釈は、対象のプレイヤーが現在の局で最終的に和了することを条件として、精算時に成立するドラの総数を予測するものです。ロンとツモは区別しません。通常のドラと赤ドラを含み、リーチ後の和了では精算時に開かれる裏ドラも含みます。まだ確定していないドラ表示牌も予測の対象です。

この解釈では、現在確定しているドラの枚数を表すものではなく、最終的な和了確率も掛けません。

プロトコルが要求するのは、`players` が「座席」の節に従うこと、離散値が非負整数または `N+` 形式の文字列であること、`expectedValue` と `pointEstimate` が `0` 以上であることだけです。エンジンが上記の統計的解釈を採用する必要はありません。`N` は先頭に不要なゼロを付けない非負の10進整数で、`N+` は `N` 以上を表します。1つの分布で使用できる `N+` は1つだけで、`N` 以上の数値を別に含めることはできません。この出力を別の意味のドラ数予測に使用しても、ホストは同じデータ構造として解析します。

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

推奨される統計的な解釈は、対象のプレイヤーが現在の局で最終的に和了することを条件として、その手牌が精算時に生む打点を予測するものです。ロンとツモは区別しません。本場による加点、リーチ棒、供託などの場の収入は含めません。

この解釈では、ロンの打点は放銃者がその手牌に対して支払う点数、ツモの打点は他の3人がその手牌に対して支払う点数の合計です。離散分布には実際の点数区分を使用します。`expectedValue` と `pointEstimate` は、その区分の間の値を取ることもできます。最終的な和了確率は掛けません。

プロトコルが要求するのは、`players` が「座席」の節に従うこと、離散値が非負整数の点数であること、`expectedValue` と `pointEstimate` が `0` 以上であることだけです。エンジンが上記の統計的解釈を採用する必要はありません。この出力を別の意味の打点予測に使用しても、ホストは同じデータ構造として解析します。

## `kyoku-outcome`

```json
{
  "drawProbability": 0.25,
  "players": [
    {
      "seat": 0,
      "winProbability": 0.30,
      "dealInProbability": 0.06,
      "targetGivenWin": [
        {"seat": 0, "probability": 0.42},
        {"seat": 1, "probability": 0.18},
        {"seat": 2, "probability": 0.21},
        {"seat": 3, "probability": 0.19}
      ]
    }
  ]
}
```

| フィールド | 必須 | 形式と意味 |
| --- | --- | --- |
| `drawProbability` | はい | `P(現在の局が流局する)`。荒牌流局と途中流局を含みます。 |
| `players` | はい | 絶対座席 `0..3` をそれぞれ1回ずつ含む。 |
| `players[].seat` | はい | プレイヤーの絶対座席。 |
| `players[].winProbability` | はい | `P(そのプレイヤーが現在の局で和了する)`。 |
| `players[].dealInProbability` | はい | `P(そのプレイヤーが現在の局で放銃する)`。 |
| `players[].targetGivenWin` | はい | 条件付き確率分布 `P(target = 座席 \| そのプレイヤーが和了する)`。絶対座席 `0..3` をそれぞれ1回ずつ含みます。ツモでは `target` と和了者が一致します。 |

`1 - drawProbability` は、少なくとも1人が和了する確率です。ダブロンやトリプルロンでは、複数の `winProbability` が同時に成立します。

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

`players` は絶対座席 `0..3` をそれぞれ1回ずつ含みます。`prediction` は「数値予測」コンテナを使用し、最後の入力イベント後の持ち点から、現在の局の精算後までの持ち点変化を表します。入力履歴に反映済みの変化は重ねて計上しません。

離散分布の値は整数点とし、負の値も使用できます。

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

`players` は絶対座席 `0..3` をそれぞれ1回ずつ含みます。`prediction` は「数値予測」コンテナを使用し、現在の対局が終了したときの順位を表します。

離散分布の値は整数 `1..4`、`expectedValue` と `pointEstimate` は `[1, 4]` とします。

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

`players` は絶対座席 `0..3` をそれぞれ1回ずつ含みます。`prediction` は「数値予測」コンテナを使用し、現在の対局が終了したときの持ち点を表します。

離散分布の値は整数点とし、負の値も使用できます。

## `action-recommendation`

### リクエストパラメータ

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

| フィールド | 必須 | 形式と意味 |
| --- | --- | --- |
| `candidates` | はい | ホストがすでにルール検証を完了した、空でない合法的なアクション候補配列です。 |
| `candidates[].candidateId` | はい | 今回のリクエスト内で唯一の不透明な関連 ID です。 |
| `candidates[].action` | はい | 規範動作対象です。 |

### 評価指標の宣言

アクション推奨は、任意の数の評価指標を宣言することができます。指標は `engine.hello` によって能力の上限が一覧され、初期化結果によって現在の構成で使用される固定の集合と順序が決定されます。

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

| フィールド | 必須 | フォーマットと意味 |
| --- | --- | --- |
| `id` | はい | エンジンが定義した安定した指標 ID です。小文字の ASCII 文字、数字、ハイフンを使用し、長さは `1..64` です。 |
| `title` | はい | 多言語の短いタイトルです。 |
| `description` | いいえ | 多言語の説明。 |
| `format` | はい | `number`、`percentage`、または `points` で、ホストの数値をフォーマットするために使用されます。 |
| `fractionDigits` | いいえ | `0..12` の整数で、表示時に保持する小数点以下の桁数を指定します。`percentage` はパーセントに換算した後、この精度が適用されます。 |
| `preferredDirection` | はい | `higher`、`lower`、または `none` で、数値の好ましい方向を示します。 |

`format` は表示形式のみを規定し、指標の統計的意味は規定しません。指標の意味は、安定した ID、タイトル、説明によって示されます。同じエンジンの主要バージョン内では、同じ指標 ID の形式、方向、意味を変更してはいけません。`fractionDigits` は表示にのみ影響し、エンジンが返す値を変更しません。提供されない場合、ホストは通常の数値形式を使用し、指標 ID に基づいて小数桁数を推測してはいけません。

初期化の結果は `primaryMetricId` を提供でき、その値は現在の `metrics` の中のいずれかの ID でなければなりません。ホストは主要な指標で詳細を並べ替えて評価できます。主要な指標がない場合、ホストは指標 ID に基づいて並べ替えに使用する指標を推測してはなりません。

初期化の結果は `recommendationMetricId` を提供でき、その値は現在の `metrics` 内の `format` が `percentage`、`preferredDirection` が `higher` の指標を指す必要があります。この指標の `[0, 1]` の数値は、各有効なアクションの相対的な推奨強度を直接示し、ホストはこれに基づいて推奨バーを描画できます。エンジンは Q 値、期待得点、またはその他の内部評価を推奨強度に換算する責任があります。ホストは指標 ID に基づいて推奨強度を推測したり、宣言されていない指標を勝手に推奨バーとして正規化したりしてはいけません。`recommendationMetricId` がない場合、ホストは `bestCandidateId` のみを表示し、評価指標に基づいて推奨バーを描画しません。

`bestCandidateId` は常にエンジンが最終的に選択する推奨アクションです。`primaryMetricId` と `recommendationMetricId` は評価の詳細と推奨の強度の表示のみを制御し、この選択を覆すために使用してはなりません。

### 結果

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

`bestCandidateId` はリクエスト候補の一つでなければなりません。エンジンがいかなる評価指標も提供しない場合でも、`bestCandidateId` を提供する必要があります。

現在設定されている `metrics` が空の場合、結果は `candidates` を提供してはいけません。`metrics` が空でない場合、結果は `candidates` を提供する必要があり、リクエスト内のすべての候補を正確にカバーしなければなりません。各候補の `metrics` は、初期化時に宣言されたすべての指標 ID を正確に含まなければなりません；値は指標形式に適合する有限の数値であり、当該候補の指標値がまだない場合は `null` を使用します。単一の値である `null` は、ホストがすでに確定した指標列やインターフェースのレイアウトを変更しません。

`percentage` 指標の非空の値は `[0, 1]` に位置する必要があります。プロトコルは異なる候補の `percentage` 数値の合計が `1` であることを要求せず、`preferredDirection` に基づいて `bestCandidateId` を検証することもありません。推奨される動作はエンジンによって直接決定されます。

## セッション、状態、終了

エンジンは次の状態を使用します：

| 状態 | 意味 |
| --- | --- |
| `starting` | プロセスは開始されましたが、まだハンドシェイクが完了していません。 |
| `uninitialized` | ハンドシェイクは完了しましたが、まだ初期化されていません。 |
| `loading` | 設定を読み込み中または置き換え中。 |
| `ready` | 分析リクエストを受け付けることができます。 |
| `busy` | 分析を実行中；並行作業がサポートされていない場合、新しい分析リクエストを受け付けてはいけません。 |
| `error` | 現在の設定は使用できません。再初期化すると回復できます。 |
| `stopping` | 閉じています。 |

状態が変化したとき、エンジンは `engine.status` 通知を送信します：

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

`state` 必須；`message` と `error` は任意。`message` は表示のみに使用され、ホストが必ず解析する必要のあるデータを搭載してはいけません。

`engine.getStatus` は同期回復と診断に使用され、成功結果は次の通りです：

```json
{
  "state": "ready",
  "activeTasks": 0,
  "queuedTasks": 0,
  "lastError": null
}
```

`activeTasks` と `queuedTasks` は非負整数です。ホストは高頻度のポーリングに依存してはなりません。正常な変化は通知によってプッシュされます。

エンジンが解析リクエストを開始または終了する際に `task.status` を送信できます：

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

タスクの状態で許可される値は `queued`、`running`、`completed`、`canceled`、`error` です。通知は元のリクエストの JSON-RPC の応答を置き換えるものではありません。

`session.reset` と `session.close` は両方とも受信します：

```json
{
  "sessionId": "game-17:seat-0:standard"
}
```

両者の成功結果は `{"ok": true}` です。`session.reset` は指定されたセッションの増分状態をクリアしますが、その後同じ ID を引き続き使用することを許可します；`session.close` はそのセッションを解放します。未知のセッションも成功と見なされ、他のセッションに影響を与えてはなりません。

キャンセルをサポートするエンジンが `request.cancel` 通知を受信しました：

```json
{
  "jsonrpc": "2.0",
  "method": "request.cancel",
  "params": {
    "requestId": "host-41"
  }
}
```

キューに並んでいるリクエストは直ちにキャンセルされるべきである。実行中のリクエストは安全なポイントでキャンセル可能である。正常にキャンセルされた場合、元のリクエストは`REQUEST_CANCELED`エラーを返す。キャンセルがサポートされていない場合やタイムリーに中断できない場合、エンジンは元のリクエストを完了させることができ、ホストはすでに古くなった結果を破棄する責任がある。

`engine.shutdown` は空のオブジェクト `{}` を受信し、まず `{"ok": true}` を返し、その後 `stopping` の状態を送信して正常に終了します。ホストはタイムアウト、通信の破損、またはプロセスの応答がない場合に、直接プロセスを終了することができます。

## エラー

プロトコルエラーにより JSON-RPC エラー応答が使用されました：

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

`message` は短いプレーンテキストです。`data.errorCode` はホストが判断できる安定した ASCII 文字列です；`data.recoverable` はプロセスを再起動せずに新しいリクエストで回復できるかを示します。追加の診断データは `data` にのみ置くことができます。

JSON-RPC 標準の数値エラーコード `-32700`、`-32600`、`-32601`、`-32602`、および `-32603` は、それぞれ解析エラー、無効なリクエスト、不明なメソッド、無効なパラメータ、および内部エラーを示します。エンジンの業務エラーには `-32000` を使用し、以下の `errorCode` を使用します：

| `errorCode` | 意味 |
| --- | --- |
| `PROTOCOL_MISMATCH` | プロトコル名またはメジャーバージョンが互換性がありません。 |
| `ENGINE_NOT_INITIALIZED` | まだ初期化に成功していません。 |
| `INITIALIZATION_FAILED` | 初期化が完了できませんでした。 |
| `INVALID_WEIGHT` | 重みが欠落している、フォーマットが間違っている、または内容が互換性がありません。 |
| `UNSUPPORTED_OUTPUT` | 出力不明、未有効化、または現在の入力モードはサポートされていません。 |
| `INVALID_HISTORY` | ゲームイベントの欠落、順序の誤り、または内容が不正です。 |
| `INVALID_CANDIDATES` | アクション候補が空、重複、または不正です。 |
| `INVALID_MODEL_OUTPUT` | モデルが欠損、非有限、または出力契約に準拠しないデータを生成しました。 |
| `REQUEST_CANCELED` | リクエストはキャンセルされました。 |
| `ENGINE_BUSY` | 現在の稼働能力では新しいタスクを受け付けることができません。 |

分析リクエストのいずれかの出力が失敗した場合、リクエスト全体がエラーを返し、一部のビジネス結果をエラー応答に含めることはできません。

## セキュリティ境界

プロトコルの互換性はエンジンの信頼性を意味するものではありません。ホストはエンジンプログラム、マニフェスト、テキスト、パス、およびすべてのプロセス出力を信頼できない入力として扱い、メッセージのサイズと待機時間を制限し、パッケージパスを検証し、マニフェストの内容を Shell 経由で実行してはなりません。ホストはエンジンを独立したプロセスで実行し、通信の破損、タイムアウト、または異常終了時にそれを終了できるようにする必要があります。

## ホストが生成する結果ソース識別子

プロトコルはエンジンにソースのフィンガープリントを生成または返すことを要求しません。結果のソースをキャッシュ、比較、または表示する必要がある場合、ホストは自身が実際に起動し、渡されたコンテンツに基づいて安定した識別子を生成します。識別子は結果に影響を与える可能性のあるすべてのデータをカバーする必要があり、少なくとも次を含む必要があります:

- 実行に影響を与えるエンジンのパッケージファイルや実行可能ファイルの要約；
- 現在使用されているすべての重みファイルの概要；
- 実際の装置の種類、有効なパラメータ、および数値精度に影響を与える動作設定；
- 契約IDとバージョンを出力する；
- 初期化結果で確定した表現、指標ID、指標形式、および志向方向。
- 結果の数値を変更するホストの後処理バージョン。

ホストは各出力ごとにソース識別子を生成します。同じエンジン設定で複数の出力を提供する場合、共有されるプログラム、重み、パラメータの部分は再利用可能です。ローカルファイルパス、多言語タイトルおよび説明は安定した識別子には含めてはいけません。プロセスの再起動回数、リクエスト番号などの一時的な状態は、別個の実行版管理で扱い、安定したソース識別子には含まれません。プロトコルは、ホスト内部の識別子のフィールド名、保存場所、またはハッシュアルゴリズムを規定していません。

</div>
