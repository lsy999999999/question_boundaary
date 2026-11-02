"""Real Luna calls only. Credentials exist only in process memory."""
import json
import time
import urllib.error
import urllib.request
from engine import write

MODEL = 'gpt-6-luna'
ENDPOINT = 'https://sub.krisrosea.top/v1/chat/completions'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Luna:
    def __init__(self, key, root):
        self.key, self.root, self.count = key, root, 0

    def ask(self, purpose, system, payload):
        self.count += 1
        if self.count > 20:
            raise RuntimeError('20-call hard limit reached')
        dest = self.root / 'wire' / f'{self.count:03d}_{purpose}'
        request = dict(model=MODEL, temperature=0, max_completion_tokens=2048,
            response_format={'type':'json_object'}, messages=[dict(role='system', content=system),
                      dict(role='user', content=json.dumps(payload, ensure_ascii=False))])
        write(dest / 'request.json', dict(time_ns=time.time_ns(), endpoint=ENDPOINT, payload=request))
        req = urllib.request.Request(ENDPOINT, data=json.dumps(request).encode(), headers={
            'Authorization': 'Bearer '+self.key, 'Content-Type': 'application/json'})
        started = time.monotonic()
        try:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=120) as response:
                body = json.loads(response.read().decode().replace(self.key, '[redacted]'))
            write(dest / 'response.json', dict(time_ns=time.time_ns(), body=body,
                elapsed_seconds=time.monotonic()-started))
            if body.get('model') != MODEL:
                raise RuntimeError('Returned model differs from gpt-6-luna')
            choices, usage = body.get('choices', []), body.get('usage', {})
            if len(choices) != 1 or choices[0].get('finish_reason') != 'stop':
                raise RuntimeError('Incomplete or ambiguous model output')
            if (not isinstance(usage.get('completion_tokens'), int)
                    or not isinstance(usage.get('prompt_tokens'), int)
                    or not 0 <= usage['completion_tokens'] <= 2048):
                raise RuntimeError('Missing accounting or completion cap exceeded')
            content = choices[0]['message']['content']
            if not isinstance(content, str):
                raise RuntimeError('Expected text content')
            return content, str(dest.relative_to(self.root))
        except Exception as exc:
            record = dict(type=type(exc).__name__, message=str(exc).replace(self.key, '[redacted]'))
            if isinstance(exc, urllib.error.HTTPError):
                record['status'] = exc.code
                record['body'] = exc.read(1500).decode(errors='replace').replace(self.key, '[redacted]')
            write(dest / 'error.json', record)
            raise RuntimeError('Luna request failed; preserved redacted record') from None

    def structured(self, purpose, system, payload, validator):
        records = []
        for attempt in range(2):
            content, wire = self.ask(purpose+f'_{attempt}', system, payload)
            try:
                text = content.strip()
                if text.startswith('```'):
                    text = text.split('\n',1)[1].rsplit('```',1)[0].strip()
                value = json.loads(text)
                validator(value)
                return value, records + [dict(wire=wire, valid=True)]
            except (ValueError, KeyError, TypeError, SyntaxError, IndexError) as exc:
                error = str(exc)[:500]
                records.append(dict(wire=wire, valid=False, error=error))
                write(self.root / wire / 'validation_error.json', records[-1])
                if attempt == 0:
                    payload = dict(original_task=payload, rejected_output=content,
                                   correction='Repair your own output without new observations.', error=error)
        raise RuntimeError('Two invalid Luna outputs; no fabricated fallback')
