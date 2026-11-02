"""Independent retrospective Luna review. Never evaluates or changes old scores."""
import getpass,json,time,sys,hashlib
from pathlib import Path
from engine import write
from numerics import validate_evidence_ownership
from transport import Luna


if __name__=='__main__':
    root=Path(sys.argv[1]);source=Path(sys.argv[2]);root.mkdir(parents=True,exist_ok=False)
    payload=json.loads(source.read_text())
    write(root/'manifest.json',dict(time_ns=time.time_ns(),scope='Retrospective evidence ownership review, no new experiments or scores',
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(__file__).parent.glob('*.py'))}))
    key=getpass.getpass('API key (hidden): ');client=Luna(key,root)
    def validate(v):
        ids=set(payload['models'])
        if len(v['updates'])!=len(ids) or {u['id'] for u in v['updates']}!=ids: raise ValueError('Review each model exactly once')
        for u in v['updates']:
            if u['status'] not in ('active','weakened','undistinguished','retired'): raise ValueError('Invalid status')
            if not u['evidence_ids']: raise ValueError('Cite evidence')
            validate_evidence_ownership(u,payload['evidence'])
            if not any(e['id'] in u['evidence_ids'] and e.get('owner_model_id')==u['id'] for e in payload['evidence']): raise ValueError('Include evidence owned by this model')
    instruction='''You are gpt-6-luna reviewing an already completed development run. This is a separate
retrospective evidence review, NOT a new experiment or a chance to rewrite old predictions/scores.
No hidden equations or sealed-input outcomes are provided. Every failure explicitly carries its owner
model and fit version. An observation name is NOT the model that made the prediction. Never attribute
another model's prediction failure to the model being assessed. Use prospective model-owned errors
and grouped-fit diagnostics. Distinguish results on one intervention pair from aggregate grouped CV.
For each model return one status with 1-2 exact evidence IDs and a Chinese reason <=60 characters.
Keep input-specific evidence local; no universal law or physical latent-state identification claim.
JSON: {"updates":[{"id":"model id","status":"active|weakened|undistinguished|retired",
"evidence_ids":["exact id"],"reason":"..."}],"summary":"Chinese, <=120 characters"}.'''
    try:
        decision,records=client.structured('owned_evidence_review',instruction,payload,validate)
        write(root/'review.json',dict(time_ns=time.time_ns(),value=decision,generation_records=records))
        write(root/'LIVE_STATUS.json',dict(stage='completed',time_ns=time.time_ns(),calls=client.count))
        print(json.dumps(decision,ensure_ascii=False),flush=True)
    except Exception as exc:
        write(root/'LIVE_STATUS.json',dict(stage='failed',time_ns=time.time_ns(),calls=client.count,error=str(exc).replace(key,'[redacted]')))
        raise SystemExit(1) from None
