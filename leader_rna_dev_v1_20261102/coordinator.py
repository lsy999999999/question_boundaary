"""Small artifact and budget broker; all scientific decisions remain actor outputs."""
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'real_case_blind_20261102'

def save(path,data):
    with path.open('x') as f:
        if isinstance(data,str):f.write(data)
        else:json.dump(data,f,ensure_ascii=False,indent=2)

def event(kind, payload):
    rec=dict(time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind=kind,**payload)
    with (ROOT/'curator/events.jsonl').open('a') as f:f.write(json.dumps(rec,ensure_ascii=False)+'\n')

def release(category):
    filenames=dict(sequence='sequence_measurements.json',fractionation='fraction_dev.json',phase_composition='phase_measurements.json',motion='mobility_dev.json')
    path=ROOT/'agent_visible'/filenames[category]
    if path.exists():return path
    events=read_events()
    used=sum(e['kind']=='evidence_release' for e in events)
    if used>=4:raise RuntimeError('evidence budget exhausted')
    content=(OLD/'curator/evidence'/filenames[category]).read_text()
    save(path,content)
    event('evidence_release',dict(category=category,path=str(path.relative_to(ROOT)),source=str(OLD/'curator/evidence'/filenames[category]),sha256=hashlib.sha256(content.encode()).hexdigest()))
    return path

def read_events():
    p=ROOT/'curator/events.jsonl'
    return [json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []

def cards(ids):
    all_cards=json.loads((ROOT/'frozen_prompts/METHOD_LIBRARY.json').read_text())['cards']
    byid={c['id']:c for c in all_cards}
    return [byid[i] for i in ids]

def bundle_one():
    evidence=release('sequence')
    data=(ROOT/'frozen_prompts/RESEARCHER_SYSTEM_PROMPT.md').read_text()
    data+='\nCASE_BRIEF:\n'+(ROOT/'agent_visible/case_brief.md').read_text()
    data+='\nOBSERVATIONS:\n'+(ROOT/'agent_visible/initial_measurements.json').read_text()
    data+='\nLEADER_TASK:\n'+(ROOT/'transcripts/leader_01.md').read_text()
    data+='\nMETHOD_CARDS:\n'+json.dumps(cards(['M02','M15','M33']),ensure_ascii=False,indent=2)
    data+='\nRELEASED_SEQUENCE_MEASUREMENTS:\n'+evidence.read_text()
    data+='\nCoordinator note: A is the reference template; the measured read fractions describe B. These are DNA reads, not post-transcription RNA concentrations. No folding interpretations are supplied. Numerical calculations are mediated: request the exact calculation and do not pretend it has run. Your reply is researcher turn 1 of at most 6. Do not directly use further tools or project memory.\n'
    dest=ROOT/'agent_visible/researcher_01.md'
    save(dest,data)
    event('researcher_bundle',dict(turn=1,path=str(dest.relative_to(ROOT)),method_ids=['M02','M15','M33']))
    print(str(dest))

if __name__=='__main__':
    if sys.argv[1:] == ['bundle-one']:bundle_one()
    else:raise SystemExit('Supported command: bundle-one')
