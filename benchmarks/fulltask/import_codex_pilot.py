#!/usr/bin/env python3
"""Publish only numerical fields from SWAT's previously captured Codex pilot.
Inputs under .benchmark/ are ignored and may include sensitive raw traces.
"""
import json
import pathlib
import subprocess
import sys
from evaluate import calculate

ROOT=pathlib.Path(__file__).resolve().parents[2]
SOURCE=ROOT/".benchmark/results"
HERE=pathlib.Path(__file__).resolve().parent
manifest={
    "benchmark":"SWAT internal Codex controlled bugfix pilot",
    "split":"historical-single-pair-2026-10-24",
    "expected_repetitions":1,
    "task_count":1,
    "tasks":[{"dataset":"internal-codex-bugfix","task_id":"normalize-none-input"}],
    "claim_policy":"Informational pilot only. NOT an official benchmark; not native SKILL loading."
}
rows=[]
for variant in ("baseline","swat"):
    summary=json.loads((SOURCE/(variant+".summary.json")).read_text())
    usage=summary["usage"][-1]
    test_dir=ROOT/".benchmark"/variant
    result=subprocess.run([sys.executable,"-m","unittest","discover","-s",".","-p","test_*.py"],
                          cwd=test_dir,capture_output=True,text=True,timeout=15)
    rows.append({
        "dataset":"internal-codex-bugfix","task_id":"normalize-none-input",
        "repetition":1,"variant":variant,
        "pass":result.returncode==0 and summary["exit"]==0,
        "input_tokens":usage["input_tokens"],
        "cached_input_tokens":usage["cached_input_tokens"],
        "output_tokens":usage["output_tokens"],
        "wall_seconds":summary["elapsed_sec"]
    })
(HERE/"pilot_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
(HERE/"pilot_observations.jsonl").write_text("".join(json.dumps(r)+"\n" for r in rows))
report=calculate(rows,manifest)
print(json.dumps({"tokens_baseline":rows[0]["input_tokens"]+rows[0]["output_tokens"],
                  "tokens_swat":rows[1]["input_tokens"]+rows[1]["output_tokens"],
                  "ratio":round((rows[0]["input_tokens"]+rows[0]["output_tokens"])/(rows[1]["input_tokens"]+rows[1]["output_tokens"]),3),
                  "passed":[r["pass"] for r in rows],"forty_x_qualified":report["forty_x_target"]["qualified_40x"]},indent=2))
