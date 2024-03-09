## 投資テーマ分析ツール

### 概要

本ツールは、ユーザーが入力した投資テーマに関連する企業群を自動で特定し、各社の事業内容や業績見通し、バリュエーション等を分析することで、投資判断の示唆を提供します。

### 機能

* **ニュースデータ分析**: 最新の市場動向を反映した関連企業の特定
    * 複数のニュースデータベース (Google News API, NewsAPI等) から記事を収集
    * Claude APIを用いて、記事から関連企業名を抽出
    * Claude APIを用いて、記事の内容を分析
    * ニュースデータ分析結果は特定のフォルダにアーカイブとして保存し、次回分析時にも読み込む
* **企業分析**: 事業内容、業績見通し、競合環境等の詳細な分析
    * IRデータベースや決算説明資料、企業公式サイト等から情報収集
    *企業概要分析結果は企業ごとに特定のフォルダにアーカイブとして保存し、次回分析時にも読み込む
    * Claude APIを用いて、情報から定性情報を抽出・要約
    * 財務諸表データに基づいて、売上高、利益、成長率等を分析
    * 企業分析結果は企業ごとに特定のフォルダにアーカイブとして保存し、次回分析時にも読み込む
* **財務分析**: バリュエーション指標の算出と分析
    * 財務諸表データに基づいて、PER、PBR、ROE等を算出
    * 業種平均や類似企業との比較分析
    * 将来の業績予想に基づいて、DCF法等の割引現在価値計算
    * 企業分析結果は企業ごとに特定のフォルダにアーカイブとして保存し、次回分析時にも読み込む
* **レポート生成**: 分析結果を分かりやすくまとめたレポート出力
    * Markdown形式で出力
    * 分析結果の可視化 (グラフ、チャート等)
    * 投資判断の示唆とリスク提示

### 必要な環境

* ライブラリ: pandas, sqlalchemy, requests, beautifulsoup4, googlenews
* ニュースデータベースのAPIキー (例: Google News API, NewsAPI等)
* IRデータベースのAPIキー (例: QuickFS, SPEEDA等)
* Claude API の利用登録

### 使い方

1. config.iniファイルに、各APIキー等を設定
2. main.pyを実行し、投資テーマを入力

```python
python main.py
```

例: 「TSMCの新工場建設とそれに付帯して営業利益が増加する会社への投資をしたい」

3. レポートがmarkdown形式で出力されます。

### モジュール構成

* news_analysis.py: ニュースデータ分析
* company_analysis.py: 企業分析
* financial_analysis.py: 財務分析
* report_generation.py: レポート生成
* main.py: メイン実行モジュール
* config.ini: 設定ファイル

### 分析の流れ

1. ニュースデータベースから、投資テーマに関連するニュース記事を検索・収集
2. Claude APIを用いて、記事から関連企業名を抽出
3. 抽出された企業について、IRデータベースや決算説明資料等から事業内容、業績見通し、競合環境等を分析
4. 財務諸表データを取得し、売上高、利益、成長率等を分析
5. バリュエーション指標を算出し、業種平均や類似企業との比較分析
6. 分析結果を総合し、投資判断の示唆を含むレポートを生成
