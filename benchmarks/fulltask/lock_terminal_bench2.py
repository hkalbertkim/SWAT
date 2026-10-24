#!/usr/bin/env python3
"""Create locked Terminal-Bench 2.0 manifest from official pinned Git tree."""
import json
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent
REPO = "harbor-framework/terminal-bench-2"

def api(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=45)
    if p.returncode:
        raise RuntimeError(p.stderr[-250:])
    return json.loads(p.stdout)

def main():
    meta = api("repos/" + REPO + "/commits/main")
    commit = meta["sha"]
    tree_sha = meta["commit"]["tree"]["sha"]
    tree = api("repos/" + REPO + "/git/trees/" + tree_sha + "?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("Truncated Git tree")
    ids = sorted({x["path"].split("/")[0] for x in tree["tree"]
                  if x.get("type") == "blob" and x["path"].count("/") == 1
                  and x["path"].endswith("/task.toml")})
    if len(ids) != 89:
        raise RuntimeError("Unexpected Terminal-Bench 2 count: " + str(len(ids)))
    m = {
        "benchmark": "Terminal-Bench 2.0",
        "split": "full-89", "source": "https://github.com/" + REPO,
        "source_commit": commit, "source_tree": tree_sha,
        "expected_repetitions": 3, "task_count": len(ids),
        "tasks": [{"dataset": "terminal-bench-2.0", "task_id": item} for item in ids],
        "claim_policy": "Official isolated verifier required; read-only task listing is not evaluation."
    }
    (ROOT / "terminal_bench2_full89.json").write_text(json.dumps(m, indent=2) + "\n")
    print(json.dumps({"repo": REPO, "commit": commit, "tasks": len(ids),
                      "required_70pct": 63}, indent=2))

if __name__ == "__main__":
    main()
