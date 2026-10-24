# SWAT

**Stop Wasting Agent Tokens.**

> Stop paying for work your AI coding agent has already done.

A tiny, portable Agent Skill that helps coding agents avoid unnecessary repeat work: duplicate repository scans, stale retries, repeated analysis, speculative refactors, and continuing after success.

No service. No API key. No KORA installation. Just one `SKILL.md`.

## Install

Copy [`skills/swat/SKILL.md`](skills/swat/SKILL.md) to your agent's supported skill directory. For an agent supporting project-local Agent Skills, use `.agents/skills/swat/SKILL.md`. Other clients may use their own directory conventions.

Ask your agent: **"Use SWAT for this task. Preserve successful steps and verify before repeating work."**

## What SWAT changes

| Situation | Without SWAT | With SWAT |
| --- | --- | --- |
| Search succeeded, test failed | Rerun search and read files | Keep valid search results; investigate failing test |
| Known symbol or failing test | Scan whole repository | Inspect exact symbol or targeted test first |
| Completed requested fix | Keep refactoring | Verify and stop |
| Test result is stale | Trust cached result | Recheck changed inputs |
| Write may already have succeeded | Blindly retry | Inspect real state before any replay |

SWAT prioritizes correctness and safety. It does not skip approvals, security checks, or mandatory tests to reduce model usage.

## Does it save tokens?

That is an experiment, not a promise. Read [EXPERIMENT.md](EXPERIMENT.md) for an honest side-by-side comparison protocol. A reduction in tool calls does not automatically establish a reduction in provider-billed tokens.

## Measured pilot (Codex CLI, October 24, 2026)

**A useful first signal, not proof of savings.** One matched small Python bug-fix trial (both variants passed two unit tests) produced the following actual Codex usage readings:

| Metric | Without SWAT | With SWAT |
| --- | ---: | ---: |
| Input tokens (includes cached) | 100,979 | 86,800 |
| Cached input tokens | 90,368 | 77,952 |
| Output tokens | 525 | 685 |
| Completed tool calls | 3 | 4 |
| Wall clock time | 16.8 s | 22.2 s |
| Independent unit tests passed | 2/2 | 2/2 |

Input tokens decreased **14.0% in this single paired observation**, while time and tool calls **increased**. A follow-up SWAT run hit a 180-second timeout and did not produce a comparable result. This is not yet evidence of consistent improvement, nor proof of cost reduction. The tested SWAT rules were injected into the prompt, rather than loaded by an agent's native skill discovery mechanism. The initial run did not counterbalance order.

For the reproducibility protocol and limitations, see [EXPERIMENT.md](EXPERIMENT.md). The [trial runner](benchmarks/run_ab.py) uses Codex JSONL usage events and records timeouts as failures.

## Why a Skill rather than a framework?

Minimal setup and no new runtime dependency. The official [Agent Skills specification](https://agentskills.io/specification) defines the required `SKILL.md` structure.

## Origin

SWAT is an independent skill informed by lessons learned building [KORA Reach](https://github.com/Krako-Labs/kora-reach), KORA Doctor, and AgentGate. SWAT does not require any of those tools. Links here are context, not installation steps.

## License

MIT. See [LICENSE](LICENSE).
