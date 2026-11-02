"""Post-freeze provenance audit only. Scientific assessment is a separate artifact."""
import json
import broker as b

def main():
    rows=[];materials=[];recovered=[]
    for n in ['A1','A2','B1','B2','C1','C2']:
        run=b.ROOT/'runs'/n;cfg=b.read(run/'config.json');s=b.state(run)
        assert b.verify(run),n+' freeze changed'
        assert s['counters']['replies']==6
        assert all(s['counters'][k]<=cfg[k+'_cap'] for k in ['search','compute'])
        materials.append(cfg['material_sha256'])
        assert b.sha(run/'materials.json')==cfg['material_sha256']
        for e in s['actor_events']:
            assert b.sha(run/'inputs'/f"{e['label']}.json")==e['input_sha256']
            if b.sha(run/'replies'/f"{e['label']}.json")!=e['reply_sha256']:
                recovery=b.ROOT/'evaluation/provenance_recovered'/f"{n}_{e['label']}_ingested.json"
                assert recovery.exists() and b.sha(recovery)==e['reply_sha256']
                assert b.read(recovery)==e['reply']
                recovered.append(dict(run=n,label=e['label'],reason='Root ingested before actor finished; actor subsequently revised file. Both final file and hash-exact ingested bytes preserved.',recovery=str(recovery.relative_to(b.ROOT))))
            inp=b.read(run/'inputs'/f"{e['label']}.json")
            text=json.dumps(inp)
            assert 's44286-026-00454' not in text
            assert 'withheld_late_timepoints' not in text
            assert not any(x['time_h']>24 for x in inp['evidence']['initial_measurements.json'])
        for t in s['tools']:
            result=t['result']
            if t['type']=='search':
                for source in result.get('sources',[]):assert source['first_publication_date']<=b.CUTOFF
                if result.get('raw_sha256'):assert b.sha(run/'tools'/t['id']/'raw.json')==result['raw_sha256']
            if t['type']=='compute' and result.get('code_sha256'):
                assert (run/'tools'/t['id']/'submitted.py').read_text()==t['request']['code']
                assert b.sha(run/'tools'/t['id']/'submitted.py')==result['code_sha256']
                assert b.sha(run/'tools'/t['id']/'data.json')==result['data_sha256']
        rows.append(dict(run=n,counters=s['counters'],frozen=True,
          successful_computations=sum(t['type']=='compute' and t['result']['status']=='executed' for t in s['tools']),
          failed_or_blocked_tools=[t['id'] for t in s['tools'] if t['result']['status'] not in {'returned','executed'}],
          search_source_counts=[len(t['result'].get('sources',[])) for t in s['tools'] if t['type']=='search'],
          literature_use_records=len(s['literature_use']),
          protocol_errors=[dict(reply=e['label'],errors=e['protocol_errors']) for e in s['actor_events'] if e.get('protocol_errors')],
          adjudications=s['adjudications'],task_statuses={k:v['status'] for k,v in s['tasks'].items()}))
    assert len(set(materials))==1
    out=dict(trace_reconstructable=True,clean_live_ingestion=not recovered,recovered_races=recovered,runs=rows,total_research_replies=sum(x['counters']['replies'] for x in rows),
       total_searches=sum(x['counters']['search'] for x in rows),total_compute_requests=sum(x['counters']['compute'] for x in rows),
       material_hash=materials[0],extra_model_reviews=0,model_retries=0,limitations=['Formal provenance checks do not establish scientific correctness','actor tool obedience is instruction based; full model-provider inference trace/token usage unavailable','the shared output schema itself encourages construction in all arms; comparison only tests added scheduling paragraph','broker intake format repair applied consistently; original code hash and patch record retained'])
    b.dump(b.ROOT/'PROVENANCE_AUDIT.json',out)
    print(json.dumps({k:v for k,v in out.items() if k!='runs'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
