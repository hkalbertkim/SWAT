#!/usr/bin/env python3
"""Manifest-locked SWAT full-task evaluation.

A task counts ONCE, even if it has multiple repetitions.
Tasks with missing, failed, or timed-out runs stay in the denominator.
No claim is permitted without the locked external task manifest and actual usage.
"""
import argparse
import collections
import json
import math
import pathlib
import statistics


def load(path):
    """Read observed task runs; refuse missing or fabricated metric fields."""
    rows = [json.loads(x) for x in pathlib.Path(path).read_text().splitlines() if x.strip()]
    required = ("dataset", "task_id", "repetition", "variant", "pass",
                "input_tokens", "cached_input_tokens", "output_tokens", "wall_seconds")
    for row in rows:
        for key in required:
            if key not in row:
                raise ValueError("Missing field: " + key)
        if not isinstance(row["dataset"], str) or not row["dataset"]:
            raise ValueError("Invalid dataset")
        if not isinstance(row["task_id"], str) or not row["task_id"]:
            raise ValueError("Invalid task_id")
        if row["variant"] not in ("baseline", "swat"):
            raise ValueError("Invalid variant")
        if type(row["pass"]) is not bool:
            raise ValueError("pass must be a boolean")
        if type(row["repetition"]) is not int or row["repetition"] < 1:
            raise ValueError("repetition must be a positive integer")
        for field in ("input_tokens", "cached_input_tokens", "output_tokens"):
            if type(row[field]) is not int or row[field] < 0:
                raise ValueError(field + " must be a nonnegative integer")
        value = row["wall_seconds"]
        if type(value) not in (float, int) or not math.isfinite(value) or value < 0:
            raise ValueError("invalid wall_seconds")
        if row["cached_input_tokens"] > row["input_tokens"]:
            raise ValueError("cached tokens exceed input")
    return rows


def load_manifest(path):
    manifest = json.loads(pathlib.Path(path).read_text())
    if not isinstance(manifest.get("tasks"), list) or not manifest["tasks"]:
        raise ValueError("manifest must contain selected tasks")
    repeats = manifest.get("expected_repetitions", 1)
    if type(repeats) is not int or repeats < 1:
        raise ValueError("invalid expected_repetitions")
    identities = set()
    for task in manifest["tasks"]:
        k = (task["dataset"], task["task_id"])
        if not all(isinstance(x, str) and x for x in k) or k in identities:
            raise ValueError("invalid or duplicate manifest task")
        identities.add(k)
    if "task_count" in manifest and manifest["task_count"] != len(manifest["tasks"]):
        raise ValueError("manifest task_count mismatch")
    return manifest


def total_tokens(row):
    return row["input_tokens"] + row["output_tokens"]


def calculate(rows, manifest=None):
    if manifest is None:
        # Historical ad hoc runs can be inspected but MUST NOT pass the public gate.
        keys = sorted({(r["dataset"], r["task_id"]) for r in rows})
        manifest = {"tasks": [{"dataset": d, "task_id": t} for d, t in keys],
                    "expected_repetitions": max((r["repetition"] for r in rows), default=1)}
        locked = False
    else:
        locked = True

    selected = [(t["dataset"], t["task_id"]) for t in manifest["tasks"]]
    selected_set = set(selected)
    repetitions = manifest.get("expected_repetitions", 1)
    observed = {}
    for row in rows:
        key = (row["dataset"], row["task_id"])
        if key not in selected_set:
            raise ValueError("Result not in locked manifest: " + str(key))
        if row["repetition"] > repetitions:
            raise ValueError("Unexpected repetition")
        full_key = (key, row["repetition"], row["variant"])
        if full_key in observed:
            raise ValueError("Duplicate observation: " + str(full_key))
        observed[full_key] = row

    results = []
    for dataset, task_id in selected:
        ratios = []
        all_pass = True
        all_present = True
        baseline_pass = True
        swat_pass = True
        raw_total = collections.Counter()
        for repetition in range(1, repetitions + 1):
            b = observed.get(((dataset, task_id), repetition, "baseline"))
            s = observed.get(((dataset, task_id), repetition, "swat"))
            if b is None or s is None:
                all_present = False
                all_pass = False
                baseline_pass = baseline_pass and (b is not None and b["pass"])
                swat_pass = swat_pass and (s is not None and s["pass"])
                continue
            baseline_pass = baseline_pass and b["pass"]
            swat_pass = swat_pass and s["pass"]
            if not b["pass"] or not s["pass"] or total_tokens(s) == 0 or total_tokens(b) == 0:
                all_pass = False
                continue
            ratios.append(total_tokens(b) / total_tokens(s))
            raw_total["baseline_total_tokens"] += total_tokens(b)
            raw_total["swat_total_tokens"] += total_tokens(s)
            raw_total["baseline_cached_input"] += b["cached_input_tokens"]
            raw_total["swat_cached_input"] += s["cached_input_tokens"]
        qualified = all_present and all_pass and len(ratios) == repetitions and statistics.median(ratios) >= 40
        results.append({
            "dataset": dataset, "task_id": task_id, "expected_repetitions": repetitions,
            "complete": all_present, "baseline_all_pass": bool(baseline_pass),
            "swat_all_pass": bool(swat_pass),
            "median_pair_ratio": round(statistics.median(ratios), 3) if ratios else None,
            "qualified_40x": qualified
        })

    n = len(results)
    achieved = sum(r["qualified_40x"] for r in results)
    by_dataset = {}
    for dataset in sorted(set(r["dataset"] for r in results)):
        group = [r for r in results if r["dataset"] == dataset]
        m = len(group)
        q = sum(r["qualified_40x"] for r in group)
        by_dataset[dataset] = {
            "selected_tasks": m, "qualified_40x": q,
            "required_70pct": math.ceil(m * 0.7 - 1e-12),
            "fraction": round(q / m, 4)
        }
    baseline_success = sum(r["baseline_all_pass"] for r in results)
    swat_success = sum(r["swat_all_pass"] for r in results)
    ready = locked and n >= 30 and repetitions >= 3
    return {
        "locked_manifest": locked,
        "selected_distinct_tasks": n,
        "expected_repetitions": repetitions,
        "observed_runs": len(observed),
        "expected_runs": 2 * n * repetitions,
        "fully_observed_tasks": sum(r["complete"] for r in results),
        "baseline_pass_tasks": baseline_success,
        "swat_pass_tasks": swat_success,
        "forty_x_target": {
            "required_fraction": 0.7,
            "all_selected_denominator": n,
            "required_task_count": math.ceil(n * 0.7 - 1e-12),
            "qualified_40x": achieved,
            "fraction": round(achieved / n, 4),
            "dataset_breakdown": by_dataset,
            "minimum_sample_met": ready,
            "achieved": bool(ready and achieved / n >= 0.7 and swat_success >= baseline_success),
        },
        "tasks": results,
        "note": "A 100-task subset is not proof for an entire 642-task benchmark. "
                "Both variants must pass every expected repeat; median paired token ratio >=40 per task. "
                "No inference from search microbenchmarks or absent data."
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonl", help="Real observed Codex/agent usage records")
    parser.add_argument("--manifest", help="Pre-registered tasks manifest JSON")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest(args.manifest) if args.manifest else None
    report = calculate(load(args.jsonl), manifest)
    if args.summary_only:
        report.pop("tasks")
    print(json.dumps(report, indent=2))
