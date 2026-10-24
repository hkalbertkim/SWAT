#!/usr/bin/env python3
"""Pre-register SWE-bench Pro V2 full split and stratified 100-task pilot.
Reads only pinned GitHub file paths; never downloads reference solutions.
"""
import collections
import hashlib
import json
import math
import pathlib
import subprocess
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent
REPO = "scaleapi/SWE-bench_Pro-os"
SEED = "swat-precommit-2026-10-24-v1"


def api(path):
    call = subprocess.run(["gh", "api", path], text=True, capture_output=True, timeout=40)
    if call.returncode:
        raise RuntimeError(call.stderr[-400:])
    return json.loads(call.stdout)


def manifest(tasks, sha, tree_sha, label):
    return {
        "benchmark": "SWE-bench Pro V2",
        "split": label, "source": "https://github.com/" + REPO,
        "source_commit": sha, "source_tree": tree_sha,
        "selection_seed": SEED, "expected_repetitions": 3,
        "task_count": len(tasks),
        "tasks": [{"dataset": "swe-bench-pro-v2/" + group, "task_id": identity}
                  for group, identity in sorted(tasks)],
        "claim_policy": "All selected distinct tasks in denominator. A subset does not establish a full split claim."
    }


def main():
    metadata = api("repos/" + REPO + "/commits/main")
    commit = metadata["sha"]
    tree_sha = metadata["commit"]["tree"]["sha"]
    data = api("repos/" + REPO + "/git/trees/" + tree_sha + "?recursive=1")
    if data.get("truncated"):
        raise RuntimeError("Incomplete Git tree")
    paths = [item["path"] for item in data["tree"]
             if item.get("type") == "blob"
             and item["path"].startswith("v2/tasks/")
             and item["path"].endswith("/instruction.md")]
    groups = collections.defaultdict(list)
    for path in paths:
        identity = path.split("/")[2]
        if not identity.startswith("instance_") or "__" not in identity:
            raise ValueError("Unexpected V2 id: " + identity)
        group = identity.split("__")[0][len("instance_"):]
        groups[group].append((group, identity))
    all_tasks = [x for group in groups.values() for x in group]
    if len(all_tasks) != 642 or len(groups) != 11:
        raise RuntimeError("Unexpected public split dimensions: %d/%d" % (len(all_tasks), len(groups)))

    quotas = {g: int(100 * len(v) / len(all_tasks)) for g, v in groups.items()}
    remainders = sorted(groups, key=lambda g: (-(100*len(groups[g])/len(all_tasks) - quotas[g]), g))
    for g in remainders[:100 - sum(quotas.values())]:
        quotas[g] += 1
    selected = []
    for group, items in groups.items():
        ranked = sorted(items, key=lambda x: hashlib.sha256((SEED + ":" + x[1]).encode()).hexdigest())
        selected += ranked[:quotas[group]]
    assert len(selected) == 100 and len(set(selected)) == 100

    full = manifest(all_tasks, commit, tree_sha, "full-642")
    pilot = manifest(selected, commit, tree_sha, "pre-registered-stratified-100")
    (ROOT / "swebench_pro_v2_full642.json").write_text(json.dumps(full, indent=2) + "\n")
    (ROOT / "swebench_pro_v2_pilot100.json").write_text(json.dumps(pilot, indent=2) + "\n")
    print(json.dumps({"source_commit": commit, "full_count": len(all_tasks),
                      "pilot_count": len(selected), "group_quotas": quotas}, indent=2))


if __name__ == "__main__":
    main()
