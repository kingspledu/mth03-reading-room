from pathlib import Path
import json, math
from collections import Counter
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'dense-scene-plan.json').read_text(encoding='utf-8'))
remaining=Counter(s['part_id'].split('_')[2] for s in plan if s['status']!='integrated')
status=json.loads((ROOT/'production-status.json').read_text(encoding='utf-8'))
status.update(integrated_scenes=sum(s['status']=='integrated' for s in plan),remaining_scene_candidates=sum(remaining.values()),remaining_chapter_aligned_batches=sum(math.ceil(n/16) for n in remaining.values()),batch_size_max=16,per_session_batches='2–3, sequential generation and visual review',remaining_by_chapter={k:{'scenes':v,'batches':math.ceil(v/16)} for k,v in remaining.items()})
for p in [ROOT/'production-status.json',ROOT/'public/production-status.json']:
    p.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(status,ensure_ascii=False,indent=2))
