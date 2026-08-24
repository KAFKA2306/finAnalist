# finAnalist — consumer AI adoption & economics evidence

[![CI](https://github.com/KAFKA2306/finAnalist/actions/workflows/ci.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/ci.yml)
[![AI consumer source](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-consumer-source.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-consumer-source.yml)
[![AI economics source](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-economics-source.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/ai-economics-source.yml)
[![Deploy Pages](https://github.com/KAFKA2306/finAnalist/actions/workflows/pages.yml/badge.svg)](https://github.com/KAFKA2306/finAnalist/actions/workflows/pages.yml)

Consumer AIの**利用・能力**と、frontier AI providersの**ARR / revenue run rate / revenue**を、定義とsource provenanceを保ったまま追跡するrepositoryです。

- Consumer AI dashboard: https://kafka2306.github.io/finAnalist/
- AI Economics dashboard: https://kafka2306.github.io/finAnalist/economics.html

## Canonical APIs

### Consumer AI

`api/v1/ai-consumer/`

- `metrics.json` — provider/product/metricごとの公式usage observation
- `features.json` — feature launch / rollout / announcement event
- `comparison.json` —同一定義内のlatest comparison
- `openai-signals.json` — OpenAI Signals公式CSV bundle metadata
- `manifest.json` — source / retrieved evidence hash / output hash
- `index.json` — stable entry point

### AI Economics

`api/v1/ai-economics/`

- `observations.ndjson` — append-onlyの経済観測履歴
- `latest.json` — `provider × product × metric × measurement_type` ごとのlatest observation
- `comparables.json` — Microsoft / Salesforce / Adobe / SAP等の比較用一次財務値
- `sources.json` — source class / source health / response SHA-256
- `candidates.json` — RSS / official news indexから発見した候補。canonical observationとは分離
- `manifest.json` — seed / inventory / output hash / coverage
- `index.json` — stable entry point

## Data rules

- `company_reported` / `media_reported` / `third_party_estimate` / `derived` / `modeled` を混ぜない。
- ARR、annualized revenue run rate、annual revenue、quarterly revenueを別metricとして保持する。
- `effective_at` と `observed_at` を分離する。
- 推定値が更新されても過去値を上書きしない。
- standalone revenueが確認できないproviderを親会社segment revenueで埋めない。
- 異なる通貨を無断換算しない。SAPのEUR値はUSD比較barから除外する。
- discovery sourceの更新だけでcanonical observationを作らない。

## Rebuild

```bash
python research/update_ai_consumer.py
python research/validate_ai_consumer.py api/v1/ai-consumer

python research/update_ai_economics.py
python research/validate_ai_economics.py api/v1/ai-economics
```

`AI economics source` workflowは平日にsourceをlive取得し、一次sourceはfail-closedで検証します。TickerTrends / ARK / media source等のdiscovery候補はsource attributionを残して蓄積し、canonical observationへ自動昇格させません。内容が変わらなければ同じcanonical outputを維持します。

## Verification

```bash
python -m unittest \
  tests.test_openai_signals_collector \
  tests.test_ai_consumer_ledger \
  tests.test_ai_economics -v
```

Pages workflowはconsumerとeconomicsのcanonical projectionを同じsource commitからbuildし、deployment後にexact commitと両APIを再取得して検証します。
