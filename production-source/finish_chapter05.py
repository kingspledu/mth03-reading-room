from pathlib import Path
import json,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'dense-scene-plan.json').read_text(encoding='utf-8'))
for s in plan[126:149]:
    assert s['status']=='integrated'
    s['review']='Visually reviewed source, identity sheets, gutter overlay and all crops. Chapter5 dog-head scepter ownership, book/notebook state and ghost reveal checked.'
(ROOT/'dense-scene-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
dest=ROOT/'public/production-source'
for n in ['chapter05-consistency-plan.json','mth03_batch127_prompt.txt','mth03_batch143_prompt.txt','review_current_batches.py','finish_chapter05.py']:
    shutil.copy2(ROOT/n,dest/n)
audits=[]
for start,count in [(127,16),(143,7)]:
    a=json.loads((ROOT/'crop-review'/f'grid-{start:04}.json').read_text())
    a['source']=f'source_images/grid-{start:04}.png'
    for t in a['tiles']:t['target']='assets/'+Path(t['target']).name
    a['native_size']=list(Image.open(ROOT/'source_images'/f'grid-{start:04}.png').size)
    a['visual_review']='Source, actual boundary overlay and every crop checked. No unused cells counted.'
    audits.append(a)
(dest/'chapter05-crop-audit.json').write_text(json.dumps(audits,indent=2),encoding='utf-8')
print('Chapter5:23 scenes reviewed')
