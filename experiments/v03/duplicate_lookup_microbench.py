#!/usr/bin/env python3
"""Narrow, safe proof-of-concept: deduplicate identical read-only searches.
Not an agent token benchmark. No general shell-command execution.
"""
from pathlib import Path
import subprocess
import tempfile
import time
import json
import hashlib

def lookup(directory, pattern):
    return subprocess.check_output(["/usr/bin/grep", "-R", "-n", "--include=*.txt", "-F", pattern, str(directory)], text=True)

def run():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        for i in range(120):
            (root / f"doc_{i:03}.txt").write_text(("alpha one\nbeta two\n" * 140) + ("needle here\n" if i%30==0 else ""))
        # Repeat a search after unrelated downstream processing, without changing the files.
        requests=["needle"]*20
        start=time.perf_counter()
        original=[lookup(root,p) for p in requests]
        baseline_sec=time.perf_counter()-start
        cache={}
        actual_calls=0
        start=time.perf_counter()
        optimized=[]
        for p in requests:
            # This experiment deliberately establishes immutable inputs for the entire batch.
            key=(str(root),p)
            if key not in cache:
                cache[key]=lookup(root,p)
                actual_calls+=1
            optimized.append(cache[key])
        optimized_sec=time.perf_counter()-start
        assert original==optimized
        result={"scenario":"20 repeated identical read-only repository searches over immutable files","requests":len(requests),"baseline_process_invocations":len(requests),"deduplicated_process_invocations":actual_calls,"invocation_reduction_factor":len(requests)/actual_calls,"baseline_seconds":round(baseline_sec,4),"deduplicated_seconds":round(optimized_sec,4),"elapsed_speedup":round(baseline_sec/optimized_sec,2) if optimized_sec else None,"outputs_equal":True,"agent_token_savings":"not measured","scope":"controlled redundant lookup microbenchmark only"}
        print(json.dumps(result,indent=2))
        Path(__file__).with_name("results.json").write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__":
    run()
