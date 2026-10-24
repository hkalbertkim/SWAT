#!/usr/bin/env python3
"""Read-only status report for the pre-registered full SWAT campaign.

Counts distinct official tasks separately from oracle preflight and genuine
paired agent experiments. Never reports missing tasks as completed.
"""
import json
import pathlib
import subprocess

ROOT=pathlib.Path(__file__).resolve().parents[2]
JOBS=ROOT/".benchmark/harbor-jobs"
MANIFESTS=[
    ("swe_pro_full642", ROOT/"benchmarks/fulltask/swebench_pro_v2_full642.json"),
    ("terminal_bench_full89", ROOT/"benchmarks/fulltask/terminal_bench2_full89.json"),
]

def official_job(name):
    path=JOBS/name/"result.json"
    if not path.exists():
        return {"state":"NOT_STARTED","completed":0,"errored":0}
    try:
        r=json.loads(path.read_text())
        stats=r.get("stats",{})
        return {"state":"FINISHED" if r.get("finished_at") else "ACTIVE_OR_INTERRUPTED",
                "completed":stats.get("n_completed_trials",0),
                "errored":stats.get("n_errored_trials",0),
                "running":stats.get("n_running_trials",0),
                "pending":stats.get("n_pending_trials",0),
                "expected":r.get("n_total_trials")}
    except (ValueError,OSError) as exc:
        return {"state":"CORRUPT","message":str(exc)}

def main():
    total=0
    manifest_counts={}
    for name,path in MANIFESTS:
        m=json.loads(path.read_text())
        manifest_counts[name]={"distinct_tasks":len(m["tasks"]),
                               "required_40x":(7*len(m["tasks"])+9)//10,
                               "expected_agent_runs":len(m["tasks"])*6}
        total+=len(m["tasks"])*6
    status={"manifest":manifest_counts,"total_expected_agent_runs":total,
            "jobs":{"terminal_oracle_sanity":official_job("swat-tb2-full89-oracle-mounted"),
                    "terminal_baseline":official_job("swat-tb2-full89-codex-baseline"),
                    "terminal_swat":official_job("swat-tb2-full89-codex-swat"),
                    "swe_pro_baseline":official_job("swat-swe-pro-v2-full642-baseline"),
                    "swe_pro_swat":official_job("swat-swe-pro-v2-full642-swat")},
            "rule":"Oracle trials do not count as model runs or SWAT 40x qualifications."}
    print(json.dumps(status,indent=2))

if __name__=="__main__":main()
