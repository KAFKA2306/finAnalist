# Consumer AI Evidence Agent Contract

`AGENTS.md` is the repository-wide agent instruction source.

This repository owns evidence about consumer-AI users, subscribers, usage, commerce, and related commercial signals. Global market/forecast comparison belongs in `investor2`.

## Data contract

- Prefer company primary disclosures and official product/API documentation.
- Preserve metric identity, definition, scope/geography, reporting period, unit, source URL, retrieval time, and provenance required by the current dataset.
- Users, subscribers, sessions, revenue, commerce volume, conversion, and derived estimates are different metrics unless the source explicitly relates them.
- Do not infer missing company metrics, global totals, monetization, conversion, or market share.
- `research/validate_ai_consumer.py` is the validation authority; do not duplicate its logic.

## Release boundary

Repository checks prove only the evidence and revision they executed. Product/data release requires direct verification of the merged artifact, API/UI, or fresh source acquisition that owns the claim.

Do not execute purchases, subscriptions, trades, or account actions.

## Outcome-first task interpretation (Altitude / Depth / Range / Speed)

- **Altitude:** Interpret a task as a verifiable user outcome, not only the named intermediate step. Infer the smallest justified acceptance criteria from the request and current repository state; do not silently expand scope or override explicit instructions.
- **Depth:** Use primary/current evidence and real domain tools and methods. Verify the actual postcondition independently of agent self-report, preferably on the exact changed revision or target runtime.
- **Range:** Combine code, data, tests, runtime/UI, and domain expertise when that materially improves the outcome, while respecting canonical owners and avoiding duplicate systems.
- **Speed:** Complete authorized read-only and reversible work through implementation, focused checks, and read-back without unnecessary approval loops. Bound retries and stop at the proven outcome.
- These principles never bypass repository-specific security, privacy, permission, publication, spending, destructive-action, or release boundaries. State verified results and any remaining `UNVERIFIED` layers.
