# SWAT 10× research track — not a product claim

## Narrow hypothesis
When an agent retries a multi-step read-only discovery workflow after an unrelated downstream failure, preserving valid intermediate evidence may reduce *duplicate discovery calls* by >=90% for that workflow. This is not equivalent to 90% total token or cost savings.

## Candidate scenario
1. Perform 10 independent bounded file lookups with stable inputs, recording output identifiers and repository revision.
2. Trigger a downstream deterministic test failure.
3. Compare a baseline replay-all agent against an evidence-resuming strategy.
4. Verify all task outcomes and permissions match.

## Required metrics
Task success; duplicate discovery count; total calls; actual input/cached/output tokens; wall time; recovery calls; replayed side effects. Repeat with 3+ randomized tasks, 5+ seeds where feasible, same model/settings.

## Falsification
Reject a claimed 10× breakthrough if the baseline does not naturally repeat discovery, if SWAT requires a runtime interceptor while advertised as a plain Skill, or if task-level cost/success worsens.

## Existing work to borrow
- GitHub Copilot efficiency research (September 2026): https://github.blog/ai-and-ml/github-copilot/how-we-make-ai-coding-more-cost-efficient-without-sacrificing-task-quality/
- SWT runtime and cache design: https://github.com/swt-labs/stop-wasting-tokens
- Agent Skills format: https://agentskills.io/specification
