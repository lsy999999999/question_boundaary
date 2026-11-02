"""Execution checks, not a multi-agent effectiveness benchmark."""
import json
from pathlib import Path
from engine import digest


def read(p):
    return json.loads(Path(p).read_text())


def audit(root):
    root = Path(root)
    errors, ids = [], []
    prompt_tokens = completion_tokens = reasoning_tokens = 0
    wires = sorted((root/'wire').iterdir())
    if len(wires) > 20:
        errors.append('request budget exceeded')
    for wire in wires:
        req, res = read(wire/'request.json'), read(wire/'response.json')
        payload, body = req['payload'], res['body']
        ids.append(body.get('id'))
        if payload['model'] != 'gpt-6-luna' or body['model'] != 'gpt-6-luna':
            errors.append('model mismatch '+wire.name)
        if payload['max_completion_tokens'] != 2048 or not 0 <= body['usage']['completion_tokens'] <= 2048:
            errors.append('token limit '+wire.name)
        if req['time_ns'] >= res['time_ns']:
            errors.append('request order '+wire.name)
        if body['choices'][0]['finish_reason'] != 'stop':
            errors.append('non-stop '+wire.name)
        prompt_tokens += body['usage']['prompt_tokens']
        completion_tokens += body['usage']['completion_tokens']
        reasoning_tokens += body['usage'].get('completion_tokens_details',{}).get('reasoning_tokens',0)
    if None in ids or len(set(ids)) != len(ids):
        errors.append('missing or duplicated response IDs')

    def bind(value, records):
        last = records[-1]
        body = read(root/last['wire']/'response.json')['body']
        content = body['choices'][0]['message']['content'].strip()
        if content.startswith('```'):
            content = content.split('\n',1)[1].rsplit('```',1)[0].strip()
        if json.loads(content) != value:
            errors.append('generation-content mismatch '+last['wire'])
    for round_no in range(3):
        dest = root/f'round_{round_no}'
        fc = read(dest/'forecast_commit.json')
        if fc['sha256'] != digest(fc['record']):
            errors.append('forecast hash '+str(round_no))
        design = read(dest/'design.json')
        bind(design['design'], design['generation_records'])
        if fc['record']['actions'] != design['design']['actions']:
            errors.append('design/forecast mismatch')
        for i in range(2):
            observation = read(root/'observations'/f'r{round_no}_experiment_{i}.json')
            if observation['time_ns'] <= fc['record']['time_ns']:
                errors.append('forecast after observation '+str(round_no))
            if observation['action'] != fc['record']['actions'][i]:
                errors.append('experiment input mismatch')
        for p in dest.glob('*_proposal.json'):
            node = read(p)
            value = {k:v for k,v in node.items() if k not in ('generation_records','round')}
            bind(value,node['generation_records'])
    final = read(root/'final_commit.json')
    if final['sha256'] != digest(final['record']):
        errors.append('final hash')
    bind(final['record']['decision'],final['record']['generation_records'])
    sealed = read(root/'sealed_predictions.json')
    if final['record']['time_ns'] >= sealed['time_ns']:
        errors.append('sealed evaluation before commitment')
    if any(read(w/'request.json')['time_ns'] >= final['record']['time_ns'] for w in wires):
        errors.append('model called after final commitment')
    return dict(passed=not errors, errors=errors, calls=len(wires),
        prompt_tokens=prompt_tokens, completion_tokens=completion_tokens,
        reasoning_tokens_included_in_completion=reasoning_tokens,
        checks=['generation binding','requested/returned model','token accounting','response IDs',
                'forecast hashes','forecast before observation','designed input executed',
                'final commitment before sealed evaluation','no post-evaluation model calls'],
        excluded=['scientific novelty','causal identification','multi-agent advantage','independent model identity'])


if __name__ == '__main__':
    import sys
    print(json.dumps(audit(sys.argv[1]),indent=2,ensure_ascii=False))
