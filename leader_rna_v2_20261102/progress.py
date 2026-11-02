"""Read-only progress command; independent of current working directory."""
import datetime
import json
from pathlib import Path

root=Path(__file__).resolve().parent
print('RNA V2 |',datetime.datetime.now().astimezone().isoformat(timespec='seconds'))
print('阶段A:', '接口验收通过' if (root/'STAGE_A_REPORT.json').exists() else '尚未通过')
total=0
for name in ['A1','A2','B1','B2','C1','C2']:
 r=root/'runs'/name
 if not r.exists():print(name,'未开始');continue
 replies=list((r/'replies').glob('*.json'));total+=len(replies)
 states=sorted((r/'states').glob('*.json'));s=json.loads(states[-1].read_text())
 frozen=(r/'FROZEN.json').exists()
 print(f"{name}: 回复 {len(replies)}/6，入账 {s['counters']['replies']}/6，检索 {s['counters']['search']}，计算 {s['counters']['compute']}，"+('已冻结' if frozen else '待总控处理/验收'))
print(f'阶段B回复：{total}/36')
gate=root/'STAGE_C_DECISION.json'
if gate.exists():
 d=json.loads(gate.read_text());print('阶段C:',d['decision']);print('原因:',d['reason'])
else:print('阶段C: 等待阶段B验收')
full=root/'runs/V2_full'
if full.exists():
 s=json.loads(sorted((full/'states').glob('*.json'))[-1].read_text())
 count=len(list((full/'replies').glob('*.json')))
 print(f"完整RNA V2：回复 {count}/12，入账 {s['counters']['replies']}/12，检索 {s['counters']['search']}/6，计算 {s['counters']['compute']}/10，"+('已冻结' if (full/'FROZEN.json').exists() else '执行/验收中'))
 events=full/'autonomous_events.jsonl'
 if events.exists() and events.read_text().splitlines():
  last=json.loads(events.read_text().splitlines()[-1]);print('后台调度最近记录:',last)
report=root/'REPORT.md'
print('结果报告:',report if report.exists() else '尚在整理')
done=root/'COMPLETED.json'
research_done=root/'RESEARCH_RUN_COMPLETED.json'
failed=root/'RESEARCH_RUN_FAILED.json'
if done.exists():print('本轮状态:',json.loads(done.read_text())['status'])
elif research_done.exists():print('本轮状态:',json.loads(research_done.read_text())['status'])
elif failed.exists():print('本轮状态: 运行失败',json.loads(failed.read_text()))
else:print('本轮状态: 进行中；长时间无新记录时需回到主会话检查')
