#!/usr/bin/env bash
set -euo pipefail
theory_root="${1:?project directory}"
/home/lsyedith/miniconda3/bin/conda create --offline --yes --clone /home/lsyedith/miniconda3/envs/ml --prefix "$theory_root/.env_gpu"
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt
export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
"$theory_root/.env_gpu/bin/python" -m pip install --timeout 60 --no-cache-dir --index-url https://pypi.tuna.tsinghua.edu.cn/simple numpy==1.26.4 scipy==1.12.0 transformers==4.48.3 accelerate==1.3.0 huggingface-hub==0.28.1 safetensors==0.5.2
"$theory_root/.env_gpu/bin/python" -c 'import torch,transformers,numpy,scipy; assert torch.__version__.split("+")[0]=="2.5.1"; print({"torch":torch.__version__,"transformers":transformers.__version__,"numpy":numpy.__version__,"scipy":scipy.__version__})'
touch "$theory_root/ENV_READY"
