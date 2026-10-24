---
name: swat
description: Reduce redundant agent work without reducing correctness.
---
# SWAT — Stop Wasting Agent Tokens

Apply only when repeated work, retries, unnecessary exploration, or task overrun are plausible. For trivial tasks, act normally; do not spend turns discussing optimization.

1. **Reuse what is still valid.** Before re-reading or re-searching, check whether equivalent evidence from this task remains current for the same inputs and permissions.
2. **Resume from the failure.** If a downstream step fails, retain valid earlier read-only results. Check actual state before retrying writes, deployments, or other side effects.
3. **Stop at verified completion.** Make the smallest requested change, run appropriate required tests, and stop when the acceptance condition is satisfied.

Do not shorten logs if missing detail would force a re-read. Preserve complete results and use targeted retrieval for large repetitive outputs. Never skip permissions, required tests, security checks, or user approval. Report measurements only if the agent provides actual usage data.

This is a behavioral Skill, not an interceptor or a guarantee of savings.
