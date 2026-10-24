# SWAT 20× diverse benchmark checkpoint — 2026-10-24

## Scope and methodology
These are **read-only command invocation microbenchmarks**, not entire coding-agent workloads or token benchmarks.

- 8 controlled synthetic fixture workloads: [diverse_results.json](diverse_results.json).
- 3 actual public repository snapshots: [real_repo_results.json](real_repo_results.json) (requests, click, flask) with 3 fixed *synthetic query sequences* for each.
- Baseline runs every read-only search; optimized version reuses a previously obtained identical answer while repository files remain unchanged.
- Each dataset checks exact equivalence of return code and stdout.
- No user prompts or stochastic model executions were performed; no cost/token claim is warranted.
- Run durations are short and a single timing run per scenario; repeat and use robust statistics before publishing precision performance claims.

## Actual measured findings
- Synthetic: 4 of 8 scenarios achieve >=20× speedup: identical 40×, count hotspot 29×, small repo 29×, large repo 30×.
- Synthetic 80 queries / 5 unique: 16.52×; 60 / 15: 3.93×; unique queries ~1×.
- Real repository snapshots: heavy repetitive search ~29.77–30.89×, three distinct queries repeated ~9.90–10.06×, unique search ~0.99–1.01×.
- Output equivalence: 17/17 cases pass.
- **20× is reached on 7/17 scenarios, not in all workload distributions.**
- By construction, invocation reduction is requests / unique queries. The result cannot imply a general 20× improvement in agents.

## What changes direction
This verifies an available optimization mechanism but does not validate a product differentiator. GitHub Copilot's Sept 2026 research found that hiding useful tool output can cause costly recovery work; optimize completed tasks, preserving useful context.
Microsoft CompactionBench (Oct 2026) reports up to 25.4% full-task cost reduction, illustrating how modest true system-level savings compare to large narrow microbenchmark multipliers.

## Next decisive experiment
1. Collect real tool-call traces from Codex/KORA Doctor (with permission, redacted and no secrets).
2. Determine observed repeated read-only requests, including repository state changes and cache validity.
3. Build a constrained plugin/interceptor **only if** Skill-only A/B shows that model instructions cannot prevent retries.
4. Run paired end-to-end agent task benchmarks on SWE-bench Verified samples; compare resolution success, uncached+cached token costs, model turn counts, latency.
5. The 20× target remains a research goal for a **naturally high-duplication segment**, never a general product claim before that evidence.

External references:
- https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md
- https://github.blog/ai-and-ml/github-copilot/how-we-make-ai-coding-more-cost-efficient-without-sacrificing-task-quality/
- https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/
