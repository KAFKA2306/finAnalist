# 投資テーマ分析ツール

## 概要

本ツールは、ユーザーが入力した投資テーマに関連する企業群を自動で特定し、各社の事業内容や業績見通し、バリュエーション等を分析することで、投資判断の示唆を提供します。データ収集の自動化と分析アルゴリズムの高度化により、より正確で網羅的な分析を実現します。

## 機能

### データ収集の自動化と定期更新

- NewsAPI、FRED API、Financial Modeling Prep API、SIMFIN APIを用いて、各種データベースからのデータ収集を自動化し、定期的に最新データを取得
- Alpha Vantage API、Finnhub API、Polygon APIを用いて、株価データや財務データを自動収集

### ニュースデータ分析

- NewsAPIから関連記事を収集し、OpenAI APIやClaude APIを用いて、自然言語処理によるセンチメント分析を実施
- Twitter APIを用いて、投資テーマに関連するツイートを収集し、ソーシャルメディア上の評判を分析
- ニュースデータ分析結果は `data/news_analysis` フォルダにJSON形式で保存し、次回分析時にも読み込む
- ニュース記事の重要度をスコア化し、重要度の高い記事を優先的に分析・表示することで、情報の取捨選択を支援

### 企業分析

- 企業の事業内容や業績見通し、競合環境等の情報を収集
- Claude APIを用いて、収集した情報から定性情報を抽出・要約
- Alpha Vantage API、Finnhub API、Polygon APIから取得した財務諸表データに基づいて、売上高、利益、成長率等を分析
- 企業分析結果は `data/company_analysis` フォルダに企業ごとにCSV形式で保存し、次回分析時にも読み込む
- 企業情報のバージョン管理を行い、変更履歴を追跡可能にすることで、分析の再現性を確保

### 財務分析

- Alpha Vantage API、Finnhub API、Polygon APIから取得した財務諸表データに基づいて、PER、PBR、ROE等を算出
- Financial Modeling Prep APIとSIMFIN APIを用いて、業種平均や類似企業とのバリュエーション比較分析を実施
- 将来の業績予想に基づいて、DCF法等の割引現在価値計算を行い、企業価値を評価
- OpenAI APIを活用し、財務データからの異常値検知を高度化
- 財務分析結果は `data/financial_analysis` フォルダに企業ごとにCSV形式で保存し、次回分析時にも読み込む
- 財務指標の時系列変化をグラフ化し、トレンドを視覚的に把握しやすくすることで、分析の深度を向上

### レポート生成

- 分析結果をMarkdown形式で `reports` フォルダに出力
- グラフやチャートを活用し、分析結果をビジュアルに分かりやすく表現
- HTMLとJavaScriptを用いてインタラクティブな形式で提供し、ユーザーが関心のある項目を掘り下げて確認可能
- 投資判断の示唆とリスク提示
- レポートのテンプレートを柔軟に設定できるようにし、ユーザーの好みに合わせたカスタマイズを可能に

### 投資シミュレーション

- Alpha Vantage API、Finnhub API、Polygon APIから取得した過去の株価データを用いて、投資戦略のバックテストを実施
- OpenAI APIを活用し、リスクとリターンを評価し、最適な投資戦略を提案
- シミュレーション結果は `data/simulations` フォルダにCSV形式で保存
- シミュレーション条件を柔軟に設定できるようにし、様々なシナリオを検討可能に

## 必要な環境

- NewsAPI、Claude API、Alpha Vantage API、Finnhub API、Polygon API、OpenAI API、Twitter API、FRED API、Financial Modeling Prep API、SIMFIN API、Discord APIの利用登録とAPIキーの取得

## フォルダ構成

```
investment_theme_analysis/
│
├── config/
│   └── config.ini
│
├── data/
│   ├── company_analysis/
│   │   └── {company_name}.csv
│   ├── financial_analysis/
│   │   └── {company_name}.csv
│   ├── news_analysis/
│   │   └── {date}.json
│   └── simulations/
│       └── {strategy_name}.csv
│
├── lib/
│   ├── data_collection.py
│   ├── news_analysis.py
│   ├── company_analysis.py
│   ├── financial_analysis.py
│   ├── report_generation.py
│   └── simulation.py
│
├── logs/
│   └── {date}.log
│
├── reports/
│   └── {date}_report.md
│
├── templates/
│   ├── report_template.md
│   └── graph_template.html
│
├── main.py
├── requirements.txt
```

- `config/config.ini`: 各種APIキーや設定情報を記述
- `data/`: 分析結果やシミュレーション結果を保存するフォルダ
  - `company_analysis/`: 企業分析結果をCSV形式で保存
  - `financial_analysis/`: 財務分析結果をCSV形式で保存
  - `news_analysis/`: ニュース分析結果をJSON形式で保存
  - `simulations/`: 投資シミュレーション結果をCSV形式で保存
- `lib/`: 各機能を担当するPythonモジュールを格納
  - `data_collection.py`: データ収集の自動化
  - `news_analysis.py`: ニュースデータ分析
  - `company_analysis.py`: 企業分析
  - `financial_analysis.py`: 財務分析
  - `report_generation.py`: レポート生成
  - `simulation.py`: 投資シミュレーション
- `logs/`: 実行ログを記録するフォルダ
- `reports/`: 生成されたレポートをMarkdown形式で保存
- `templates/`: レポートやグラフのテンプレートを格納
- `main.py`: メイン実行モジュール
- `requirements.txt`: 必要なPythonパッケージを記述

## 使い方

1. `config/config.ini` ファイルに、各APIキー等を設定
2. 仮想環境を構築し、必要なパッケージをインストール
   
   ```
   cd .\finAnalist
   pip install -r .\requirements.txt
   ```

3. `main.py` を実行し、投資テーマを入力
   
   ```
   python main.py
   ```
   
   例: 「次世代電池の開発動向と関連企業への投資」

4. レポートが `reports/` フォルダにMarkdown形式で出力され、Discordで共有されます。
5. レポート内のインタラクティブなグラフを用いて、詳細な分析結果を確認します。
6. 投資シミュレーション結果を参考に、最適な投資戦略を検討します。

## 分析の流れ

1. ニュース記事やツイートなどのテキストデータを収集（NewsAPI、Twitter API）
2. OpenAI APIやClaude APIを用いて、収集したテキストデータからセンチメント分析や関連企業の抽出を実施
3. 抽出された企業リストを基に、財務データや株価データを収集（Alpha Vantage API、Finnhub API、Polygon API、FRED API、Financial Modeling Prep API、SIMFIN API）
4. 収集したデータを基に、企業分析、財務分析、バリュエーション分析を実施
5. OpenAI APIを用いて、財務データからの異常値検知を実施
6. 分析結果を総合し、グラフや図表を交えたインタラクティブなレポートを生成
7. Alpha Vantage API、Finnhub API、Polygon APIから取得した過去の株価データを用いて、投資シミュレーションを実行
8. OpenAI APIを活用して、最適な投資戦略を提案し、リスクとリターンを評価
9. 分析結果とシミュレーション結果を統合し、最終的な投資判断の示唆を提供
10. レポートをDiscordで自動的に共有し、チーム内での情報共有を促進

この分析フローにより、データ収集におけるエラーや無駄を最小限に抑えつつ、自然言語処理の結果を活用した効率的な分析が可能になります。

実装に際しては、モジュール化を徹底し、各機能の独立性を高めることで、保守性と拡張性を確保します。
