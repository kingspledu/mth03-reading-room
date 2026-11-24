from pathlib import Path
import argparse
import json, sys, hashlib
from PIL import Image,ImageOps,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from grid_boundaries import crop_grid
ROOT=Path(__file__).resolve().parent
plan=json.loads((ROOT/'dense-scene-plan.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser()
parser.add_argument('--chapter',type=int,default=1)
args=parser.parse_args()
for start,count in ({1:[(17,16),(33,11)],2:[(44,16),(60,16),(76,5)],3:[(81,16),(97,4)],4:[(101,16),(117,10)],5:[(127,16),(143,7)]}[args.chapter]):
    selected=plan[start-1:start-1+count]
    files=[ROOT/'public/assets'/(s['id']+'.webp') for s in selected]
    audit=ROOT/'crop-review'/f'grid-{start:04}.json'
    records=crop_grid(ROOT/'source_images'/f'grid-{start:04}.png',files,audit)
    out=Image.new('RGB',(1000,270*((count+3)//4)),'white')
    d=ImageDraw.Draw(out)
    for i,f in enumerate(files):
        im=Image.open(f)
        assert im.size==tuple(records[i]['size'])
        assert min(im.size)>200
        out.paste(ImageOps.contain(im,(245,245)),((i%4)*250,(i//4)*270))
        d.text(((i%4)*250,(i//4)*270+246),f.stem,fill='black')
    out.save(ROOT/'crop-review'/f'contact-{start:04}.jpg')
    print(start,count,records[0]['size'])
