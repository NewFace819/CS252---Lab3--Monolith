# Lab 3 H1 - AI extension review - Thông (vbthg)

## Feature and implementation prompt

Implementation brief developed with Codex:

> Extend the fee answer with an optional tuition breakdown. Show the regular and
> retake portions when the question includes the standalone word `breakdown`.
> Keep the existing service/API contracts, use configured rates and add offline tests.

Example through the CLI or `POST /v1/chat`:

```text
Question: tuition breakdown for 18 credits and 2 retake
Answer: Your tuition is 9,450,000 VND. Regular: 8,100,000 VND; retake: 1,350,000 VND.
```

The same question without `breakdown` still returns exactly
`Your tuition is 9,450,000 VND.`. The keyword is case-insensitive and must be a
separate whitespace-delimited word; this feature does not attempt natural-language parsing.

## Initial AI proposal

This is the initial, unintegrated AI proposal, retained here as review evidence.
It is not the production implementation:

```python
def fee_breakdown(credits, retake):
    regular = credits * 450000
    repeated = retake * 450000 * 1.5
    total = regular + repeated
    return f"Your tuition is {total:,.0f} VND. Regular: {regular:,.0f} VND; retake: {repeated:,.0f} VND."
```

## Review changes implemented with Codex

| # | Initial proposal / problem | Final change | Evidence and reason |
|---|---|---|---|
| 1 | Hard-coded rate `450000` and multiplier `1.5` ignore the environment configuration. | Reuse `Settings` and the existing `tuition()` calculation in `AssistantService._fee()`. | A test uses a rate of 101 and multiplier 1.5; the answer follows those settings. No new settings or public signatures. |
| 2 | `:,.0f` rounds the float total, which disagrees with the existing integer total for fractional VND. | Keep the validated total from `tuition()` and calculate the retake portion as `total - regular`. | For 2 regular credits and 1 retake at rate 101, the total stays 353, not 354; portions 202 + 151 reconcile exactly. This preserves the existing truncation policy rather than introducing another one. |
| 3 | A standalone formatter has no missing-credit or range validation. Calling it directly could bypass the service's error handling. | Add the breakdown only after the existing `parse_credits()` / `tuition()` block succeeds. | Missing credits and counts 0 / 31 keep the existing helpful error answers; no partial breakdown or exception leaks to HTTP. |
| 4 | Replacing all fee answers with the proposed output would change established behaviour. | Require the optional standalone `breakdown` keyword. Leave the ordinary answer unchanged. | Exact-output tests cover both old and new answers. The HTTP test checks the existing five response fields, intent and request ID. |

## Checklist and verification

- Interfaces: `handle(Message) -> Response`, `Intent`, models and endpoint schemas unchanged.
- Implementation: only the existing service orchestration changes; no leaf-module dependency added.
- Dependencies: none added. No LLM call, network, clock or new global state for the feature.
- Secrets and privacy: no keys needed and no new logging. A regression test checks that the question is not logged.
- Tests: 8 core cases plus 1 HTTP case, all offline. Initial suite: **172 passed**;
  after integrating main with PR #26: **185 passed**.
- Ruff check and format check pass.
- Reviewer requested for the PR: **Hải (`NewFace819`)**. Approval and merge are separate from these local checks.

## Review confirmation

Thông confirmed reading the completed review on 2026-11-06. Codex assisted with
the implementation, review improvements, tests and documentation; see the
[AI use log](../ai-use-log.md).

