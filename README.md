# finAnalist — 出典付き投資テーマ記述パイプライン

入力テーマのニュースと、利用者が明示した市場シンボルの企業・財務・価格データを取得し、記述レポートへまとめるPythonプロトタイプです。

**企業名の自動推測、センチメント、DCF、将来予測、異常値のAI判定、最適投資戦略の提案は行いません。**

## 監査で確認した問題

過去実装は次の状態でした。

- `main.py`が引数必須の`NewsAnalyzer`を引数なしで生成し、起動時に失敗
- 廃止済みの`text-davinci-002`と旧Claude completion APIへ依存
- ニュースAPIキーをURLへ埋め込み
- HTTPタイムアウトなし
- Alpha Vantage、Finnhub、Polygonの異なるJSONを同じ辞書へ上書き結合
- 先行APIが失敗すると未初期化辞書を`.update()`して例外
- Finnhubの取得期間が固定Unix時刻、Polygonの期間が固定日付
- 企業分析が`分析結果のダミー`を返す
- 財務分析と異常検知がダミー文字列を返す
- 投資シミュレーションと評価がダミー文字列を返す
- レポートが未計算センチメントを実結果として表示

## 現在の処理

```text
テーマと検証済み市場シンボルを明示
  → NewsAPIで記事メタデータを取得
  → 記事数・媒体・日付・欠損を記述集計
  → Alpha Vantage OVERVIEWを出典別に保存
  → 公開フィールドを企業情報・財務指標へ正規化
  → Alpha Vantage TIME_SERIES_DAILYのraw closeを取得
  → 単純買持ちの価格リターン・ボラティリティ・DDを記述
  → MarkdownレポートとCSVを保存
```

NewsAPIの`/v2/everything`を記事探索に使い、APIキーは`X-Api-Key`ヘッダーで送信します。Alpha Vantageは`OVERVIEW`と`TIME_SERIES_DAILY`だけを使用し、プロバイダーを跨いだJSON結合は行いません。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export NEWS_API_KEY="..."
export ALPHA_VANTAGE_API_KEY="..."
```

## 実行

企業はニュース本文から推測せず、市場シンボルを明示します。

```bash
python main.py \
  "semiconductor manufacturing equipment" \
  --symbol ASML \
  --symbol AMAT
```

## 現在の出力

```text
data/news_analysis/articles.json
  - 記事タイトル、媒体、公開日時、URL、説明
  - source_counts
  - sentiment_status: not_computed
  - company_extraction_status: not_computed

data/company_analysis/results.csv
  - 企業名、取引所、通貨、国、セクター、業種等
data/financial_analysis/results.csv
  - Alpha Vantage OVERVIEWの数値フィールド
data/financial_analysis/quality_flags.csv
  - 欠損値・負値等の決定論的品質フラグ
data/simulations/results.csv
  - raw closeの買持ち記述統計
reports/investment_report.md
```

## 価格バックテストの意味

`TIME_SERIES_DAILY`の`4. close`を使用します。

- raw closeであり、配当を含みません
- 株式分割調整済みとは扱いません
- 総合リターンではありません
- 手数料、税、スプレッド、約定を含みません
- 価格リターン、年率ボラティリティ、最大ドローダウンの記述だけです
- `descriptive_not_recommendation`と`no_strategy_optimization_performed`を保存します

## 停止している機能

- Twitter/X取得 — 認証、レート制限、個人情報、出典契約が未実装
- 企業名自動抽出 — 評価済みEntity Linkingがない
- センチメント — ラベル付き評価データ、モデル版、棄却規則がない
- 可視化 — 出典、単位、as-of、グラフ意味検証が未実装
- 企業価値評価・予測・推奨 — 根拠とOOS検証がない

これらを呼ぶとダミー結果を返さず、`NotImplementedError`で停止します。

## テスト

```bash
python -m unittest discover -s tests -v
```

確認項目:

- NewsAPIキーをURLではなくヘッダーで送る
- APIのレート制限・エラーpayloadを成功扱いしない
- 企業・財務分析にダミー文字列が混入しない
- 未実装センチメントが偽結果を返さない
- raw closeバックテストが非推奨・配当なしと表示される

本プロジェクトは投資助言や売買推奨ではありません。

**README最終監査:** 2026-08-02
