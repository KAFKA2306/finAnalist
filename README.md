# finAnalist — consumer AI adoption evidence

[![CI](https://github.com/KAFKA2306/finAnalist/actions/workflows/ci.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/ci.yml)
[![AI consumer source](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-consumer-source.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-consumer-source.yml)
[![Deploy Pages](https://github.com/KAFKA2306/finAnalist/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/pages.yml)

**OpenAI / Google / Meta のconsumer AIが、検索・意思決定・マルチモーダル操作・購入の入口へ広がっているかを、各社の一次情報だけで追跡します。**

公開ダッシュボード: https://kafka2306.github.io/finAnalist/

旧NewsAPI / Alpha Vantage投資レポートprototypeは正準成果物ではありません。現在の安定したmachine-readable surfaceは [`api/v1/ai-consumer/`](api/v1/ai-consumer/) です。Pagesはこの正準APIだけをread-onlyで表示し、別のcurrent値を持ちません。

## Canonical outputs

- [`metrics.json`](api/v1/ai-consumer/metrics.json) — provider/product/metricごとの公式usage observation
- [`features.json`](api/v1/ai-consumer/features.json) — feature launch / rollout / announcement event。usageとは別table
- [`comparison.json`](api/v1/ai-consumer/comparison.json) — provider × metric definitionの最新公表値。WAU↔MAUの換算はしない
- [`openai-signals.json`](api/v1/ai-consumer/openai-signals.json) — OpenAI Signals公式CSV bundleのfile inventory / SHA-256
- [`manifest.json`](api/v1/ai-consumer/manifest.json) — 全一次sourceのURL / retrieved evidence hash / file hash
- [`index.json`](api/v1/ai-consumer/index.json) — 安定したentry point

## Data contract

各usage observationは以下を必須にします。

- `provider`
- `product`
- `metric`
- `value` / `unit` / `qualifier`
- `geography`
- `period`
- `as_of`
- `definition`
- `source_url`

重要な分離規則:

- weekly active users / monthly active users / subscriber count / query count / message countを別metricとして保持
- `greater_than` / `nearly` 等の公式qualifierを捨てない
- feature launchとactual usageを別tableにする
- `announced` と `launched` を同一視しない
- third-party traffic estimateをofficial observationに混ぜない
- 数値非開示期間を補間しない
- 異なるmetric definitionを月次換算等で疑似比較しない

## Primary sources

- OpenAI Signals: https://openai.com/signals/data-download/
- OpenAI product/company announcements: https://openai.com/news/
- Google Search / Alphabet official posts: https://blog.google/products-and-platforms/products/search/
- Meta Newsroom: https://about.fb.com/news/

`research/update_ai_consumer.py` はledger内で参照する各公式URLをlive取得し、response SHA-256をmanifestへ保存します。OpenAI Signalsは公式CSV ZIP自体のSHA-256と各CSV metadataも保持します。

## Rebuild

```bash
python research/update_ai_consumer.py
```

GitHub Actionsの `AI consumer source` は平日に一次情報を再検証し、evidenceが変わった場合だけ [`api/v1/ai-consumer/`](api/v1/ai-consumer/) をcommitします。`Deploy Pages` はmain上の同じcanonical APIを静的artifactへ同梱し、公開後にexact source commitと主要JSONを再検証します。

## Verification

```bash
python -m unittest tests.test_openai_signals_collector tests.test_ai_consumer_ledger -v
```

CIはさらにlive sourceを取得して、次をfail-closedで検証します。

- OpenAI / Google / Metaの3 providerが存在する
- 公式公表履歴が12か月以上ある
- metric definition / geography / period / sourceが欠落しない
- usage / feature eventが分離されている
- WAU / MAUを相互換算していない
- third-party traffic sourceが混入していない
- OpenAI Signals bundleが実際に取得できる

Tracked work: https://github.com/KAFKA2306/finAnalist/issues/11
