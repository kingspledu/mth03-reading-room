import argparse
import json
import shutil
import subprocess
from pathlib import Path
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from grid_boundaries import crop_grid

root=Path(__file__).resolve().parent
parser=argparse.ArgumentParser()
parser.add_argument('image')
parser.add_argument('--start',type=int,required=True)
parser.add_argument('--count',type=int,default=16)
args=parser.parse_args()
plan=json.loads((root/'dense-scene-plan.json').read_text(encoding='utf-8'))
assert 1 <= args.count <= 16
selected=plan[args.start-1:args.start-1+args.count]
source=root/'source_images'
source.mkdir(exist_ok=True)
shutil.copyfile(args.image,source/f'grid-{args.start:04}.png')
records=crop_grid(args.image,[root/'public/assets'/f"{s['id']}.webp" for s in selected],root/'crop-review'/f'grid-{args.start:04}.json')
for scene in selected:
    scene.update(status='integrated',asset=f"assets/{scene['id']}.webp",alt=scene['source_text'].strip()[:120],review='Detected gutters; crop overlay requires visual review.')
(root/'dense-scene-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
subprocess.run(['python',str(root/'split_parts.py')],check=True)
subprocess.run(['python',str(root/'build_characters.py')],check=True)
