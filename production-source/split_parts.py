"""Create independent part pages from the verified Master JSON text."""
import copy
import hashlib
import html
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
PUBLIC=ROOT/'public'
master=json.loads(Path('C:/Users/고보민/Downloads/_보존/_MTH/00_MTH_NotebookLM_Master.json').read_text(encoding='utf-8-sig'))
parts=[p for p in master['parts'] if p['book_number']==3]
story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
words=json.loads((PUBLIC/'vocabulary.json').read_text(encoding='utf-8'))
pattern=re.compile(r'\b('+ '|'.join(map(re.escape,words))+r')\b',re.I)
template=BeautifulSoup((PUBLIC/'index.html').read_text(encoding='utf-8'),'html.parser')
def filename(part):
    return f"part-{part['chapter_number']:02}-{part['part_number']:02}.html"
def title(part):
    return f"Chapter {part['chapter_number']} · Part {part['part_number']} — "+part['title'].split(' - ',1)[-1]
def clean(text):
    return re.sub(r'\s+','',text)
chapter_text={c['id']:c['paragraphs'] for c in story['chapters']}
image_endpoints={}
for chapter,paragraphs in chapter_text.items():
    offset=0
    endpoints=[]
    for paragraph in paragraphs:
        offset+=len(clean(paragraph['text']))
        element=template.find(id=paragraph['id'])
        sibling=element.find_next_sibling() if element else None
        if sibling and sibling.name=='figure':
            endpoints.append((offset,str(sibling)))
    image_endpoints[chapter]=endpoints

links=''.join(f'<a href="{filename(p)}">{html.escape(title(p))}</a>' for p in parts)
offsets={}
total_images=0
for index,part in enumerate(parts):
    page=copy.deepcopy(template)
    page.title.string=title(part)+' · Mummies in the Morning'
    for nav in page.select('.toc'):
        nav.clear()
        nav.append(BeautifulSoup(links,'html.parser'))
    for nav in page.select('.part-links'):
        nav.decompose()
    article=page.find('article')
    article.clear()
    article.append(BeautifulSoup('<h2>'+html.escape(title(part))+'</h2>','html.parser'))
    chapter=f"chapter-{part['chapter_number']:03}"
    start=offsets.get(chapter,0)
    end=start+len(clean(part['original_text']))
    figures=[(position,figure) for position,figure in image_endpoints[chapter] if start<position<=end]
    current=start
    for number,text in enumerate(re.split(r'\n\s*\n',part['original_text'].strip()),1):
        escaped=html.escape(text)
        escaped=pattern.sub(lambda m:'<button class="vocab-word" data-word="'+m.group().lower()+'" aria-expanded="false">'+m.group()+'</button>',escaped)
        markup='<p class="story-text" id="part-p'+str(number)+'"><span class="sentence">'+escaped+'</span></p>'
        article.append(BeautifulSoup(markup,'html.parser'))
        current+=len(clean(text))
        while figures and figures[0][0]<=current:
            _,figure=figures.pop(0)
            article.append(BeautifulSoup(figure,'html.parser'))
            total_images+=1
    assert not figures
    offsets[chapter]=end
    plan_path=ROOT/'dense-scene-plan.json'
    if plan_path.exists():
        scenes=json.loads(plan_path.read_text(encoding='utf-8'))
        local=[s for s in scenes if s['part_id']==part['id'] and s['status']=='integrated']
        offset=0
        for paragraph in list(article.select('.story-text')):
            # Scene offsets refer to original_text, including paragraph separators.
            # Summed visible text lengths omit those separators and lose final scenes.
            paragraph_text=paragraph.get_text()
            position=part['original_text'].find(paragraph_text,offset)
            assert position >= 0, (part['id'], paragraph_text[:60])
            offset=position+len(paragraph_text)
            while offset < len(part['original_text']) and part['original_text'][offset].isspace():
                offset += 1
            applicable=[s for s in local if s['end']<=offset]
            for scene in applicable:
                figure=BeautifulSoup('<figure><img loading="lazy" src="'+scene['asset']+'" alt="'+html.escape(scene['alt'],quote=True)+'" style="width:min(100%,340px);height:auto;display:block;margin:auto"></figure>','html.parser')
                paragraph.insert_after(figure)
                local.remove(scene)
                total_images+=1
    previous='<a href="'+filename(parts[index-1])+'">← 이전 파트</a>' if index else ''
    following='<a href="'+filename(parts[index+1])+'">다음 파트 →</a>' if index+1<len(parts) else ''
    footer=page.select_one('.end-note')
    footer.clear()
    footer.append(BeautifulSoup('<nav class="part-links">'+previous+'<a href="index.html">전체 목차</a>'+following+'</nav>','html.parser'))
    skip=page.select_one('.skip')
    if skip: skip['href']='#part-p1'
    for link in page.select('a[href]'):
        if link['href'].startswith('#chapter-'):
            link['href']='#part-p1'
    actual=''.join(p.get_text() for p in page.select('.story-text'))
    assert clean(actual)==clean(part['original_text'])
    (PUBLIC/filename(part)).write_text(str(page),encoding='utf-8')

# The landing page is the part table of contents.
for nav in template.select('.toc'):
    nav.clear()
    nav.append(BeautifulSoup(links,'html.parser'))
for nav in template.select('.part-links'):
    nav.decompose()
article=template.find('article')
article.clear()
article.append(BeautifulSoup('<h2>목차 · 13 Parts</h2><nav class="part-index">'+links+'</nav>','html.parser'))
skip=template.select_one('.skip')
if skip: skip['href']=filename(parts[0])
for link in template.select('a[href]'):
    if link['href'].startswith('#chapter-'):
        link['href']=filename(parts[0])
(PUBLIC/'index.html').write_text(str(template),encoding='utf-8')
worker=(PUBLIC/'sw.js').read_text(encoding='utf-8')
worker=worker.replace("const CORE=[",'const CORE=['+','.join(repr('./'+filename(p)) for p in parts)+',')
version=hashlib.sha256(''.join((PUBLIC/filename(p)).read_text(encoding='utf-8') for p in parts).encode()).hexdigest()[:12]
worker=re.sub(r"const CACHE=PREFIX\+'[^']+';","const CACHE=PREFIX+'"+version+"';",worker)
(PUBLIC/'sw.js').write_text(worker,encoding='utf-8')
assert total_images==sum(s['status']=='integrated' for s in json.loads((ROOT/'dense-scene-plan.json').read_text(encoding='utf-8'))),total_images
print(f'Verified 13 independent parts, exact original text, {total_images} illustrations, previous/next navigation.')
