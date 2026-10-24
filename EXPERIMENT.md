# SWAT — reproducible A/B experiment

**Question:** Does loading SWAT decrease redundant coding-agent work without reducing successful completion?

1. Choose a small, non-sensitive, deterministic task with a clear pass/fail condition.
2. Make two disposable copies of the same repository revision.
3. Run baseline without SWAT, then SWAT with the skill loaded, using the same agent, model, tools, prompts, permissions, and environment. Reverse ordering on later repetitions.
4. Record actual model token usage if available, successful task completion, number of repeated reads/searches, retry chain length, calls, wall-clock time, and skipped mandatory checks.
5. Use at least three runs per condition before suggesting a performance pattern. Label one-off results anecdotes, not benchmarks.
6. Publish raw counts and failed cases. Never conflate tool calls, elapsed time, or frontier escalations with exact token cost.
7. Run only trusted tests or use a sandbox. Do not run untrusted repository scripts by default.

## Recording template

| Trial | Skill | Task passed? | Input tokens | Output tokens | Tool calls | Duplicated calls | Time | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| A1 | Off | — | — | — | — | — | — | Unmeasured |
| B1 | On | — | — | — | — | — | — | Unmeasured |

**Evidence rule:** Do not populate the table with estimated or invented outcomes.

## Pilot outcome (2026-10-24)

One completed pair passed 2/2 tests in both variants. Baseline 100,979 input / 525 output tokens, 3 tool calls, 16.8 sec. SWAT 86,800 input / 685 output tokens, 4 calls, 22.2 sec. Additional SWAT trial timed out after 180 sec. Experimental evidence is currently insufficient to claim consistent savings.
