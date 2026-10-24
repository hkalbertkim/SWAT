---
name: swat
description: Stop Wasting Agent Tokens. Use during coding and debugging to prevent duplicate reads, broad repeated searches, replay of successful steps after a downstream failure, speculative edits, and unnecessary LLM work without skipping safety or validation.
---

# SWAT — Stop Wasting Agent Tokens

Do less redundant work. Preserve correctness.

## 1. Define done before doing work
- Identify the requested outcome and a checkable success condition.
- Separate required changes from interesting extras. Do not expand scope unasked.
- Prefer the smallest reversible action that can establish the answer or produce the artifact.

## 2. Inspect once, reuse while valid
- Before searching or reading, check whether the same answer, tool output, or file content is already available in this task.
- Reuse successful read-only results only while inputs, file revisions, access scope, and freshness requirements remain unchanged.
- Search narrowly around known paths, symbols, failures, and logs before scanning entire repositories.
- Never claim a cached observation is current if the underlying state may have changed.

## 3. Retry the failed step, not the successful chain
- On failure, identify the first failed operation and preserve proven upstream results.
- Retry only the failed step when the operation is safe to replay.
- Do **not** replay payments, deployments, messages, writes, external mutations, or other non-idempotent operations without checking their real status first.
- Respect rate limits and transient errors; do not manufacture success.

## 4. Use deterministic checks first
- For a known failing test, run the smallest relevant test before broader suites.
- For formatting, file existence, syntax, and static validations, use reliable local tools rather than repeatedly asking a model to speculate.
- Escalate to broader analysis when evidence is inconclusive or the localized fix fails.

## 5. Stop after verified success
- Verify the requested outcome and any mandatory security/regression checks.
- Stop when acceptance criteria are met. No opportunistic refactors or polish unless requested.
- Report what changed, how it was verified, and what remains uncertain.

## Safety and honesty
- Never bypass authorization, confirmation, user approval, safety checks, or required testing to save tokens.
- Do not cross security boundaries to reuse stale or private outputs.
- This skill changes agent behavior through instructions. It is not a cache, tool interceptor, or guarantee of token savings.
- Measure token savings using actual model usage data, not the number of omitted tool calls.

## Example
A repository search succeeds, but a downstream test command fails.
- Wasteful: rerun repository discovery, read the same files again, then retry the entire chain.
- SWAT: retain the verified search result if inputs remain unchanged; inspect the test failure and retry only the relevant check.

## Background
SWAT is standalone. Its practical principles are informed by work on KORA Doctor, KORA Reach and AgentGate. None is required to run this skill.
