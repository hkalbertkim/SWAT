#!/usr/bin/env python3
"""Read-only search replay against pinned public GitHub repositories."""
import subprocess, pathlib, time, json
ROOT=pathlib.Path(__file__).resolve().parents[2]
STORE=ROOT/".benchmark/public-repos"
SOURCES=[
("requests","https://github.com/psf/requests.git",["Session","Response","Request","timeout","verify"]),
("click","https://github.com/pallets/click.git",["Context","Option","Argument","Command","Parameter"]),
("flask","https://github.com/pallets/flask.git",["Flask","request","Blueprint","Response","session"]),
]
def rg(root,term):
    # Search only tracked Python sources; matching output is byte-for-byte reused.
    p=subprocess.run(["git","grep","-n","-F",term,"--","*.py"],cwd=root,capture_output=True,text=True)
    return p.returncode,p.stdout
def benchmark(root,terms,label):
    started=time.perf_counter()
    original=[rg(root,t) for t in terms]
    a=time.perf_counter()-started
    started=time.perf_counter()
    cache={};observed=[]
    for t in terms:
        if t not in cache:cache[t]=rg(root,t)
        observed.append(cache[t])
    b=time.perf_counter()-started
    assert original==observed
    return {"pattern":label,"calls":len(terms),"unique_calls":len(set(terms)),"invocation_reduction_x":round(len(terms)/len(set(terms)),2),"elapsed_speedup_x":round(a/b,2),"baseline_seconds":round(a,4),"reuse_seconds":round(b,4),"exact_match":True}
def main():
    STORE.mkdir(parents=True,exist_ok=True)
    results=[]
    for name,url,terms in SOURCES:
        path=STORE/name
        if not (path/".git").exists():
            p=subprocess.run(["git","clone","--depth","1","--quiet",url,str(path)],capture_output=True,text=True,timeout=60)
            if p.returncode:raise RuntimeError(name+": "+p.stderr[-500:])
        commit=subprocess.check_output(["git","rev-parse","HEAD"],cwd=path,text=True).strip()
        scenarios=[("heavy-retry",[terms[0]]*30),
                   ("mixed-retry",[terms[i%3] for i in range(30)]),
                   ("mostly-unique",terms+["__swat_absent_"+str(i) for i in range(25)])]
        for label,queries in scenarios:
            value=benchmark(path,queries,label)
            value.update({"repo":name,"upstream":url,"commit":commit})
            results.append(value)
            print(json.dumps(value),flush=True)
    dest=pathlib.Path(__file__).with_name("real_repo_results.json")
    dest.write_text(json.dumps({"results":results,"scope":"Real public repositories, synthetic query sequences, read-only git grep, no model agent tokens measured","date":"2026-10-24"},indent=2)+"\n")
if __name__=="__main__":main()
