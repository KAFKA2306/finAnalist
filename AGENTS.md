# Repository Agent Contract

## Mission

Own consumer-AI usage and agent/commerce behavior evidence for this repository. Produce reproducible observations of user/subscriber/usage/commercial signals from primary sources where possible, while keeping partial product metrics separate from global AI-market forecasts.

## Canonical authority

- Prefer company primary disclosures, official product/API documentation and other authoritative sources appropriate to each metric.
- Preserve company/product/metric identity, definition, scope/geography, observation/reporting period, unit, source URL, retrieval time and provenance fields required by the dataset.
- Keep users, subscribers, sessions, revenue, AI-mediated commerce and derived estimates as distinct metrics unless the source explicitly defines a relationship.
- Cross-repository ARK forecast comparison belongs in `investor2`; do not duplicate forecast authority here.

## Autonomous execution

1. Inspect current `main`, README, open Issues/PRs, canonical metric feeds, workflows/tests and public outputs.
2. Continue one canonical workline before creating another collector, schema, branch or Issue.
3. Prefer newly verified primary observations, definition/scope corrections, deterministic comparisons, public usability, then simplification.
4. Require exact definition/unit/scope compatibility before connecting metrics or calculating forecast gaps.
5. Run focused deterministic checks and verify the exact reviewed revision before merge.
6. Stop at the fixed point; do not transform user/subscriber proxies into revenue or global-market measurements.

## Branch lifecycle

- Aside from the default branch and unavoidable platform-managed/protected branches, a persistent branch is permitted only while it is the head branch of a currently open PR.
- Creating a work branch creates an obligation to open or reuse its canonical PR immediately; do not use branches as backlog, continuation state, backup, archive, or evidence storage.
- After a PR is merged or closed, delete its head branch after verifying PR/main state. A branch with no open PR is an orphan and must be deleted.
- Before and after work, compare repository branches with open PR heads. Do not report cleanup/fixed point while an orphan task branch remains.
- If the available tool cannot delete a branch, record that as a tooling blocker and do not claim cleanup complete. Never create another orphan branch as a workaround.

## Merge and release are separate

### PR merge conditions

A PR may merge when the repository-local metric/data contract is correct on the exact head revision: metric definitions and scope remain intact, primary-source provenance is preserved, deterministic tests pass, generated artifacts are reproducible where affected, and no unresolved review or correctness blocker remains.

A future company disclosure, live source fetch after merge, public deployment, observed user adoption, traffic, revenue, or conversion is **not** a merge condition unless the PR specifically changes the release mechanism and pre-merge validation belongs to that bounded change.

### Product/data release conditions

Release is a separate post-merge decision. Treat consumer-AI data/views as released only after the merged `main` revision is read back and the release surfaces in scope are actually verified, including published artifacts/API/UI, deployment identity, fresh source acquisition when required, and rollback/rebuild path where applicable.

A merged PR does not prove product/data release or market adoption. A release/source blocker may block release without invalidating a correctly merged repository change. Report merge and release independently.

## Boundaries

- Users, subscribers, usage, commerce volume and revenue are not interchangeable.
- Do not infer missing company metrics, global totals, monetization, conversion or market share.
- Do not execute purchases, subscriptions, trades or account actions.
- Unobserved source, CI, deployment or commercial outcomes remain unverified.

## Completion report

Report verified consumer-AI evidence Before -> After, primary source/canonical artifact, Issue/PR/commit/check evidence, then report `merged` and `released` separately with direct evidence for each. Include branch cleanup state, manual work removed and remaining blocker.