"""Dependency-free launcher: wait for preparation, then exec the supervisor."""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--role",choices=["baselines","gpu"],required=True)
args=p.parse_args()
(root/"launcher.pid").write_text(str(os.getpid()))
if args.role=="gpu":
    started=time.monotonic()
    while not ((root/"ENV_READY").exists() and (root/"models/Qwen2.5-7B-Instruct/DOWNLOAD_COMPLETE.json").exists()):
        record={"stage":"preparing_environment","role":"gpu","updated_at":datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),"env_ready":(root/"ENV_READY").exists(),"model_ready":(root/"models/Qwen2.5-7B-Instruct/DOWNLOAD_COMPLETE.json").exists(),"launcher_pid":os.getpid()}
        if time.monotonic()-started>7200:
            record.update(stage="failed",error="Preparation exceeded two hours")
        tmp=root/"LIVE_STATUS.tmp";tmp.write_text(json.dumps(record,indent=2));tmp.replace(root/"LIVE_STATUS.json")
        if record["stage"]=="failed":raise RuntimeError(record["error"])
        time.sleep(20)
    python=str(root/".env_gpu/bin/python")
    model=str(root/"models/Qwen2.5-7B-Instruct")
else:
    python="/home/lsy/theory_discovery_20261031/.venv/bin/python"
    model="/home/lsy/theory_discovery_20261031/models/Qwen2.5-7B-Instruct"
os.chdir(root)
os.execv(python,[python,str(root/"supervise.py"),"--role",args.role,"--python",python,"--model",model])
