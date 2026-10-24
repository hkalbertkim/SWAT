#!/usr/bin/env python3
"""Freeze and validate FULL SWAT official benchmark execution coverage.

This program prepares the complete run inventory (no task filtering) and prints
run commands. It deliberately does not spend model tokens or upload Codex auth.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "benchmarks" / "fulltask"
LOCAL = ROOT / ".benchmark"
HARBOR = LOCAL / "harbor-venv/bin/harbor"
SWE = LOCAL / "public-benchmarks/swe-bench-pro-v2"
TB = LOCAL / "public-benchmarks/terminal-bench-2"
OUTPUT = LOCAL / "full_runs"
SUITES = [
    ("swebench_pro_v2_full642.json", SWE, "v2/tasks", 642),
    ("terminal_bench2_full89.json", TB, ".", 89),
]


def sha(directory):
    return subprocess.check_output(
        ["git", "-C", str(directory), "rev-parse", "HEAD"], text=True
    ).strip()


def inspect_suites():
    suites = []
    for filename, cloned, tasks_subdir, expected in SUITES:
        src = json.loads((BENCH / filename).read_text())
        assert src["task_count"] == expected and len(src["tasks"]) == expected
        assert sha(cloned) == src["source_commit"], (filename, "wrong upstream commit")
        basedir = cloned / tasks_subdir
        for task in src["tasks"]:
            name = task["task_id"]
            folder = basedir / name
            if not folder.is_dir():
                raise RuntimeError("Missing task directory: " + str(folder))
            for item in ("task.toml", "instruction.md"):
                if not (folder / item).is_file():
                    raise RuntimeError("Missing official task file: " + str(folder / item))
        suites.append({
            "suite": src["benchmark"],
            "source_commit": src["source_commit"],
            "manifest": filename,
            "task_count": expected,
            "task_root": str(basedir),
            "expected_repetitions": src["expected_repetitions"],
            "expected_runs": expected * 2 * src["expected_repetitions"],
        })
    assert sum(s["expected_runs"] for s in suites) == 4386
    return suites


def commands(suites, model="gpt-5.6", provider="docker"):
    outputs = []
    for item in suites:
        for variant in ("baseline", "swat"):
            # External task execution requires a confined model-credential strategy.
            # Do NOT copy a reusable ChatGPT session auth file into a cloud sandbox.
            cmd = [
                str(HARBOR), "run",
                "--path", item["task_root"],
                "--agent", "codex",
                "--model", model,
                "--env", provider,
                "--n-attempts", "3",
                "--n-concurrent", "1" if provider == "docker" else "16",
                "--job-name", "swat-" + item["manifest"].replace(".json", "").replace("_full642", "-642").replace("_full89", "-89") + "-" + variant,
            ]
            if variant == "swat":
                cmd += ["--ak", "prompt_template_path=" + str(OUTPUT / "swat-prompt.j2")]
            outputs.append({"suite": item["suite"], "variant": variant, "cmd": cmd})
    return outputs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", choices=("docker", "modal"), default="docker")
    parser.add_argument("--model", default="gpt-5.6")
    parser.add_argument("--execute", action="store_true")
    opts = parser.parse_args()
    suites = inspect_suites()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    skill = (ROOT / "skills/swat/SKILL.md").read_text()
    (OUTPUT / "swat-prompt.j2").write_text(
        "{{ instruction }}\n\nApply the following SWAT behavior rules while retaining all original task requirements:\n\n" + skill
    )
    jobs = commands(suites, opts.model, opts.provider)
    plan = {
        "source": "locked manifests and pinned official Git clones",
        "status": "BLOCKED_AT_SECURE_SCALABLE_EXECUTION",
        "suites": suites, "jobs": jobs,
        "total_distinct_tasks": sum(s["task_count"] for s in suites),
        "expected_agent_executions": sum(s["expected_runs"] for s in suites),
        "notes": [
            "A job that starts or exits 0 can still contain failed trials; inspect Harbor result.json.",
            "SWE-bench Pro V2 authoritative claims require official fresh-container patch regrading.",
            "Do not expose reusable local ChatGPT auth to a third-party cloud worker.",
            "Arm64 local Docker uses slow amd64 emulation for SWE-bench Pro V2 images.",
            "Do not publish raw agent trajectories or secret-bearing logs.",
        ],
    }
    (OUTPUT / "full_run_plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    public = {
        "status": plan["status"], "suites": [
            {k: s[k] for k in ("suite", "source_commit", "manifest", "task_count", "expected_runs")}
            for s in suites
        ],
        "total_distinct_tasks": plan["total_distinct_tasks"],
        "expected_agent_executions": plan["expected_agent_executions"],
        "prepared_jobs": len(jobs),
        "provider": opts.provider,
        "model": opts.model,
        "reason_not_executing": "No approved credential-isolated scalable worker and verified official grader",
    }
    (BENCH / "FULL-RUN-PREFLIGHT.json").write_text(json.dumps(public, indent=2) + "\n")
    print(json.dumps(public, indent=2))
    if opts.execute:
        # Gate intentionally fails closed. Full cloud model execution requires an
        # explicitly configured scoped credential and verified fresh-container grader,
        # neither of which may be inferred from a local ChatGPT session file.
        raise SystemExit("BLOCKED: full-agent official execution needs secure "
                         "model credentials, cloud capacity and passing grader preflight. "
                         "No incomplete/full-suite result was fabricated.")


if __name__ == "__main__":
    main()
