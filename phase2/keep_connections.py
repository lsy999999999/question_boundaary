"""Keep authorized SSH channels alive during bounded unattended execution."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from manage_hosts import HOSTS

ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument("--stop",action="store_true");args=p.parse_args()
pidfile=ROOT/"connection_pids.json"
if args.stop:
    if pidfile.exists():
        for pid in json.loads(pidfile.read_text()).values():
            try:os.kill(pid,15)
            except ProcessLookupError:pass
        pidfile.unlink()
else:
    if pidfile.exists():raise RuntimeError("Connection keepers already registered")
    pids={}
    for label,h in HOSTS.items():
        with (ROOT/f"connection_{label}.log").open("a") as log:
            child=subprocess.Popen(["ssh","-S",h["socket"],"-o","BatchMode=yes","-o","ConnectTimeout=12","-o","ServerAliveInterval=30",h["host"],"sleep 43200"],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        pids[label]=child.pid
    pidfile.write_text(json.dumps(pids,indent=2))
    print(json.dumps(pids))
