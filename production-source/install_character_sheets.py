from pathlib import Path
import shutil, json, re
ROOT = Path(__file__).resolve().parent
src = Path('C:/Users/고보민/.codex/generated_images/01a20918-df73-7881-8001-91cc2de23c23')
pairs = {'children':'29502232-c70b-4ce4-9b19-e68a2687aaef', 'procession':'6704b519-d98c-4607-b673-ffc197c211db', 'hutepi':'ce9cf6d4-f5e8-4f96-84bf-f18033eef671', 'cat':'fb6642d1-4371-4d55-879c-f92cd1902a20', 'mom':'77bf3070-4a5e-4dd7-8328-a476369595f4'}
for key, value in pairs.items():
    shutil.copy2(src / f'exec-{value}.png', ROOT / f'public/assets/mth03-{key}-sheet-v1.png')
p = ROOT / 'build_reader.py'
t = p.read_text(encoding='utf-8')
start = t.find("if (ROOT/'public/assets/character-sheet.png').exists():")
if start >= 0:
    end = t.index("print('Verified Book 3", start)
    t = t[:start] + "subprocess.run(['python',str(ROOT/'build_characters.py')],check=True)\n" + t[end:]
    p.write_text(t, encoding='utf-8')
b = json.loads((ROOT / 'character-bible.json').read_text(encoding='utf-8'))
mapping = {'MTH03-CAT':'cat','MTH03-HUTEPI':'hutepi','MTH03-PROCESSION':'procession','MTH03-WHITE-FIGURE':'procession','MTH-MOM':'mom'}
for c in b['characters']:
    key = mapping.get(c['id'], 'children')
    c['visual_sheet'] = f'assets/mth03-{key}-sheet-v1.png'
    if c['id'] in mapping:
        c['design'] = 'Dedicated visual sheet v1; see visual_sheets rules.'
(ROOT / 'character-bible.json').write_text(json.dumps(b,ensure_ascii=False,indent=2),encoding='utf-8')
from build_characters import build
build()
sw = ROOT / 'public/sw.js'
t = sw.read_text(encoding='utf-8')
t = re.sub(r"const CACHE=PREFIX\+'[^']+';", "const CACHE=PREFIX+'characters-v1-20261124';", t)
assets = ['./characters.html', './character-bible.json'] + [f'./assets/mth03-{key}-sheet-v1.png' for key in pairs]
for asset in assets:
    if "'"+asset+"'" not in t:
        t = t.replace('const CORE=[', 'const CORE=[' + repr(asset) + ',', 1)
sw.write_text(t, encoding='utf-8')
provenance = {'reference':'Book 4 children visual sheet v1; Mom shares Book 1 appearance', 'review':'Full sheets visually reviewed. Four oxen counted. No slicing; entire image ratio retained.', 'files':{key:f'exec-{value}.png' for key,value in pairs.items()}}
(ROOT / 'public/character-sheet-provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
print('Installed five reviewed sheets and durable renderer.')
