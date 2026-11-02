"""Execution transport only; scientific decisions come from the remote model.

Never persist authentication. Frozen V4 research code is reused without edits.
"""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'

import concurrent.futures
import getpass
import hashlib
import json
import resource
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ORIGINAL = Path('/home/lsyedith/theory_discovery_phase2_v4_20261031')
ROOT = Path(__file__).resolve().parent
ENDPOINT = 'https://sub.krisrosea.top/v1/chat/completions'
MODEL = 'gpt-6-luna'
METHODS = ['state_fixed', 'history_cv', 'plain', 'retrieval', 'structured', 'no_active', 'shuffled']
AGENTS = METHODS[2:]


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False))
    tmp.replace(path)


def status(stage, **details):
    record = dict(stage=stage, time_ns=time.time_ns(), pid=os.getpid(), **details)
    write(ROOT / 'LIVE_STATUS.json', record)
    print(json.dumps(record, ensure_ascii=False), flush=True)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Transport:
    def __init__(self, key):
        self.key = key
        self.lock = threading.Lock()
        self.stop = threading.Event()
        self.count = 0
        self.stage = 'dev'

    def generate(self, batches):
        if len(batches) != 1:
            raise RuntimeError('Frozen per-request batch size is one')
        if self.stop.is_set():
            raise RuntimeError('Transport stopped after a previous request failure')
        messages = batches[0]
        with self.lock:
            self.count += 1
            number = self.count
        if number > 560:
            raise RuntimeError('Frozen 560-request cap exceeded')
        payload = dict(model=MODEL, messages=messages, max_completion_tokens=512, temperature=0)
        dest = ROOT / 'wire' / self.stage / f'{number:04d}_{uuid.uuid4().hex}'
        write(dest / 'request.json', dict(time_ns=time.time_ns(), endpoint=ENDPOINT, payload=payload))
        req = urllib.request.Request(ENDPOINT, data=json.dumps(payload).encode(),
            headers={'Authorization': 'Bearer ' + self.key, 'Content-Type': 'application/json'})
        started = time.monotonic()
        try:
            with urllib.request.build_opener(NoRedirect).open(req, timeout=90) as response:
                body = response.read().decode().replace(self.key, '[redacted]')
                http_status = response.status
            elapsed = time.monotonic() - started
            data = json.loads(body)
            write(dest / 'response.json', dict(time_ns=time.time_ns(), http_status=http_status,
                                               body=data, elapsed_seconds=elapsed))
            if data.get('model') != MODEL:
                raise RuntimeError('Returned model differs from frozen requested model')
            choices = data.get('choices', [])
            if len(choices) != 1:
                raise RuntimeError('Expected exactly one response choice')
            content = choices[0].get('message', {}).get('content')
            if content is None:
                content = ''
            if not isinstance(content, str):
                raise RuntimeError('Response content is not text')
            usage = data.get('usage', {})
            if 'prompt_tokens' not in usage or 'completion_tokens' not in usage:
                raise RuntimeError('API token accounting absent')
            if usage['completion_tokens'] > 512:
                raise RuntimeError('Service exceeded frozen 512 completion-token limit')
            return [dict(text=content, input_tokens=usage['prompt_tokens'],
                output_tokens=usage['completion_tokens'], batch_elapsed_seconds=elapsed,
                amortized_seconds=elapsed, peak_gpu_allocated_gb=0.0,
                peak_process_ram_gb=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20,
                backend='third_party_api', model_path=MODEL, returned_model=data['model'],
                finish_reason=choices[0].get('finish_reason'), api_usage=usage,
                api_response_id=data.get('id'), wire_record=str(dest.relative_to(ROOT)))]
        except Exception as exc:
            self.stop.set()
            error = dict(type=type(exc).__name__, message=str(exc).replace(self.key, '[redacted]'))
            if isinstance(exc, urllib.error.HTTPError):
                error['http_status'] = exc.code
                error['body'] = exc.read(4000).decode(errors='replace').replace(self.key, '[redacted]')
            write(dest / 'error.json', error)
            raise RuntimeError('API request failed; see redacted wire error record') from None


def freeze_source():
    reference = json.loads((ORIGINAL / 'runs/dev_v4/manifest.json').read_text())
    frozen = ROOT / 'frozen'
    frozen.mkdir(exist_ok=False)
    (frozen / 'discovery').mkdir()
    for name, digest in reference['source_hashes'].items():
        source = ORIGINAL / name
        if hashlib.sha256(source.read_bytes()).hexdigest() != digest:
            raise RuntimeError('Original V4 source hash mismatch: ' + name)
        shutil.copy2(source, frozen / name)
    shutil.copy2(ORIGINAL / 'audit_results.py', frozen / 'audit_results.py')
    sys.path.insert(0, str(frozen))
    return reference


def gate(summary, audited):
    reasons = []
    for method, row in summary['methods'].items():
        if row['generation_calls'] and row['invalid_outputs'] / row['generation_calls'] > .25:
            reasons.append(f'{method}: invalid outputs >25%')
    if audited['source_counts']['structured']['valid_non_none'] < 1:
        reasons.append('structured: no valid nonempty mapping')
    if audited['representation_changes']['structured']['tasks_with_revision'] < 1:
        reasons.append('structured: no representation revision')
    for field in ('forecast_order_errors', 'forecast_hash_errors', 'evaluation_order_errors'):
        if audited[field]:
            reasons.append(field)
    return dict(passed=not reasons, reasons=reasons,
        criterion='Unchanged V4 development invocation/format gate; semantic correctness separate.')


def stage(split, transport, reference):
    from dataclasses import asdict
    import numpy as np
    import scipy
    from discovery.runner import run_baselines, run_agents, source_hashes
    from discovery.world import catalog
    from discovery.report import build_report
    from audit_results import audit

    transport.stage = split
    seeds = [201] if split == 'dev' else [31, 32, 33]
    tasks = catalog(split, seeds)
    root = ROOT / 'runs' / split
    if root.exists():
        raise RuntimeError('Refusing to overwrite or silently resume an existing run')
    manifest = dict(reference, split=split, seeds=seeds, tasks=[asdict(t) for t in tasks],
        methods=METHODS, backend='third_party_api', model=MODEL, endpoint=ENDPOINT,
        python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
        batch_size=1, threads=1, concurrent_api_requests=5, max_new_tokens=512,
        source_hashes=source_hashes(), protocol_version='v4-source-schema-model-swap-total-token-cap-v2',
        api_transport_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        comparison='Fixed V4 task replication; previously used evaluation tasks, no retuning.',
        compute_limit='API max_completion_tokens=512, potentially inclusive of hidden reasoning; different tokenizer.')
    write(root / 'manifest.json', manifest)
    status(split + '_baselines')
    run_baselines(tasks, root, METHODS[:2], 3)
    checks = []
    original_split = 'dev_v4' if split == 'dev' else 'eval_v4'
    original_a = ROOT / 'reference_baselines'
    for method in METHODS[:2]:
        for task in tasks:
            current = json.loads((root / method / task.task_id / 'result.json').read_text())
            old = json.loads((original_a / original_split / method / task.task_id / 'result.json').read_text())
            delta = abs(current['test']['test_nmse'] - old['test']['test_nmse'])
            matched = delta < 1e-12 and current['selected_actions'] == old['selected_actions'] and current['selected_representations'] == old['selected_representations']
            checks.append(dict(method=method, task_id=task.task_id, matched=matched, nmse_absolute_difference=delta))
    write(root / 'baseline_equivalence.json', checks)
    if not all(c['matched'] for c in checks):
        raise RuntimeError('Numerical baseline equivalence failed; no model requests for this stage')
    status(split + '_agents', baseline_matches=len(checks))
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        jobs = [pool.submit(run_agents, tasks, root, [method], 3, transport, 1) for method in AGENTS]
        try:
            for future in concurrent.futures.as_completed(jobs):
                future.result()
        except Exception:
            transport.stop.set()
            for future in jobs:
                future.cancel()
            raise
    summary = build_report(root, METHODS)
    audited = audit(root)
    if not summary['complete']:
        raise RuntimeError('Incomplete stage')
    if any(audited[k] for k in ('forecast_order_errors', 'forecast_hash_errors', 'evaluation_order_errors')):
        raise RuntimeError('Stage provenance audit failed')
    return summary, audited


def main():
    key = getpass.getpass('API key (hidden): ')
    transport = Transport(key)
    try:
        import numpy as np
        import scipy
        if sys.version_info[:2] != (3, 10) or np.__version__ != '1.26.4' or scipy.__version__ != '1.12.0':
            raise RuntimeError('Original numerical environment not matched')
        reference = freeze_source()
        status('starting', requested_model=MODEL)
        summary, audited = stage('dev', transport, reference)
        decision = gate(summary, audited)
        write(ROOT / 'gate.json', decision)
        if not decision['passed']:
            status('development_gate_failed', gate=decision, api_requests=transport.count)
            return
        status('development_gate_passed', api_requests=transport.count)
        stage('eval', transport, reference)
        status('completed', api_requests=transport.count)
    except Exception as exc:
        status('failed', error_type=type(exc).__name__,
               error=str(exc).replace(key, '[redacted]'), api_requests=transport.count)
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
