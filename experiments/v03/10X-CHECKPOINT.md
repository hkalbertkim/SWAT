# 10× threshold checkpoint — October 24, 2026

## Experiment passed, narrow scope only

The `duplicate_lookup_microbench.py` script ran 20 identical read-only searches over 120 immutable text fixtures. Reusing the first successful lookup yielded the same output every time.

Recorded run (see `results.json`):
- Raw read-only process invocations: 20
- Deduplicated process invocations: 1
- Read-only process invocation reduction: **20×**
- Elapsed time in this run: 0.146 s versus 0.0072 s (**20.24×**)
- Output equivalence: PASS

## Important distinction
This benchmark measures only duplicate retrieval work, deliberately crafted to create repeated requests. It is not a realistic whole-agent A/B benchmark, not an SDK or API billing result, not proof of 10× model tokens/cost, and not the behavior of a standalone Skill. Runtime memoization requires safe read-only classification and invalidation on file changes, permissions, and freshness.

## Evolution decision
We tried a different design class, **execution-level deduplication**, rather than incremental prompt edits. This produced >10× on the narrow redundant lookup workload. Stop optimizing this microbenchmark. Next product gate (if pursued): collect organic duplicate traces from live agent sessions, preserve correctness and test cache invalidation, then compare full task outcomes and actual token measurements across diverse tasks.

## Public research
- https://github.com/NousResearch/hermes-agent/issues/18076 — loop detection and duplicate calls
- https://github.com/anvanster/compressor — measured selective output compression
- https://github.com/daseinlabs/code-compression-bench — cost per solved task as primary metric
- https://github.blog/ai-and-ml/github-copilot/how-we-make-ai-coding-more-cost-efficient-without-sacrificing-task-quality/ — recovery from aggressive compression may increase total cost
