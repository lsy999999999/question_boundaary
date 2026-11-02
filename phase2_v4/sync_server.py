"""Transfer this project through an already-authenticated SSH control socket.

Credentials are never read or stored by this script.
"""
import argparse
import io
import shlex
import subprocess
import tarfile
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pull", action="store_true")
    p.add_argument("--host", default="lsy@10.42.127.214")
    p.add_argument("--socket", default="/private/tmp/ideas_ssh_a")
    p.add_argument("--remote", default="/home/lsy/theory_discovery_phase2_v4_20261031")
    p.add_argument("--destination", type=Path, help="Separate local pull directory for each host")
    args = p.parse_args()
    root = Path(__file__).resolve().parent
    ssh = ["ssh", "-S", args.socket, "-o", "BatchMode=yes", args.host]
    if args.pull:
        root = args.destination or root
        root.mkdir(parents=True, exist_ok=True)
        code = f'''import sys,tarfile
from pathlib import Path
root=Path({args.remote!r})
with tarfile.open(fileobj=sys.stdout.buffer,mode="w|gz") as archive:
 for name in ["runs","LIVE_STATUS.json","supervisor.log","environment_freeze.txt","model_identity.json","bootstrap.log","bootstrap_py312.log","protocol_tests.log","gate.json","FROZEN.json","PLAN.md"]:
  path=root/name
  if path.exists():archive.add(path,arcname=name)
'''
        result = subprocess.run(ssh + ["python3 -c " + shlex.quote(code)], capture_output=True, check=True)
        with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:gz") as archive:
            for member in archive:
                target = (root / member.name).resolve()
                if not target.is_relative_to(root.resolve()) or member.issym() or member.islnk():
                    raise ValueError("Unsafe archive member")
                archive.extract(member, root)
        print("Results synchronized")
    else:
        stream = io.BytesIO()
        with tarfile.open(fileobj=stream, mode="w:gz") as archive:
            for path in root.rglob("*"):
                relative = path.relative_to(root)
                if path.is_file() and path.suffix in (".py", ".md", ".sh", ".txt", ".json") and not any(part in relative.parts for part in ("runs", "sources", "__pycache__", ".venv", ".venv_py312", "models")) and path.name not in ("LIVE_STATUS.json", "model_identity.json", "gate.json"):
                    archive.add(path, arcname=str(relative))
        code = f'''import sys,tarfile
from pathlib import Path
root=Path({args.remote!r});root.mkdir(exist_ok=True,parents=True)
with tarfile.open(fileobj=sys.stdin.buffer,mode="r|gz") as archive:
 for member in archive:
  target=(root/member.name).resolve()
  if not target.is_relative_to(root.resolve()) or member.issym() or member.islnk():raise ValueError("Unsafe archive member")
  archive.extract(member,root)
print("Source synchronized")
'''
        result = subprocess.run(ssh + ["python3 -c " + shlex.quote(code)], input=stream.getvalue(), capture_output=True, check=True)
        print(result.stdout.decode().strip())


if __name__ == "__main__":
    main()
