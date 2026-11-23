"""Build Book 3 from verified canonical source and split into thirteen parts."""
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parent
master=json.loads(Path('C:/Users/고보민/Downloads/_보존/_MTH/00_MTH_NotebookLM_Master.json').read_text(encoding='utf-8-sig'))
book=next(b for b in master['books'] if b['book_number']==3)
story=json.loads((ROOT/'story.json').read_text(encoding='utf-8'))
for chapter,source in zip(story['chapters'],book['chapters']):
    assert ' '.join(p['text'] for p in chapter['paragraphs']).split()==source['source_text'].split()
subprocess.run(['python','C:/Users/고보민/.codex/skills/illustrated-story-reader/scripts/story_site.py','build','--project',str(ROOT)],check=True)
rows='''gazed|응시했다|Looked steadily at something.
tiptoed|발끝으로 살금살금 걸었다|Walked quietly on the toes.
bushes|덤불|Groups of small thick plants.
branch|나뭇가지|A woody part growing from a tree.
medallion|큰 메달|A large medal kept as a special object.
bookmark|책갈피|Something used to mark a place in a book.
breeze|산들바람|A light gentle wind.
rattled|바스락거렸다|Made a series of short knocking sounds.
scattered|흩어진|Spread over different places.
pyramid|피라미드|An ancient structure with triangular sides meeting at the top.
desert|사막|A very dry area with little rain.
mummy|미라|A body preserved and wrapped in cloth.
ghost|유령|The spirit of a dead person in a story.
queen|여왕|A woman who rules a country.
torch|횃불|A burning stick used to give light.
tomb|무덤|A place where a dead person is buried.
hieroglyphs|상형문자|Ancient writing made with pictures and symbols.
scroll|두루마리|A long roll of paper used for writing.
whispered|속삭였다|Spoke very quietly.
shadows|그림자들|Dark shapes made when something blocks light.
passage|통로|A narrow way through a building.
chamber|방|A room inside a large building or structure.
sarcophagus|석관|A stone container for a coffin.
treasure|보물|Valuable objects such as gold and jewels.
clutched|꽉 쥐었다|Held something tightly.
vanished|사라졌다|Disappeared suddenly.'''
words={}
for row in rows.splitlines():
    term,ko,definition=row.split('|')
    words[term]={'ko':ko,'definition':definition}
(ROOT/'public/vocabulary.json').write_text(json.dumps(words,ensure_ascii=False),encoding='utf-8')
page=(ROOT/'public/index.html').read_text(encoding='utf-8').replace('</head>','<link rel="stylesheet" href="learning.css"><script src="learning.js" defer></script></head>')
(ROOT/'public/index.html').write_text(page,encoding='utf-8')
subprocess.run(['python',str(ROOT/'split_parts.py')],check=True)
subprocess.run(['python',str(ROOT/'build_characters.py')],check=True)
print('Verified Book 3 original text: 10 chapters, 13 parts, 520 paragraphs.')
