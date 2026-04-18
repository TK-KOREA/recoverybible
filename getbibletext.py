import tkinter as tk
from tkinter import scrolledtext, messagebox
import tkinter.font as tkfont
import threading
import requests
from bs4 import BeautifulSoup
import re

# 구약(0) 및 신약(1)의 책 이름과 bibleSelOp 매핑 딕셔너리
BIBLE_MAP = {
    '창': (0, 1), '창세기': (0, 1), '출': (0, 2), '출애굽기': (0, 2), '레': (0, 3), '레위기': (0, 3),
    '민': (0, 4), '민수기': (0, 4), '신': (0, 5), '신명기': (0, 5), '수': (0, 6), '여호수아': (0, 6),
    '삿': (0, 7), '사사기': (0, 7), '룻': (0, 8), '룻기': (0, 8), '삼상': (0, 9), '사무엘상': (0, 9),
    '삼하': (0, 10), '사무엘하': (0, 10), '왕상': (0, 11), '열왕기상': (0, 11), '왕하': (0, 12), '열왕기하': (0, 12),
    '대상': (0, 13), '역대상': (0, 13), '대하': (0, 14), '역대하': (0, 14), '스': (0, 15), '에스라': (0, 15),
    '느': (0, 16), '느헤미야': (0, 16), '에': (0, 17), '에스더': (0, 17), '욥': (0, 18), '욥기': (0, 18),
    '시': (0, 19), '시편': (0, 19), '잠': (0, 20), '잠언': (0, 20), '전': (0, 21), '전도서': (0, 21),
    '아': (0, 22), '아가': (0, 22), '사': (0, 23), '이사야': (0, 23), '렘': (0, 24), '예레미야': (0, 24),
    '애': (0, 25), '예레미야애가': (0, 25), '겔': (0, 26), '에스겔': (0, 26), '단': (0, 27), '다니엘': (0, 27),
    '호': (0, 28), '호세아': (0, 28), '욜': (0, 29), '요엘': (0, 29), '암': (0, 30), '아모스': (0, 30),
    '옵': (0, 31), '오바댜': (0, 31), '욘': (0, 32), '요나': (0, 32), '미': (0, 33), '미가': (0, 33),
    '나': (0, 34), '나훔': (0, 34), '합': (0, 35), '하박국': (0, 35), '습': (0, 36), '스바냐': (0, 36),
    '학': (0, 37), '학개': (0, 37), '슥': (0, 38), '스가랴': (0, 38), '말': (0, 39), '말라기': (0, 39),
    '마': (1, 1), '마태복음': (1, 1), '막': (1, 2), '마가복음': (1, 2), '눅': (1, 3), '누가복음': (1, 3),
    '요': (1, 4), '요한복음': (1, 4), '행': (1, 5), '사도행전': (1, 5), '롬': (1, 6), '로마서': (1, 6),
    '고전': (1, 7), '고린도전서': (1, 7), '고후': (1, 8), '고린도후서': (1, 8), '갈': (1, 9), '갈라디아서': (1, 9),
    '엡': (1, 10), '에베소서': (1, 10), '빌': (1, 11), '빌립보서': (1, 11), '골': (1, 12), '골로새서': (1, 12),
    '살전': (1, 13), '데살로니가전서': (1, 13), '살후': (1, 14), '데살로니가후서': (1, 14), '딤전': (1, 15), '디모데전서': (1, 15),
    '딤후': (1, 16), '디모데후서': (1, 16), '딛': (1, 17), '디도서': (1, 17), '몬': (1, 18), '빌레몬서': (1, 18),
    '히': (1, 19), '히브리서': (1, 19), '약': (1, 20), '야고보서': (1, 20), '벧전': (1, 21), '베드로전서': (1, 21),
    '벧후': (1, 22), '베드로후서': (1, 22), '요일': (1, 23), '요한일서': (1, 23), '요이': (1, 24), '요한이서': (1, 24),
    '요삼': (1, 25), '요한삼서': (1, 25), '유': (1, 26), '유다서': (1, 26), '계': (1, 27), '요한계시록': (1, 27)
}

# 영어 회복역 책 번호/이름 매핑 (bible_ver, bible_sel_op) → (번호문자열, 영어책이름)
ENGLISH_BOOK_MAP = {
    (0,  1): ('01', 'Genesis'),      (0,  2): ('02', 'Exodus'),       (0,  3): ('03', 'Leviticus'),
    (0,  4): ('04', 'Numbers'),      (0,  5): ('05', 'Deuteronomy'),  (0,  6): ('06', 'Joshua'),
    (0,  7): ('07', 'Judges'),       (0,  8): ('08', 'Ruth'),         (0,  9): ('09', '1Samuel'),
    (0, 10): ('10', '2Samuel'),      (0, 11): ('11', '1Kings'),       (0, 12): ('12', '2Kings'),
    (0, 13): ('13', '1Chronicles'),  (0, 14): ('14', '2Chronicles'),  (0, 15): ('15', 'Ezra'),
    (0, 16): ('16', 'Nehemiah'),     (0, 17): ('17', 'Esther'),       (0, 18): ('18', 'Job'),
    (0, 19): ('19', 'Psalms'),       (0, 20): ('20', 'Proverbs'),     (0, 21): ('21', 'Ecclesiastes'),
    (0, 22): ('22', 'SongofSongs'),  (0, 23): ('23', 'Isaiah'),       (0, 24): ('24', 'Jeremiah'),
    (0, 25): ('25', 'Lamentations'), (0, 26): ('26', 'Ezekiel'),      (0, 27): ('27', 'Daniel'),
    (0, 28): ('28', 'Hosea'),        (0, 29): ('29', 'Joel'),         (0, 30): ('30', 'Amos'),
    (0, 31): ('31', 'Obadiah'),      (0, 32): ('32', 'Jonah'),        (0, 33): ('33', 'Micah'),
    (0, 34): ('34', 'Nahum'),        (0, 35): ('35', 'Habakkuk'),     (0, 36): ('36', 'Zephaniah'),
    (0, 37): ('37', 'Haggai'),       (0, 38): ('38', 'Zechariah'),    (0, 39): ('39', 'Malachi'),
    (1,  1): ('40', 'Matthew'),      (1,  2): ('41', 'Mark'),         (1,  3): ('42', 'Luke'),
    (1,  4): ('43', 'John'),         (1,  5): ('44', 'Acts'),         (1,  6): ('45', 'Romans'),
    (1,  7): ('46', '1Corinthians'), (1,  8): ('47', '2Corinthians'), (1,  9): ('48', 'Galatians'),
    (1, 10): ('49', 'Ephesians'),    (1, 11): ('50', 'Philippians'),  (1, 12): ('51', 'Colossians'),
    (1, 13): ('52', '1Thessalonians'),(1, 14): ('53', '2Thessalonians'),(1, 15): ('54', '1Timothy'),
    (1, 16): ('55', '2Timothy'),     (1, 17): ('56', 'Titus'),        (1, 18): ('57', 'Philemon'),
    (1, 19): ('58', 'Hebrews'),      (1, 20): ('59', 'James'),        (1, 21): ('60', '1Peter'),
    (1, 22): ('61', '2Peter'),       (1, 23): ('62', '1John'),        (1, 24): ('63', '2John'),
    (1, 25): ('64', '3John'),        (1, 26): ('65', 'Jude'),         (1, 27): ('66', 'Revelation'),
}

ENGLISH_ABBREV_MAP = {
    (0,  1):'Gen.',(0,  2):'Exo.',(0,  3):'Lev.',(0,  4):'Num.',(0,  5):'Deut.',(0,  6):'Josh.',
    (0,  7):'Judg.',(0,  8):'Ruth',(0,  9):'1 Sam.',(0, 10):'2 Sam.',(0, 11):'1 Kings',(0, 12):'2 Kings',
    (0, 13):'1 Chron.',(0, 14):'2 Chron.',(0, 15):'Ezra',(0, 16):'Neh.',(0, 17):'Esth.',(0, 18):'Job',
    (0, 19):'Psa.',(0, 20):'Prov.',(0, 21):'Eccl.',(0, 22):'S.S.',(0, 23):'Isa.',(0, 24):'Jer.',
    (0, 25):'Lam.',(0, 26):'Ezek.',(0, 27):'Dan.',(0, 28):'Hos.',(0, 29):'Joel',(0, 30):'Amos',
    (0, 31):'Obad.',(0, 32):'Jon.',(0, 33):'Mic.',(0, 34):'Nah.',(0, 35):'Hab.',(0, 36):'Zeph.',
    (0, 37):'Hag.',(0, 38):'Zech.',(0, 39):'Mal.',
    (1,  1):'Matt.',(1,  2):'Mark',(1,  3):'Luke',(1,  4):'John',(1,  5):'Acts',(1,  6):'Rom.',
    (1,  7):'1 Cor.',(1,  8):'2 Cor.',(1,  9):'Gal.',(1, 10):'Eph.',(1, 11):'Phil.',(1, 12):'Col.',
    (1, 13):'1 Thes.',(1, 14):'2 Thes.',(1, 15):'1 Tim.',(1, 16):'2 Tim.',(1, 17):'Titus',
    (1, 18):'Philem.',(1, 19):'Heb.',(1, 20):'James',(1, 21):'1 Pet.',(1, 22):'2 Pet.',
    (1, 23):'1 John',(1, 24):'2 John',(1, 25):'3 John',(1, 26):'Jude',(1, 27):'Rev.',
}

KOREAN_ABBREV_MAP = {
    (0,  1):'창',(0,  2):'출',(0,  3):'레',(0,  4):'민',(0,  5):'신',(0,  6):'수',
    (0,  7):'삿',(0,  8):'룻',(0,  9):'삼상',(0, 10):'삼하',(0, 11):'왕상',(0, 12):'왕하',
    (0, 13):'대상',(0, 14):'대하',(0, 15):'스',(0, 16):'느',(0, 17):'에',(0, 18):'욥',
    (0, 19):'시',(0, 20):'잠',(0, 21):'전',(0, 22):'아',(0, 23):'사',(0, 24):'렘',
    (0, 25):'애',(0, 26):'겔',(0, 27):'단',(0, 28):'호',(0, 29):'욜',(0, 30):'암',
    (0, 31):'옵',(0, 32):'욘',(0, 33):'미',(0, 34):'나',(0, 35):'합',(0, 36):'습',
    (0, 37):'학',(0, 38):'슥',(0, 39):'말',
    (1,  1):'마',(1,  2):'막',(1,  3):'눅',(1,  4):'요',(1,  5):'행',(1,  6):'롬',
    (1,  7):'고전',(1,  8):'고후',(1,  9):'갈',(1, 10):'엡',(1, 11):'빌',(1, 12):'골',
    (1, 13):'살전',(1, 14):'살후',(1, 15):'딤전',(1, 16):'딤후',(1, 17):'딛',
    (1, 18):'몬',(1, 19):'히',(1, 20):'약',(1, 21):'벧전',(1, 22):'벧후',
    (1, 23):'요일',(1, 24):'요이',(1, 25):'요삼',(1, 26):'유',(1, 27):'계',
}

def get_korean_ref(bv, bso, ch, vs):
    abbrev = KOREAN_ABBREV_MAP.get((bv, bso), '?')
    if vs:
        return f"{abbrev} {ch}:{vs}"
    else:
        return f"{abbrev} {ch}장"

def get_english_ref(bv, bso, ch, vs):
    abbrev = ENGLISH_ABBREV_MAP.get((bv, bso), '?')
    if vs:
        return f"{abbrev} {ch}:{vs}"
    else:
        return f"{abbrev} {ch}"

# 다운로드 속도를 비약적으로 높여주는 장(Chapter) 캐시 메모리
CHAPTER_CACHE = {}
ENGLISH_CHAPTER_CACHE = {}

def fetch_english_verse_text(bible_ver, bible_sel_op, chapter, verse=""):
    if (bible_ver, bible_sel_op) not in ENGLISH_BOOK_MAP:
        return "(영어 회복역: 해당 책 정보 없음)"

    book_num, book_name = ENGLISH_BOOK_MAP[(bible_ver, bible_sel_op)]
    cache_key = f"en_{book_num}_{chapter}"

    if cache_key in ENGLISH_CHAPTER_CACHE:
        soup = ENGLISH_CHAPTER_CACHE[cache_key]
    else:
        url = f"https://text.recoveryversion.bible/{book_num}_{book_name}_{chapter}.htm"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            ENGLISH_CHAPTER_CACHE[cache_key] = soup
        except Exception as e:
            return f"(영어 오류: {e})"

    def extract_by_anchor(s, ch, v):
        # <p id="Heb11-7" class="verse"> 형식: id가 {책약어}{장}-{절}
        p_tag = s.find('p', id=re.compile(rf'^[A-Za-z]+{ch}-{v}$'), class_='verse')
        if not p_tag:
            return None
        # <b> 태그(절 번호 참조) 제거 후 텍스트 추출
        b_tag = p_tag.find('b')
        if b_tag:
            b_tag.extract()
        text = p_tag.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        return text.strip() if text else None

    if verse:
        text = extract_by_anchor(soup, chapter, verse)
        return text if text else "(영어 회복역: 해당 구절을 찾을 수 없습니다)"
    else:
        verses = []
        v = 1
        consecutive_misses = 0
        while True:
            text = extract_by_anchor(soup, chapter, str(v))
            if text:
                verses.append(f"{v} {text}")
                v += 1
                consecutive_misses = 0
            else:
                v += 1
                consecutive_misses += 1
                if consecutive_misses > 3:
                    break
        return ' '.join(verses) if verses else "(영어 회복역: 장 본문을 추출할 수 없습니다)"


def fetch_verse_text(bible_ver, bible_sel_op, chapter, verse=""):
    cache_key = f"{bible_ver}_{bible_sel_op}_{chapter}"
    
    if cache_key in CHAPTER_CACHE:
        raw_full_text = CHAPTER_CACHE[cache_key]
    else:
        url = f"http://rv.or.kr/read_recovery.php?bibleVer={bible_ver}&bibOutline=&bibleSelOp={bible_sel_op}&bibChapt={chapter}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8' if 'utf-8' in response.headers.get('content-type', '').lower() else 'euc-kr'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tag in soup(["script", "style", "header", "footer", "nav", "title", "noscript"]):
                tag.extract()
                
            raw_full_text = soup.get_text(separator=' ', strip=True)
            raw_full_text = re.sub(r'\([가-힣][^\)]*?[-―–—].*?\)', '', raw_full_text)
            raw_full_text = re.sub(r'\s+', ' ', raw_full_text)
            CHAPTER_CACHE[cache_key] = raw_full_text
            
        except Exception as e:
            return f"(오류 발생: {e})"

    def extract_v(text, v):
        start_pattern = rf"(?:^|\s){v}(?!\d)(?!\s*[장편권])\s+"
        match = re.search(start_pattern, text)
        if not match:
            return None
            
        start_idx = match.end()
        end_idx = len(text)
        
        for i in range(1, 10):
            next_v = str(int(v) + i)
            next_pattern = rf"\s{next_v}(?!\d)(?!\s*[장편권])\s+"
            next_match = re.search(next_pattern, text[start_idx:])
            if next_match:
                end_idx = start_idx + next_match.start()
                break
                
        extracted = text[start_idx:end_idx].strip()
        
        cut_regex = (
            r'\s+[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]\.\s+[가-힣]|'   
            r'\s+[A-Z]\.\s+[가-힣]|'                  
            r'\s+[a-z]\.\s+[가-힣]|'                  
            r'\s+\d+\.\s+[가-힣][^\.]*?―|'                    
            r'\s*\([a-z]\)\s+[가-힣][^\)]*?―|'                
            r'\s*\(\d+\)\s+[가-힣][^\)]*?―|'                  
            r'\s*\d+:\d+(-\d+)?\)|'  
            r'\s+제\d+권\s*―|'                        
            r'\s*ᐸ\s*\||' 
            r'\s*\'?(?:main_dim|sub_dim|top_btn)\'?'
        )
        
        extracted = re.split(cut_regex, extracted)[0].strip()
        extracted = re.sub(r'\s*[-―–—]\s*\d+:\d+(-\d+)?.*', '', extracted)
        
        return extracted.strip()

    if verse:
        res = extract_v(raw_full_text, verse)
        return res if res else "해당 구절을 웹페이지에서 찾을 수 없습니다."
    else:
        verses = []
        v = 1
        consecutive_misses = 0
        while True:
            v_text = extract_v(raw_full_text, v)
            if v_text:
                verses.append(f"{v} {v_text}")
                v += 1
                consecutive_misses = 0
            else:
                v += 1
                consecutive_misses += 1
                if consecutive_misses > 3: 
                    break
        
        if verses:
            return " ".join(verses)
        else:
            return "장 본문을 추출할 수 없습니다."

def parse_and_scrape(text_input, output_box, status_label, fetch_btn, include_english=False):
    fetch_btn.config(state=tk.DISABLED)
    status_label.config(text="스크래핑 진행 중... 잠시만 기다려주세요.")
    output_box.delete('1.0', tk.END)
    
    # 🔥 핵심 로직: 한국어 자연어 '장/절' 표현을 기계가 인식하기 쉬운 기호로 사전 정규화(치환)
    text_input = re.sub(r'(\d+)\s*장\s*(?=\d)', r'\1:', text_input)
    text_input = re.sub(r'(\d+)\s*절\s*(?:과|와|및|,\s*)\s*(?=\d)', r'\1, ', text_input)
    text_input = re.sub(r'(\d+)\s*절\s*(?:에서|부터|-|~)\s*(?=\d)', r'\1-', text_input)
    text_input = re.sub(r'(?<=\d)\s*절(?:까지)?', '', text_input)
    
    pattern = r'([가-힣]+)?\s*(\d+)\s*(?:(장)(?:\s*(\d+)절)?|:\s*(\d+(?!\d)(?:\s*-\s*\d+(?!\d))?(?!\s*:)(?:\s*,\s*\d+(?!\d)(?:\s*-\s*\d+(?!\d))?(?!\s*:))*))'
    
    current_book = None
    last_end_pos = -100
    
    results = []
    seen_verses = set()
    
    for match in re.finditer(pattern, text_input):
        book_raw = match.group(1)
        chapter = match.group(2)
        is_jang_word = match.group(3) == '장'
        jang_verse = match.group(4)
        colon_verses_str = match.group(5)
        
        start_pos = match.start()
        
        if book_raw:
            if book_raw in BIBLE_MAP:
                current_book = book_raw
            else:
                continue 
        else:
            if not current_book or (start_pos - last_end_pos) > 500:
                continue
                
        last_end_pos = match.end()
        bible_ver, bible_sel_op = BIBLE_MAP[current_book]
        
        def append_result(bv, bso, ch, vs):
            ko_ref = get_korean_ref(bv, bso, ch, vs)
            text = fetch_verse_text(bv, bso, ch, vs)
            line = f"[{ko_ref}] {text}"
            if include_english:
                en_text = fetch_english_verse_text(bv, bso, ch, vs)
                en_ref = get_english_ref(bv, bso, ch, vs)
                line += f"\n[{en_ref}] {en_text}"
            results.append(line)

        try:
            if is_jang_word and jang_verse:
                unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}:{jang_verse}"
                if unique_key not in seen_verses:
                    seen_verses.add(unique_key)
                    append_result(bible_ver, bible_sel_op, chapter, jang_verse)

            elif is_jang_word and not jang_verse:
                unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}장"
                if unique_key not in seen_verses:
                    seen_verses.add(unique_key)
                    append_result(bible_ver, bible_sel_op, chapter, "")

            elif colon_verses_str:
                verse_parts = colon_verses_str.split(',')
                for part in verse_parts:
                    part = part.strip()
                    if '-' in part:
                        v_start, v_end = part.split('-')
                        for v in range(int(v_start), int(v_end) + 1):
                            unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}:{v}"
                            if unique_key not in seen_verses:
                                seen_verses.add(unique_key)
                                append_result(bible_ver, bible_sel_op, chapter, str(v))
                    else:
                        v = part
                        unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}:{v}"
                        if unique_key not in seen_verses:
                            seen_verses.add(unique_key)
                            append_result(bible_ver, bible_sel_op, chapter, v)
                
        except Exception as e:
            results.append(f"[{current_book} {chapter}장] 관련 오류: {e}")

    if not results:
        output_box.insert(tk.END, "지문에서 유효한 성경 구절을 찾지 못했습니다.")
    else:
        for res in results:
            output_box.insert(tk.END, res + "\n")
            
    status_label.config(text="스크래핑 완료!")
    fetch_btn.config(state=tk.NORMAL)

def on_fetch_click(input_box, output_box, status_label, fetch_btn, include_english_var):
    text_input = input_box.get('1.0', tk.END)
    if not text_input.strip():
        messagebox.showwarning("경고", "먼저 왼쪽에 지문을 입력해주세요.")
        return

    thread = threading.Thread(
        target=parse_and_scrape,
        args=(text_input, output_box, status_label, fetch_btn, include_english_var.get())
    )
    thread.daemon = True
    thread.start()

# ==========================================
# GUI 디자인 부분 (Grid 레이아웃 적용으로 양쪽 크기 동일하게 맞춤)
# ==========================================

root = tk.Tk()
root.title("회복역 성경 가져오기 v1")
root.geometry("1000x600")

_FONT = "Noto Sans KR" if "Noto Sans KR" in tkfont.families() else "맑은 고딕"

# 하단 상태 바를 먼저 바닥에 붙입니다.
status_label = tk.Label(root, text="대기 중...", font=(_FONT, 10), fg="gray")
status_label.pack(side=tk.BOTTOM, anchor="w", padx=10, pady=5)

# 메인 프레임 생성
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# 핵심: 세 구역(왼쪽창, 중앙버튼, 오른쪽창)의 비율을 Grid로 설정
# uniform="equal_cols" 옵션이 두 창의 크기를 수학적으로 똑같이 강제합니다.
main_frame.columnconfigure(0, weight=1, uniform="equal_cols") # 왼쪽
main_frame.columnconfigure(1, weight=0)                       # 중앙 (버튼 크기만큼만)
main_frame.columnconfigure(2, weight=1, uniform="equal_cols") # 오른쪽
main_frame.rowconfigure(0, weight=1)                          # 높이는 꽉 채우게

# 1. 왼쪽 입력 영역
left_frame = tk.Frame(main_frame)
left_frame.grid(row=0, column=0, sticky="nsew")
tk.Label(left_frame, text="입력", font=(_FONT, 12, "bold")).pack(anchor="w")
input_box = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, font=(_FONT, 11))
input_box.pack(fill=tk.BOTH, expand=True, pady=5)

# 2. 오른쪽 결과 영역 (가운데 버튼에서 이 변수를 써야 하므로 먼저 생성)
right_frame = tk.Frame(main_frame)
right_frame.grid(row=0, column=2, sticky="nsew")
tk.Label(right_frame, text="결과", font=(_FONT, 12, "bold")).pack(anchor="w")
output_box = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, font=(_FONT, 11))
output_box.pack(fill=tk.BOTH, expand=True, pady=5)

# 3. 중앙 버튼 영역
mid_frame = tk.Frame(main_frame, bg="#f0f0f0")
mid_frame.grid(row=0, column=1, sticky="ns", padx=8)

# 수직 중앙 정렬용 spacer + btn_group
tk.Frame(mid_frame, bg="#f0f0f0").pack(expand=True, fill=tk.BOTH)

btn_group = tk.Frame(mid_frame, bg="#f0f0f0")
btn_group.pack()

include_english_var = tk.BooleanVar(value=False)
english_chk = tk.Checkbutton(
    btn_group, text="영어 회복역", variable=include_english_var,
    font=(_FONT, 9), bg="#f0f0f0", activebackground="#f0f0f0",
    cursor="hand2"
)
english_chk.pack(pady=(0, 6))

fetch_btn = tk.Button(
    btn_group, text="가져오기 ▶", font=(_FONT, 11, "bold"),
    width=10, height=2, bg="#43a047", fg="white",
    activebackground="#2e7d32", activeforeground="white",
    relief=tk.FLAT, cursor="hand2", bd=0
)
fetch_btn.config(command=lambda: on_fetch_click(input_box, output_box, status_label, fetch_btn, include_english_var))
fetch_btn.pack(fill=tk.X, pady=(0, 6))

clear_btn = tk.Button(
    btn_group, text="지우기", font=(_FONT, 11, "bold"),
    width=10, height=2, bg="#e53935", fg="white",
    activebackground="#b71c1c", activeforeground="white",
    relief=tk.FLAT, cursor="hand2", bd=0,
    command=lambda: (input_box.delete('1.0', tk.END), output_box.delete('1.0', tk.END), status_label.config(text="대기 중..."))
)
clear_btn.pack(fill=tk.X)

tk.Frame(mid_frame, bg="#f0f0f0").pack(expand=True, fill=tk.BOTH)

root.mainloop()