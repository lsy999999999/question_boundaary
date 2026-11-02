"""Download public Qwen model files from ModelScope, with resumable shards."""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://modelscope.cn/models/Qwen/Qwen2.5-7B-Instruct/resolve/master/"


def download(root, name):
    dest = root / name
    if dest.exists() and dest.stat().st_size:
        print(json.dumps({"file": name, "status": "existing", "bytes": dest.stat().st_size}), flush=True)
        return
    partial = dest.with_name(dest.name + ".part")
    for attempt in range(5):
        try:
            offset = partial.stat().st_size if partial.exists() else 0
            request = urllib.request.Request(BASE + name, headers={"User-Agent": "research-prototype/1.0"})
            if offset:
                request.add_header("Range", f"bytes={offset}-")
            with urllib.request.urlopen(request, timeout=90) as response:
                append = offset > 0 and response.status == 206
                with partial.open("ab" if append else "wb") as f:
                    while True:
                        block = response.read(4 * 1024 * 1024)
                        if not block:
                            break
                        f.write(block)
                    f.flush()
                    os.fsync(f.fileno())
            partial.replace(dest)
            print(json.dumps({"file": name, "status": "downloaded", "bytes": dest.stat().st_size}), flush=True)
            return
        except Exception as exc:
            print(json.dumps({"file": name, "attempt": attempt + 1, "error": str(exc)}), flush=True)
            if attempt == 4:
                raise
            time.sleep(min(2**attempt, 15))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    files = ["config.json", "generation_config.json", "tokenizer_config.json", "tokenizer.json", "vocab.json", "merges.txt", "model.safetensors.index.json"]
    for name in files:
        download(args.output, name)
    index = json.loads((args.output / "model.safetensors.index.json").read_text())
    shards = sorted(set(index["weight_map"].values()))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda name: download(args.output, name), shards))
    actual = sum((args.output / name).stat().st_size for name in shards)
    expected = index["metadata"]["total_size"]
    if actual < expected:
        raise RuntimeError(f"Incomplete model: {actual} < {expected}")
    (args.output / "DOWNLOAD_COMPLETE.json").write_text(json.dumps({"source": BASE, "total_shard_bytes": actual, "index_tensor_bytes": expected, "files": files + shards}, indent=2))
    print("MODEL_READY", flush=True)


if __name__ == "__main__":
    main()
