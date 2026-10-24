# SWAT — 40× on 70%: end-to-end evaluation protocol (2026-10-24)

**Research target:** At least 70% of preselected, distinct benchmark tasks must individually achieve **40× or greater reduction in total model input+output tokens**, without reducing task correctness. Do not measure only duplicated shell calls, tool output size, or a 40× average.

For 100 selected tasks, **70 distinct tasks** must qualify. For the official SWE-bench Pro V2 full 642-task split, 450 must qualify. For Terminal-Bench 2.0's 89 tasks, 63 must qualify.

## Frozen task lists

- [SWE-bench Pro V2 stratified 100-task pilot](swebench_pro_v2_pilot100.json)
- [SWE-bench Pro V2 full 642 tasks](swebench_pro_v2_full642.json)
- [Terminal-Bench 2.0 full 89 tasks](terminal_bench2_full89.json)

Both upstream source commits are pinned. Do not substitute only easy tasks after viewing results or change selection to improve the metric. A pilot claim is limited to its 100 selected tasks; it is not a full-benchmark claim.

## Per-task qualification

1. Run baseline and SWAT on the same task from identical repository base commits, with the same model, reasoning effort, tool access, fixed resources, safety policy and task timeout.
2. Run each variant three times using isolated containers or an equivalently trustworthy sandbox; alternate the run order. Do not expose the benchmark's reference patch to either agent.
3. All six executions must pass the benchmark's independent verifier. Missing, failed, and timed-out runs count against the target.
4. In each paired repetition, measure all model usage (including the skill instructions, work and verification). Compute `baseline_total_tokens / swat_total_tokens`. A task qualifies if the median of its three paired ratios is at least 40×.
5. Each selected task counts **once** toward numerator and denominator. Only an explicit, pre-registered manifest defines the denominator.
6. Preserve actual cached input counts and report billed costs separately if reliable provider rates are available. Total tokens and dollars are different metrics.
7. Maintain equal or better overall task success counts. Report performance by benchmark and source repository.

## Data integrity

A result row is genuine measured data, not estimated:

```json
{"dataset":"swe-bench-pro-v2/example","task_id":"example","repetition":1,"variant":"baseline","pass":true,"input_tokens":1200,"cached_input_tokens":100,"output_tokens":200,"wall_seconds":50.0}
```

Use:
```bash
python3 benchmarks/fulltask/evaluate.py observed.jsonl --manifest benchmarks/fulltask/swebench_pro_v2_pilot100.json --summary-only
python3 -m unittest discover -s benchmarks/fulltask -p 'test_*.py'
```

Tasks with no observations stay in the selected denominator, and results outside the manifest are rejected. The report cannot return an achieved 40×/70% gate with fewer than 30 tasks, fewer than three repetitions, absent manifest, or degraded success rates.

## Current status

Read [STATUS-2026-10-24.md](STATUS-2026-10-24.md) for exact coverage, provenance, pilot measurements, and blockers. Do not mix the 20–40× controlled search microbenchmarks into full agent performance.

## Genuine execution requirements

SWE-bench Pro V2 provides pinned public task images and Harbor verifiers. Terminal-Bench requires isolated task containers. MSM2-1 currently has Codex CLI and Colima installed, but Colima is not running and Docker CLI/Harbor were not found. Benchmarks must not execute untrusted scripts directly on the personal Mac. Dataset discovery is not task completion.

## Evolution path

If 40× on at least 70% is not achieved by the standalone SKILL.md, test independent public techniques—selective context loading, validated artifact reuse, safe read-only tool-call deduplication with invalidation, deterministic routing—each with its own separate evidence. Do not claim that a runtime interceptor's performance comes from the standalone Skill.

Sources: [SWE-bench Pro V2](https://github.com/scaleapi/SWE-bench_Pro-os/blob/main/v2/README.md), [Terminal-Bench 2.0](https://github.com/harbor-framework/terminal-bench-2), [Agent Skills](https://agentskills.io/specification).
