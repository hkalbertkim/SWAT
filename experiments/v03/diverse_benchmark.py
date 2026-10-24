#!/usr/bin/env python3
"""Diverse deterministic read-only workloads. Results are NOT agent token savings."""
import pathlib, tempfile, subprocess, time, json, random, hashlib, statistics
rng=random.Random(20261024)
def search(root,term,mode):
    if mode=="grep":
        p=subprocess.run(["/usr/bin/grep","-R","-n","-F","--include=*.txt",term,str(root)],capture_output=True,text=True)
        return (p.returncode,p.stdout)
    if mode=="count":
        p=subprocess.run(["/usr/bin/grep","-R","-c","-F","--include=*.txt",term,str(root)],capture_output=True,text=True)
        return (p.returncode,p.stdout)
def trial(label,terms,nfiles,nlines,mode):
    with tempfile.TemporaryDirectory(prefix="swatdiverse_") as tmp:
        root=pathlib.Path(tmp)
        for i in range(nfiles):
            lines=["alpha common beta "+str(i)+"\n"]*nlines
            lines[i%nlines]="token_"+str(i%7)+" needle_"+str(i%13)+"\n"
            (root/f"doc_{i:04}.txt").write_text("".join(lines))
        basestart=time.perf_counter()
        base=[search(root,t,mode) for t in terms]
        base_elapsed=time.perf_counter()-basestart
        cache={};underlying=0
        optstart=time.perf_counter()
        out=[]
        for t in terms:
            key=(mode,t)
            if key not in cache:
                cache[key]=search(root,t,mode);underlying+=1
            out.append(cache[key])
        opt_elapsed=time.perf_counter()-optstart
        assert base==out
        return {"dataset":label,"files":nfiles,"queries":len(terms),"unique_queries":len(set(terms)),"baseline_calls":len(terms),"optimized_calls":underlying,"call_reduction_x":round(len(terms)/underlying,2),"latency_speedup_x":round(base_elapsed/opt_elapsed,2),"baseline_s":round(base_elapsed,4),"optimized_s":round(opt_elapsed,4),"exact_equivalence":True,"model_tokens":"not measured"}
def main():
    ds=[
        ("identical_retry_40",["needle_3"]*40,150,100,"grep"),
        ("hotspot_80_20",["needle_3"]*64+["token_"+str(i%4) for i in range(16)],150,100,"grep"),
        ("mixed_50pct",["needle_"+str(i%15) for i in range(60)],150,100,"grep"),
        ("mostly_unique",["query_"+str(i) for i in range(60)],150,100,"grep"),
        ("unique_only",["query_"+str(i) for i in range(40)],150,100,"grep"),
        ("count_hotspot",["token_2"]*48+["token_5"]*12,150,100,"count"),
        ("small_repo_repeated",["needle_2"]*30,12,60,"grep"),
        ("large_repo_repeated",["needle_2"]*30,500,200,"grep"),
    ]
    results=[trial(*d) for d in ds]
    for r in results:print(json.dumps(r),flush=True)
    pathlib.Path(__file__).with_name("diverse_results.json").write_text(json.dumps({"seed":20261024,"note":"Synthetic diverse controlled read-only workloads, no agent-model call or token benchmarks. No mutations within query batches. Avoid implying universal performance.","results":results},indent=2)+"\n")
if __name__=="__main__":main()
