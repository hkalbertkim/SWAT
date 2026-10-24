#!/usr/bin/env python3
"""SWAT full-task paired evaluation. Input JSONL contains genuine observed agent runs.
Never imputes missing tokens or reports 20x from synthetic search-only tests.
"""
import argparse,json,statistics,pathlib,collections
def load(path):
    rows=[json.loads(line) for line in pathlib.Path(path).read_text().splitlines() if line.strip()]
    for r in rows:
        for key in ("dataset","task_id","variant","pass","input_tokens","cached_input_tokens","output_tokens","wall_seconds"):
            if key not in r: raise ValueError("Missing field "+key)
        if r["variant"] not in ("baseline","swat"):raise ValueError("unknown variant")
        if r["cached_input_tokens"]>r["input_tokens"]:raise ValueError("invalid cached > input")
        if min(r["input_tokens"],r["cached_input_tokens"],r["output_tokens"],r["wall_seconds"])<0:raise ValueError("negative metric")
    return rows
def calculate(rows):
    pairs=collections.defaultdict(dict)
    for r in rows:
        key=(r["dataset"],r["task_id"],r.get("repetition",1))
        if r["variant"] in pairs[key]:raise ValueError("duplicate variant in pair "+str(key))
        pairs[key][r["variant"]]=r
    complete=[v for v in pairs.values() if len(v)==2]
    def token(r):return r["input_tokens"]+r["output_tokens"]
    def uncached(r):return r["input_tokens"]-r["cached_input_tokens"]+r["output_tokens"]
    baseline_success=sum(v["baseline"]["pass"] for v in complete)
    swat_success=sum(v["swat"]["pass"] for v in complete)
    def agg(metric):
        a=sum(metric(v["baseline"]) for v in complete)
        b=sum(metric(v["swat"]) for v in complete)
        return {"baseline":a,"swat":b,"ratio":round(a/b,3) if b>0 else None}
    return {"complete_pairs":len(complete),"unpaired":len(pairs)-len(complete),"pass_counts":{"baseline":baseline_success,"swat":swat_success},"total_tokens":agg(token),"uncached_plus_output_tokens":agg(uncached),"elapsed_seconds":agg(lambda r:r["wall_seconds"]),"twenty_x_full_task_tokens_proven":len(complete)>=30 and swat_success>=baseline_success and (agg(token)["ratio"] or 0)>=20,"notes":"No pricing assumption; token totals are not equivalent to billed cost. Check multi-run/task-stratified performance before making claims."}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("jsonl");a=p.parse_args()
    print(json.dumps(calculate(load(a.jsonl)),indent=2))
