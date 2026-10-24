# SWAT — Full-task 20x benchmark protocol

**Primary question:** Across genuine coding-agent tasks, can SWAT reduce total consumed tokens per successfully completed task by 20× without losing reliability?

## Benchmark coverage
1. SWE-bench Pro V2 public: long-horizon software changes, multiple languages.
2. Terminal-Bench 2.0: terminal and operations agent tasks.
3. SWE-bench multilingual: language and repository diversity.
4. Held-out recent real user coding tasks, with authorization and full privacy redaction.
5. Verified and synthetic retry cases for diagnosis ONLY. Do not pool microbenchmarks with entire-task scores.

## Critical environment limitations
MSM2-1 currently has Codex CLI 0.149.1 but does not have Docker or Harbor installed. Terminal-Bench and SWE-bench graders typically rely on isolated environments; do not execute downloaded tasks on the personal host without a sandbox. Acquiring data is not equivalent to graded evaluation.

## Comparison
Same model ID, same reasoning effort, same repository base commit, identical user request, tool availability, safety policies, task time budget and environment. Separate fresh worktrees/containers. Alternating order (AB/BA), minimum 3 repetitions per task, randomized seed when supported. No leaked gold patches, network disabled during task execution when benchmark permits. Record authentication and prompt-skill loading method; native SKILL.md loading separately tested from prompt injection.

## Metrics / gates
Primary: *actual cost per solved task*, using provider token categories and applicable price/rate accounting. Where pricing is unavailable, show raw input, cached input and output separately. Compare paired task success, correctness regressions, end-to-end latency and model/tool calls. Count timeouts and skipped validations as failures. Require minimum 30 paired tasks in 3 different domains before any aggregate headline, and follow with full official task sets where practical.

Predefined success rule: >=20x ratio with at least baseline pass rate, measured on whole task including loading skill, retries, cache overhead and verification. State the dataset and subset coverage exactly. No selective exclusion of poor runs.

## Measurement schema
JSONL one row per task run:
```json
{"dataset":"example","task_id":"task-1","repetition":1,"variant":"baseline","pass":true,"input_tokens":1200,"cached_input_tokens":100,"output_tokens":200,"wall_seconds":50.0}
```
Use `python3 benchmarks/fulltask/evaluate.py results.jsonl` only on real captured runs. The evaluator deliberately does not read SWAT search microbenchmarks.

## Product pivot gate
If standalone skill fails to improve full-task outcomes, test alternate public approaches: progressive disclosure, selective output reduction, safe tool-call reuse with invalidation, and context compaction. Compare as distinct arms, not cumulative tuning. Keep SWAT V0 minimal; do not mix external runtimes into its advertised results.

## Relevant references
- https://labs.scale.com/leaderboard/swe_bench_pro_public_v2?tab=full
- https://www.tbench.ai/?version=2.0
- https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md
- https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/

## Revised research gate — 2026-10-24: 40× on at least 70% of tasks

40× is evaluated on **total actual model tokens over each completed coding task**, not just duplicated searches, single prompt sections, or wall-clock microbenchmarks. Count skill loading, retries, model turns and verification. For each paired run, the baseline must successfully solve the task and SWAT must also succeed; unsuccessful SWAT runs are counted as non-qualifying, not excluded. Qualifying ratio: baseline total input-plus-output tokens divided by SWAT total input-plus-output tokens >=40. Report cached-input and billed-cost figures separately.

A preliminary gate needs at least 30 baseline-solved paired runs spanning 3 datasets, at least 70% of which qualify, no decline in overall success counts, and per-dataset results disclosed. Then expand to held-out tasks and official full suites before making a broad product-performance claim. Avoid cherry-picking datasets or claiming representative coverage from only 30 samples. Do not move the goalpost after observing results.

Previous 20× aggregate metric remains in the scorer for historical comparisons; **40× / 70% is now the research target**. This is not yet a measured outcome.

Relevant evidence: Microsoft's October 2026 CompactionBench report reduced task cost up to 25.4%, an indication of how challenging broad 40× savings are. https://www.microsoft.com/en-us/research/publication/benchmarking-long-horizon-agent-context-compaction-with-compactionbench/
