"""Coordinate authorized hosts through existing SSH control connections."""
import argparse
import json
import shlex
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HOSTS={"a":{"host":"lsy@10.42.127.214","socket":"/private/tmp/ideas_ssh_a","root":"/home/lsy/theory_discovery_phase2_20261031"},"b":{"host":"lsyedith@10.77.110.187","socket":"/private/tmp/ideas_ssh_b","root":"/home/lsyedith/theory_discovery_phase2_20261031"}}


def remote(label, code):
    h=HOSTS[label]
    result=subprocess.run(["ssh","-S",h["socket"],"-o","BatchMode=yes","-o","ConnectTimeout=12",h["host"],"python3 -c "+shlex.quote(code)],capture_output=True,text=True,check=True,timeout=60)
    return json.loads(result.stdout)


def snapshot(label):
    root=HOSTS[label]["root"]
    return remote(label,f"import json; from pathlib import Path; p=Path({root!r}); print(json.dumps({{name:json.loads((p/name).read_text()) if (p/name).exists() else None for name in ['LIVE_STATUS.json','gate.json','FROZEN.json']}}))")


def main():
    p=argparse.ArgumentParser();p.add_argument("--pull",action="store_true");args=p.parse_args()
    states={}
    for label in HOSTS:
        states[label]=snapshot(label)
        (ROOT/f"remote_status_{label}.json").write_text(json.dumps(states[label],ensure_ascii=False,indent=2))
    gate=states["b"]["gate.json"]
    if gate is not None:
        frozen=states["a"]["FROZEN.json"]
        if not frozen or gate["source_hashes"]!=frozen["source_hashes"]:
            raise RuntimeError("Cross-host source mismatch; gate not forwarded")
        root=HOSTS["a"]["root"]
        remote("a",f"import json; from pathlib import Path; p=Path({root!r})/'ALLOW_EVAL.json'; data={gate!r}; tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(data)); tmp.replace(p); print(json.dumps({{'gate_forwarded':True,'passed':data['passed']}}))")
    if args.pull:
        for label,h in HOSTS.items():
            subprocess.run([sys.executable,str(ROOT/"sync_server.py"),"--pull","--host",h["host"],"--socket",h["socket"],"--remote",h["root"],"--destination",str(ROOT/"servers"/label)],check=True)
    print(json.dumps({label:s["LIVE_STATUS.json"] for label,s in states.items()},ensure_ascii=False,indent=2))


if __name__=="__main__":main()
