"""Explicit orchestration helpers; actor model calls use collaboration tool."""
import json
import sys
import broker as b

def next_input(name,role,label,final=False):
    run=b.ROOT/'runs'/name;p=b.build_input(run,role,label,final)
    prompt=f'Act as RNA research {role.upper()}. Read ONLY {p}. Follow its permissions/instructions/schema. Inspect the large input in chunks as needed, including current state and actual tool returns; avoid silently truncating evidence. Write complete JSON to {run}/replies/{label}.json. Use exec only for reading that input and writing reply; no memory/project exploration/network/scientific computation/delegation. Put tool requests in JSON for broker. '+('This is your FINAL reply: check actual results and submit your final candidate/adjudication and dissent. Do not claim a computation succeeded if it did not.' if final else 'Continue the current candidate/gap task; executor or leader follows after broker tools.')
    b.dump(run/'inputs'/f'{label}_invocation.txt',prompt)
    return prompt

if __name__=='__main__':
    action=sys.argv[1]
    if action=='next':print(next_input(sys.argv[2],sys.argv[3],sys.argv[4],len(sys.argv)>5))
    elif action=='summary':
        for name in sys.argv[2:]:
            r=b.ROOT/'runs'/name;s=b.state(r)
            print(json.dumps(dict(run=name,counters=s['counters'],candidates=[dict(id=k,target=v.get('target'),equations=v.get('equations'),predictions=v.get('predictions')) for k,v in s['candidates'].items()],tools=[dict(id=t['id'],type=t['type'],status=t['result']['status'],url=t['result'].get('url'),output_path=t['result'].get('output_path'),stdout=t['result'].get('stdout','')[:1500],stderr=t['result'].get('stderr')) for t in s['tools']],finals=s['finals']),ensure_ascii=False))
