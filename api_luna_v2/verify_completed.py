import hashlib,json,sys,re
from pathlib import Path
from collections import Counter
root=Path(sys.argv[1])
original=Path('/home/lsyedith/theory_discovery_phase2_v4_20261031')
report={'stage':json.loads((root/'LIVE_STATUS.json').read_text()),'checks':{},'failures':[]}
for split,expected in [('dev',4),('eval',24)]:
 run=root/'runs'/split
 manifest=json.loads((run/'manifest.json').read_text())
 rows=[json.loads(f.read_text()) for f in run.glob('*/*/result.json')]
 counts=dict(Counter(r['method'] for r in rows))
 for method in ['state_fixed','history_cv','plain','retrieval','structured','no_active','shuffled']:
  if counts.get(method)!=expected:report['failures'].append(f'{split}/{method}: incomplete')
 for r in rows:
  if r['n_experiments']!=6 or r['rounds']!=3:report['failures'].append(f'{split}/{r["task_id"]}: observation budget')
  if r['method'] not in ['state_fixed','history_cv'] and r['generation_calls']!=4:report['failures'].append(f'{split}/{r["task_id"]}: generation budget')
 audit=json.loads((run/'audit.json').read_text())
 for field in ['forecast_order_errors','forecast_hash_errors','evaluation_order_errors']:
  if audit[field]:report['failures'].append(f'{split}: {field}')
 baseline=json.loads((run/'baseline_equivalence.json').read_text())
 if not all(x['matched'] for x in baseline):report['failures'].append(f'{split}: baseline mismatch')
 hashes=manifest['source_hashes'];actual={name:hashlib.sha256((root/'frozen'/name).read_bytes()).hexdigest() for name in hashes}
 if hashes!=actual:report['failures'].append(f'{split}: frozen source mismatch')
 unchanged=all(hashlib.sha256((original/name).read_bytes()).hexdigest()==digest for name,digest in hashes.items())
 if not unchanged:report['failures'].append(f'{split}: original source changed')
 bindings=[];calls=[]
 for f in run.glob('*/*/request_*.json'):
  item=json.loads(f.read_text());c=item['response'];wire=root/c['wire_record'];q=json.loads((wire/'request.json').read_text());response=json.loads((wire/'response.json').read_text())['body']
  ok=(q['payload']['messages']==item['messages'] and q['payload'].get('max_completion_tokens')==512 and q['payload'].get('temperature')==0 and q['payload']['model']=='gpt-6-luna' and response['model']=='gpt-6-luna' and response['choices'][0]['message'].get('content','')==c['text'] and response['usage']['completion_tokens']==c['output_tokens'] and response['usage']['completion_tokens']<=512)
  if not ok:report['failures'].append(f'{split}: binding failure {f.relative_to(root)}')
  bindings.append(ok);calls.append(c)
 response_files=list((root/'wire'/split).glob('*/response.json'));errors=list((root/'wire'/split).glob('*/error.json'))
 if len(calls)!=expected*5*4 or len(response_files)!=len(calls) or errors:report['failures'].append(f'{split}: unaccounted requests')
 report['checks'][split]={'results':len(rows),'counts':counts,'calls':len(calls),'wire_responses':len(response_files),'wire_errors':len(errors),'all_request_bindings_match':all(bindings),'baseline_equivalence':len(baseline),'original_sources_unchanged':unchanged,'invalid_outputs':sum(r['invalid_outputs'] for r in rows),'finish_reasons':dict(Counter(c['finish_reason'] for c in calls)),'max_reported_completion_tokens':max(c['output_tokens'] for c in calls),'unique_api_response_ids':len(set(c['api_response_id'] for c in calls))}
files=[]
for prefix in ['runs','wire','frozen']:
 for f in sorted((root/prefix).rglob('*')):
  if f.is_file() and '__pycache__' not in str(f):files.append(f)
files.extend(root/n for n in ['api_transport.py','PLAN.md','ANALYSIS_PLAN.md','gate.json','LIVE_STATUS.json','verify_completed.py'])
items=[{'path':str(f.relative_to(root)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size} for f in sorted(files)]
secret_pattern=re.compile(r'sk-[A-Za-z0-9_-]{40,}')
for f in files:
 if f.suffix=='.json' and secret_pattern.search(f.read_text()):report['failures'].append('Credential-like text in '+str(f.relative_to(root)))
report['file_count']=len(items);report['files']=items
report['aggregate_sha256']=hashlib.sha256(json.dumps(items,sort_keys=True,separators=(',',':')).encode()).hexdigest()
report['passed']=not report['failures'] and report['stage']['stage']=='completed'
(root/'REMOTE_INTEGRITY.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
if not report['passed']:raise SystemExit(1)
