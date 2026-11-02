"""Retrieve explicit method cards. This tool does not infer the next scientific action."""
import argparse
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list",action="store_true")
    mode.add_argument("--ids",nargs="+")
    mode.add_argument("--tag")
    p.add_argument("--limit",type=int,default=3)
    a=p.parse_args()
    cards=json.loads(Path(__file__).with_name("METHOD_LIBRARY.json").read_text())["cards"]
    if a.list:
        print(json.dumps([{k:c[k] for k in ("id","name","tags","trigger")} for c in cards],ensure_ascii=False,indent=2))
        return
    if not 1<=a.limit<=6:
        p.error("--limit must be between 1 and 6")
    if a.ids:
        by_id={c["id"]:c for c in cards}
        missing=[i for i in a.ids if i not in by_id]
        if missing: p.error("Unknown method IDs: "+", ".join(missing))
        if len(a.ids)>6: p.error("Retrieve at most six explicit cards per request")
        selected=[by_id[i] for i in dict.fromkeys(a.ids)]
    else:
        selected=[c for c in cards if a.tag in c["tags"]][:a.limit]
        if not selected: p.error("No card has tag "+a.tag)
    print(json.dumps(selected,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
