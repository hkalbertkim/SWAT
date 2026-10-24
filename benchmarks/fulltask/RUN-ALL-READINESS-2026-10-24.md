# Complete-benchmark execution readiness — 2026-10-24

## User request and fixed scope
Run **every task**, not a cherry-picked subset, in BOTH official public suites:

- SWE-bench Pro V2: 642 distinct tasks × 2 variants (SWAT OFF/ON) × 3 attempts = **3,852 agent runs**, target >=450 individually meeting >=40×.
- Terminal-Bench 2.0: 89 distinct tasks × 2 variants × 3 attempts = **534 agent runs**, target >=63 individually meeting >=40×.
- Total: **731 distinct tasks, 4,386 actual agent runs**.
- Keep complete fail/timeout/missing rows in denominator; no aggregate-average substitution.

## Accomplished this turn
- Installed Harbor 0.24.0 into ignored project virtual environment, plus Docker CLI, Docker Compose, Docker Buildx.
- Started isolated Colima on MSM2-1 (4 vCPU, 10 GiB RAM, 160 GiB virtual disk).
- Cloned complete SWE-bench Pro V2 public task tree at pinned commit `66f92766bba642462d4bbe5479e83f91f9211862`: verified 642 task directories.
- Cloned complete Terminal-Bench 2.0 at pinned commit `2fd12b88aafdd04a52c298e3940bcb189f9766d6`: verified 89 task directories.
- Validated all 731 manifest task identities, `instruction.md`, and `task.toml` via `prepare_all.py`; generated four FULL-SUITE Harbor job specifications with `--n-attempts 3` and NO subset filters.
- Downloaded and inspected one official SWE-bench Pro V2 amd64 image: ~1.33GB compressed, 4.47GB unpacked.
- Actual isolated smoke check using official Harbor `nop` agent: Docker Compose/Buildx issues were fixed; agent sidecar reached healthy container; official verifier then failed with `RewardFileNotFoundError` after ~2m 58s. This is a **harness failure**, not a SWAT performance measurement.

## Blockers — do not claim full-suite execution
- No authenticated Modal/Daytona provider credentials or approved cloud compute budget on MSM2-1.
- A local 4-vCPU/10GB arm64 Docker VM runs all SWE-bench Pro images via amd64 emulation, and 642 images cannot fit concurrently on its 160GB disk. Official guidance recommends cloud execution.
- The official isolated grader currently does not return a reward on this Mac. Do not bypass network restrictions to make it appear to pass.
- Existing Codex ChatGPT login is a reusable local credential. Do **not** copy it into untrusted benchmark images or a third-party cloud worker without a secure, explicit credential strategy. No OpenAI API credential currently present.
- On-host 4,386 real agent runs would consume very substantial time and provider capacity. No token-intensive full-suite jobs have been started.

## Evidence / run status
- Full-suite model trials: **0 / 4,386 completed**.
- Official benchmark graded success: **none**.
- Local prior single-task Codex pilot (not part of official suites): **1.16× total model tokens**, correctness preserved.
- Status: `BLOCKED_AT_SECURE_SCALABLE_EXECUTION`, not `PASS`.

## Recovery path
1. Configure an isolated high-capacity linux/amd64 cloud evaluation provider with an approved budget and a scoped, controlled model credential / gateway. Avoid storing long-lived personal ChatGPT auth on untrusted workers.
2. Confirm official oracle/nop verifier results (SWE V2 requires oracle 642/642, nop 0/642) and lock timeouts / network allowlists.
3. Run complete baseline and SWAT job sets with 3 attempts for every task, extract actual usage and independent grader verdicts, perform pristine-container regrading, then score against frozen full manifests.
4. Publish raw aggregated numbers plus failures and incomplete cases, never guessed 40× results.

Sources:
- https://github.com/scaleapi/SWE-bench_Pro-os/blob/main/v2/README.md
- https://github.com/harbor-framework/harbor/blob/main/README.md
- https://github.com/harbor-framework/terminal-bench-2
