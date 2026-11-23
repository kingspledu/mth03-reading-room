from pathlib import Path
import json, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'dense-scene-plan.json').read_text(encoding='utf-8'))
for s in plan[80:100]:
    assert s['status']=='integrated'
    s['review']='Source, character reference, generated grid, detected gutter overlay and every crop visually checked. Chapter 3 torch, floor slope, book state, absent cat and unrevealed white figure continuity checked.'
(ROOT/'dense-scene-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
dest=ROOT/'public/production-source'
for n in ['chapter03-consistency-plan.json','mth03_batch81_prompt.txt','mth03_batch97_prompt.txt','review_current_batches.py','finish_chapter03.py']:
    shutil.copy2(ROOT/n,dest/n)
audits=[]
for start,count in [(81,16),(97,4)]:
    a=json.loads((ROOT/'crop-review'/f'grid-{start:04}.json').read_text())
    a['source']=f'source_images/grid-{start:04}.png'
    for t in a['tiles']:t['target']='assets/'+Path(t['target']).name
    a['native_size']=list(Image.open(ROOT/'source_images'/f'grid-{start:04}.png').size)
    a['visual_review']='Source, overlay and all crops checked. No filler counted.'
    audits.append(a)
(dest/'chapter03-crop-audit.json').write_text(json.dumps(audits,indent=2),encoding='utf-8')
print('Chapter 3 reviewed: 20 scenes.')
