# finAnalist — 投資テーマ分析パイプラインの試作

**リポジトリ:** https://github.com/KAFKA2306/finAnalist

入力した投資テーマから関連ニュースと企業候補を収集し、定性分析、財務分析、レポート、簡易シミュレーションへ渡すPythonパイプラインの試作です。

READMEに以前記載されていた多数のAPI連携や「最適戦略の提案」は、すべてが現在利用可能・契約済み・検証済みであることを確認できません。実際に動作する範囲は、`main.py`と`lib/`配下の現在の実装を正としてください。

## 現在の処理フロー

`main.py`は次のクラスを順番に呼び出します。

```text
投資テーマを入力
  → DataCollectorでニュース・SNS候補を取得
  → NewsAnalyzerで企業候補とセンチメントを生成
  → DataCollectorで財務・株価候補を取得
  → CompanyAnalyzerで企業分析
  → FinancialAnalyzerで財務指標・異常候補を生成
  → ReportGeneratorでMarkdownと図を出力
  → InvestmentSimulatorで戦略候補を評価
```

## 主なモジュール

| ファイル | 役割 |
| --- | --- |
| `main.py` | 全処理の呼び出し |
| `lib/data_collection.py` | ニュース、SNS、財務、株価の取得 |
| `lib/news_analysis.py` | 関連企業抽出、センチメント分析 |
| `lib/company_analysis.py` | 企業別の定性・定量整理 |
| `lib/financial_analysis.py` | 財務指標と異常候補の計算 |
| `lib/report_generation.py` | Markdown・可視化出力 |
| `lib/simulation.py` | 過去データを使ったシミュレーション |

## 出力先

```text
data/news_analysis/
data/company_analysis/
data/financial_analysis/
data/simulations/
reports/
```

各出力には、対象期間、取得日時、データ源、使用モデル、設定を追加する必要があります。

## セットアップ

```bash
git clone https://github.com/KAFKA2306/finAnalist.git
cd finAnalist
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windowsでは仮想環境の有効化コマンドを環境に合わせて変更してください。

## 実行

```bash
python main.py
```

入力例:

```text
次世代電池の技術進展と上場企業
```

投資判断を直接尋ねるテーマより、技術、需要、供給、競争、財務指標などの検証可能な問いへ分解する方が安全です。

## APIキー

コードが要求する場合は、環境変数またはGit管理外の設定ファイルへ保存します。

想定されていたサービス例:

- NewsAPI
- FRED
- Alpha Vantage
- Finnhub
- Polygon
- Financial Modeling Prep
- SimFin
- OpenAI互換API
- Anthropic API
- SNS API
- Discord

すべてを契約する必要があるとは限りません。現在のコードが実際にimport・呼び出しているサービスだけを設定してください。

APIキーを`config.ini`へ平文保存する場合は、ファイルを`.gitignore`へ追加し、既に漏えいしていないか履歴も確認してください。

## 分析品質の原則

### ニュース

- 発生日と記事公開日を分ける
- 元記事と転載を重複排除する
- 企業IR・規制開示を優先する
- LLMのセンチメントを事実として扱わない

### 財務

- 年次、四半期、時点値を混ぜない
- 通貨、単位、連結・単体を保存する
- 実績、会社予想、コンセンサス、独自推計を分ける
- PERやPBRの株価基準日を記録する

### シミュレーション

- 未来情報を入力へ含めない
- 上場廃止と銘柄入替を考慮する
- 手数料、スプレッド、税を明示する
- インサンプルとOOSを分ける
- LLMに「最適戦略」を決めさせない

## セキュリティ

- 外部記事本文を無制限に保存しない
- SNS投稿の個人情報を保存しない
- APIキーをログへ出さない
- Discordへ機密レポートを自動投稿しない
- 外部入力をプロンプトやシェルへ直接渡さない

## 現在の位置づけ

本リポジトリは、複数の金融情報処理を一つの流れへまとめる初期プロトタイプです。データ取得の完全性、分析精度、バックテストの再現性は未保証です。

本プロジェクトは投資助言や売買推奨ではありません。

**README最終監査:** 2026-08-01
