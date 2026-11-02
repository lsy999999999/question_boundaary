"""Two-host bounded execution. No credentials or remote authentication."""
import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from discovery.runner import AGENT_METHODS, BASELINE_METHODS, source_hashes, write_json
from discovery.report import build_report
from audit_results import audit

ROOT=Path(__file__).resolve().parent
MODEL=ROOT/"models/Qwen2.5-7B-Instruct"


def status(stage, **kwargs):
    data={"updated_at":datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),"stage":stage,**kwargs}
    write_json(ROOT/"LIVE_STATUS.json",data)
    print(json.dumps(data,ensure_ascii=False),flush=True)


def free_gpus():
    lines=subprocess.check_output(["nvidia-smi","--query-gpu=index,uuid,name,memory.total,memory.used,utilization.gpu","--format=csv,noheader,nounits"],text=True).splitlines()
    occupied={l.split(",")[0].strip() for l in subprocess.check_output(["nvidia-smi","--query-compute-apps=gpu_uuid,pid,used_memory","--format=csv,noheader"],text=True).splitlines() if l.strip()}
    devices=[]
    for line in lines:
        index,uuid,name,total,used,util=[v.strip() for v in line.split(",")]
        if uuid not in occupied and int(used)<500 and int(util)<5 and int(total)>22000:
            devices.append({"index":int(index),"uuid":uuid,"name":name,"total_mb":int(total)})
    return sorted(devices,key=lambda g:-g["total_mb"])


def validate_model():
    expected=json.loads((ROOT/"expected_model_identity.json").read_text())
    actual={}
    for name,identity in expected["files"].items():
        p=MODEL/name
        h=hashlib.sha256()
        with p.open("rb") as stream:
            for block in iter(lambda:stream.read(8*1024*1024),b""):h.update(block)
        actual[name]={"bytes":p.stat().st_size,"sha256":h.hexdigest()}
        if actual[name]!=identity:raise RuntimeError(f"Model identity mismatch: {name}")
    write_json(ROOT/"model_identity.json",{**expected,"files":actual,"matches_first_server":True})


def check_sources():
    frozen=ROOT/"FROZEN.json"
    hashes=source_hashes()
    if frozen.exists():
        if json.loads(frozen.read_text())["source_hashes"]!=hashes:raise RuntimeError("Frozen source changed; new version required")
    else:write_json(frozen,{"protocol":"v4-source-schema","source_hashes":hashes,"dev_seed":201,"eval_seeds":[31,32,33],"max_new_tokens":512,"batch_size":1,"rounds":3})


def run_stage(python, split, role, model):
    check_sources()
    methods=list(BASELINE_METHODS if role=="baselines" else AGENT_METHODS)
    out=ROOT/"runs"/f"{'baseline_' if role=='baselines' else ''}{split}_v4"
    out.mkdir(parents=True,exist_ok=True)
    devices=free_gpus()[:5] if role=="gpu" else []
    if role=="gpu" and not devices:raise RuntimeError("No unused GPU available")
    groups=[methods] if role=="baselines" else [methods[i::len(devices)] for i in range(len(devices))]
    workers=[]
    started=time.monotonic()
    try:
        for index,group in enumerate(groups):
            gpu=devices[index] if role=="gpu" else None
            if gpu and gpu["uuid"] not in {g["uuid"] for g in free_gpus()}:
                raise RuntimeError("Selected GPU became occupied before launch")
            env=dict(os.environ,CUDA_VISIBLE_DEVICES=gpu["uuid"] if gpu else "",OMP_NUM_THREADS="1",OPENBLAS_NUM_THREADS="1",MKL_NUM_THREADS="1",TOKENIZERS_PARALLELISM="false",HF_HUB_OFFLINE="1",TRANSFORMERS_OFFLINE="1",PYTHONUNBUFFERED="1")
            cmd=[python,"-m","discovery.runner","--split",split,"--seeds","201" if split=="dev" else "31,32,33","--methods",",".join(group),"--output",str(out),"--model",str(model),"--rounds","3","--batch-size","1","--max-new-tokens","512","--backend","cuda","--threads","4"]
            label="_".join(group)
            with (out/f"worker_{label}.log").open("a") as log:
                child=subprocess.Popen(cmd,cwd=ROOT,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            workers.append({"process":child,"methods":group,"gpu":gpu})
        write_json(out/"workers.json",[{"pid":w["process"].pid,"methods":w["methods"],"gpu":w["gpu"]} for w in workers])
        while True:
            state=[{"pid":w["process"].pid,"methods":w["methods"],"returncode":w["process"].poll()} for w in workers]
            counts={m:len(list((out/m).glob("*/result.json"))) for m in methods}
            status(f"running_{split}",role=role,directory=str(out),completed=counts,workers=state)
            if any(w["process"].poll() not in (None,0) for w in workers):raise RuntimeError("Worker failed; inspect preserved logs")
            if all(w["process"].poll()==0 for w in workers):break
            if time.monotonic()-started>21600:raise TimeoutError("Six hour stage limit")
            time.sleep(20)
    finally:
        for w in workers:
            if w["process"].poll() is None:os.killpg(w["process"].pid,signal.SIGTERM)
        for w in workers:
            try:w["process"].wait(timeout=20)
            except subprocess.TimeoutExpired:os.killpg(w["process"].pid,signal.SIGKILL)
    summary=build_report(out,methods)
    if not summary["complete"]:raise RuntimeError("Stage missing task results")
    return summary,audit(out)


def gate(summary, audited):
    reasons=[]
    for method,row in summary["methods"].items():
        if row["generation_calls"] and row["invalid_outputs"]/row["generation_calls"]>0.25:reasons.append(f"{method}: invalid outputs >25%")
    if audited["source_counts"]["structured"]["valid_non_none"]<1:reasons.append("structured: no valid nonempty mapping")
    if audited["representation_changes"]["structured"]["tasks_with_revision"]<1:reasons.append("structured: no representation revision")
    for key in ("forecast_order_errors","forecast_hash_errors","evaluation_order_errors"):
        if audited[key]:reasons.append(key)
    return {"passed":not reasons,"reasons":reasons,"criterion":"Predeclared PLAN.md invocation/format gate; semantic correctness remains separate.","source_hashes":source_hashes()}


def main():
    p=argparse.ArgumentParser();p.add_argument("--role",choices=["gpu","baselines"],required=True);p.add_argument("--python",required=True);p.add_argument("--model",type=Path,default=MODEL)
    args=p.parse_args()
    lock=(ROOT/"supervisor.lock").open("w")
    fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    (ROOT/"supervisor.pid").write_text(str(os.getpid()))
    try:
        if args.role=="gpu":
            started=time.monotonic()
            while not ((ROOT/"ENV_READY").exists() and (MODEL/"DOWNLOAD_COMPLETE.json").exists()):
                status("waiting_environment",env_ready=(ROOT/"ENV_READY").exists(),model_ready=(MODEL/"DOWNLOAD_COMPLETE.json").exists())
                if time.monotonic()-started>7200:raise TimeoutError("Two hour preparation limit")
                time.sleep(20)
            status("validating_model_identity")
            validate_model()
        check_sources()
        env=dict(os.environ,OPENBLAS_NUM_THREADS="1",OMP_NUM_THREADS="1")
        with (ROOT/"protocol_tests.log").open("w") as log:
            subprocess.run([args.python,"-m","unittest","discover","-s","tests","-v"],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)
        with (ROOT/"environment_freeze.txt").open("w") as f:
            subprocess.run([args.python,"-m","pip","freeze"],stdout=f,check=True)
        summary,audited=run_stage(args.python,"dev",args.role,args.model)
        if args.role=="gpu":
            result=gate(summary,audited);write_json(ROOT/"gate.json",result)
            if not result["passed"]:
                status("development_gate_failed",gate=result);return
            status("development_gate_passed",gate=result)
        else:
            start=time.monotonic()
            while not (ROOT/"ALLOW_EVAL.json").exists():
                status("baseline_dev_complete_waiting_gate",summary=str(ROOT/"runs/baseline_dev_v4/summary.json"))
                if time.monotonic()-start>21600:raise TimeoutError("Waiting for GPU development gate exceeded six hours")
                time.sleep(20)
            receipt=json.loads((ROOT/"ALLOW_EVAL.json").read_text())
            if not receipt.get("passed") or receipt.get("source_hashes")!=source_hashes():raise RuntimeError("Gate receipt invalid or source mismatch")
        final,audited=run_stage(args.python,"eval",args.role,args.model)
        status("completed",role=args.role,total_results=final["total_results"],summary=str(ROOT/"runs"/f"{'baseline_' if args.role=='baselines' else ''}eval_v4/summary.json"))
    except Exception as exc:
        status("failed",role=args.role,error=repr(exc));raise


if __name__=="__main__":main()
