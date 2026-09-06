# Consumer AI Evidence Agent Contract

`AGENTS.md` is the only repository-wide agent instruction source.

This repository owns evidence about consumer-AI users, subscribers, usage, commerce, and related commercial signals. Global market/forecast comparison belongs in `investor2`.

## Data rules

- Prefer company primary disclosures and official product/API documentation.
- Preserve metric identity, definition, scope/geography, reporting period, unit, source URL, retrieval time, and provenance required by the current dataset.
- Users, subscribers, sessions, revenue, commerce volume, conversion, and derived estimates are different metrics unless the source explicitly relates them.
- Do not infer missing company metrics, global totals, monetization, conversion, or market share.
- Reuse `research/validate_ai_consumer.py` as the validation authority rather than copying its logic.

## Execution and verification

Proceed with read-only and reversible work without unnecessary confirmation. Reuse one canonical collector/schema/workline per outcome and prefer deletion over parallel validation or wrappers.

Run the smallest relevant deterministic checks first. CI proves only what it executed. Merge and product/data release are separate; release requires the merged artifact/API/UI or fresh source acquisition in scope to be directly verified.

Do not execute purchases, subscriptions, trades, or account actions.

## Completion

Re-read state before writes, read back after writes, and stop when the requested evidence or release state is directly verified. Unchecked outcomes remain `UNVERIFIED`.
