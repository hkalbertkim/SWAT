#!/usr/bin/env python3
"""SWAT repeatable paired experiment. Run with python3 benchmarks/run_ab.py."""
import json
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PROMPT = "Fix the failing unittest in this small Python repository with the minimum edit. Run python3 -m unittest discover -s . -p test_*.py. Stop when tests pass. Do not use the internet. Provide a brief outcome."

def trial(number, variant):
    work = ROOT / ".benchmark" / ("run%s_%s" % (number, variant))
    work.mkdir(parents=True, exist_ok=True)
    (work / "alpha.py").write_text("def normalize(items):\n    return [x.strip().lower() for x in items]\n")
    (work / "beta.py").write_text("from alpha import normalize\n\ndef uniques(items):\n    return list(dict.fromkeys(normalize(items)))\n")
    (work / "test_beta.py").write_text('import unittest\nfrom beta import uniques\nclass Tests(unittest.TestCase):\n def test_duplicates(self):\n  self.assertEqual(uniques([" A ","a"," B "]),["a","b"])\n def test_non_strings(self):\n  self.assertEqual(uniques(["A",None," B "]),["a","b"])\nif __name__=="__main__": unittest.main()\n')
    skill = (ROOT / "skills/swat/SKILL.md").read_text()
    instruction = PROMPT if variant == "baseline" else PROMPT + "\n\nFollow this Skill:\n" + skill
    resultdir = ROOT / ".benchmark/results"
    resultdir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    try:
        run = subprocess.run(["/Users/akim/.local/bin/codex", "exec", "--json", "--ephemeral", "--ignore-user-config", "--sandbox", "workspace-write", "--skip-git-repo-check", instruction], cwd=work, input="", capture_output=True, text=True, timeout=120)
        events = []
        for line in run.stdout.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        usage = [event.get("usage", {}) for event in events if event.get("type") == "turn.completed"]
        tools = [event for event in events if event.get("type") == "item.completed" and event.get("item", {}).get("type") in ("command_execution", "mcp_tool_call")]
        check = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py"], cwd=work, capture_output=True, text=True, timeout=15)
        record = {"run": number, "variant": variant, "status": "complete", "passed": check.returncode == 0, "exit": run.returncode, "seconds": round(time.monotonic()-started, 1), "usage": usage, "tools": len(tools)}
        (resultdir / ("run%s_%s.jsonl" % (number,variant))).write_text(run.stdout)
    except subprocess.TimeoutExpired:
        record = {"run": number, "variant": variant, "status": "timeout", "passed": False, "seconds_limit": 120, "usage": None}
    (resultdir / ("run%s_%s.summary.json" % (number,variant))).write_text(json.dumps(record, indent=2))
    print(json.dumps(record), flush=True)

if __name__ == "__main__":
    for n in (2,3):
        for variant in (("swat","baseline") if n%2==0 else ("baseline","swat")):
            trial(n,variant)
