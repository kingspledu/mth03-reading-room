"""Render the durable Book 3 character reference independently of reader content."""
from pathlib import Path
import json
from html import escape

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / 'public'
SHEETS = [
    ('children', 'Jack & Annie', 'Jack은 갈색 머리·얇은 원형 안경·빨간 긴팔·청바지·갈색 운동화, Annie는 금발 단발·보라 티셔츠·청반바지·빨간 운동화로 고정합니다. 얼굴과 상대 키는 4권 시트를 기준으로 합니다. 색상과 복장 조합은 제작용 설정입니다. 가방·노트는 해당 장면의 소유와 행동을 따릅니다. Annie의 노트 포즈는 형태 참고이며 모든 장면에 노트를 추가하지 않습니다.', False),
    ('cat', 'Black Cat', '검은 털, 노란 눈, 넓은 금목걸이를 유지합니다. 책 속 그림, 실제 고양이, 화면 밖 울음소리를 구분합니다. 소리만 들리는 문장에 고양이를 임의로 그리지 않습니다. 변신이나 정체를 미리 드러내지 않습니다.', False),
    ('hutepi', 'Queen Hutepi · 유령과 미라', '검은 머리와 꽃, 주름 많은 흰 드레스, 금장신구를 유령 상태의 기준으로 삼습니다. 유령과 관 속 미라는 같은 인물의 서로 다른 상태입니다. 유령은 4장 말미와 5–6장, 7장 계단·문 장면에 맞추고, 미라는 8장 관 장면에만 사용합니다. 떠나는 배에 유령을 임의로 추가하지 않습니다. Morgan과 혼동하지 않습니다.', True),
    ('procession', '장례 행렬 & 흰 형체', '가족·하인·조문객, 금빛 관과 나무 썰매, 뿔 달린 소 네 마리를 유지합니다. 행렬 인물의 세부 얼굴은 제작용 설정입니다. 3장 말미와 4장 도입의 흰 형체는 얼굴과 정체를 확정하지 않습니다. 시트의 천 형태는 시각화 선택입니다.', True),
    ('mom', 'Mom', '목소리만 들리는 대목과 10장 부엌에서 실제로 등장하는 대목을 구분합니다. 밤색 단발·크림 블라우스·세이지 카디건·남색 바지·갈색 신발은 1권과 공유하는 제작용 외형 설정입니다. 이집트 모험 장면에 배치하지 않습니다.', True),
]

def build():
    bible = json.loads((ROOT / 'character-bible.json').read_text(encoding='utf-8'))
    bible['status'] = 'book_specific_visual_sheets_ready_v1'
    bible['visual_sheets'] = [{'id': key, 'title': title, 'asset': f'assets/mth03-{key}-sheet-v1.png', 'rules': rules, 'spoiler': spoiler} for key, title, rules, spoiler in SHEETS]
    for path in [ROOT / 'character-bible.json', PUBLIC / 'character-bible.json']:
        path.write_text(json.dumps(bible, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    parts = []
    for item in bible['visual_sheets']:
        tag = 'details' if item['spoiler'] else 'section'
        heading = f'<summary>{escape(item["title"])} · 펼쳐 보기 (스포일러)</summary>' if item['spoiler'] else f'<h2>{escape(item["title"])}</h2>'
        parts.append(f'<{tag} id="{item["id"]}">{heading}<p>{escape(item["rules"])}</p><a href="{item["asset"]}" target="_blank" rel="noopener"><img src="{item["asset"]}" alt="{escape(item["title"])} 캐릭터 일관성 시트" loading="lazy"></a><small>이미지를 누르면 원본 크기로 열립니다.</small></{tag}>')
    page = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>캐릭터 일관성 시트 · Mummies in the Morning</title><style>*{box-sizing:border-box}body{max-width:1120px;margin:auto;padding:24px 16px 56px;background:#faf6ed;color:#263e30;font:17px/1.8 system-ui}a{color:inherit}h1{line-height:1.25;font-size:clamp(28px,5vw,44px)}nav{display:flex;gap:18px;flex-wrap:wrap}section,details{margin:24px 0;padding:20px;background:#fffdf8;border:1px solid #cbd2c0;border-radius:18px}h2{margin:0}summary{font-size:23px;font-weight:bold;cursor:pointer}img{display:block;width:100%;height:auto;object-fit:contain;border-radius:10px}small{color:#60715e}.note{border-left:4px solid #748663;padding-left:18px}@media(max-width:500px){section,details{padding:12px}body{font-size:16px}}</style></head><body><nav><a href="index.html">전체 파트 목차</a><a href="character-bible.json">제작 기준 데이터</a><a href="https://kingspledu.github.io/mth04-reading-room/characters.html">4권 기준 시트</a></nav><h1>Mummies in the Morning<br>캐릭터 일관성 시트</h1><p>Magic Tree House · Book 3 / 시각 기준 v1</p><p class="note">4권의 얼굴·머리·체형과 따뜻한 선화 및 채색을 공통 기준으로 사용합니다. 원문의 등장 여부·복장·소품·상태가 시트의 예시 포즈보다 우선합니다. 아래 시트는 장면 삽화를 위한 참고이며 등장 허가 목록이 아닙니다.</p><nav><a href="#children">Jack & Annie</a><a href="#cat">검은 고양이</a><a href="#hutepi">Hutepi</a><a href="#procession">행렬·흰 형체</a><a href="#mom">Mom</a></nav>'''
    (PUBLIC / 'characters.html').write_text(page + ''.join(parts) + '<p>시트 5장 · 비율 유지 · 원본 전체 표시. 장면별 출연 여부는 원문과 scene manifest를 함께 확인합니다.</p></body></html>', encoding='utf-8')
    for path in [PUBLIC / 'index.html', *PUBLIC.glob('part-*.html')]:
        text = path.read_text(encoding='utf-8')
        if 'href="characters.html"' not in text:
            text = text.replace('<article', '<p class="reader-links"><a href="characters.html">캐릭터 일관성 시트</a></p><article', 1)
            path.write_text(text, encoding='utf-8')

if __name__ == '__main__':
    build()
