#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:?project directory required}"
PYTHON_BASE="${2:-/home/lsy/anaconda3/bin/python}"
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
mkdir -p "$ROOT"
"$PYTHON_BASE" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/python" -m pip install --no-cache-dir --disable-pip-version-check torch==2.5.1 --index-url https://download.pytorch.org/whl/cu121
"$ROOT/.venv/bin/python" -m pip install --no-cache-dir --disable-pip-version-check --index-url https://pypi.tuna.tsinghua.edu.cn/simple numpy==1.26.4 scipy==1.12.0 transformers==4.48.3 accelerate==1.3.0 huggingface-hub==0.28.1 safetensors==0.5.2
"$ROOT/.venv/bin/python" -c 'import torch,transformers,numpy,scipy; print({"torch":torch.__version__,"transformers":transformers.__version__,"cuda":torch.cuda.is_available()})'
touch "$ROOT/ENV_READY"
