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

# 각 책의 장별 절 수 (인덱스 0 = 1장)
VERSE_COUNTS = {
    (0,  1): [31,25,24,26,32,22,24,22,29,32,32,20,18,24,21,16,27,33,38,18,34,24,20,67,34,35,46,22,35,43,55,32,20,31,29,43,36,30,23,23,57,38,34,34,28,34,31,22,33,26],
    (0,  2): [22,25,22,31,23,30,25,32,35,29,10,51,22,31,27,36,16,27,25,26,36,31,33,18,40,37,21,43,46,38,18,35,23,35,35,38,29,31,43,38],
    (0,  3): [17,16,17,35,19,30,38,36,24,20,47,8,59,57,33,34,16,30,37,27,24,33,44,23,55,46,34],
    (0,  4): [54,34,51,49,31,27,89,26,23,36,35,16,33,45,41,50,13,32,22,29,35,41,30,25,18,65,23,31,40,16,54,42,56,29,34,13],
    (0,  5): [46,37,29,49,33,25,26,20,29,22,32,32,18,29,23,22,20,22,21,20,23,30,25,22,19,19,26,68,29,20,30,52,29,12],
    (0,  6): [18,24,17,24,15,27,26,35,27,43,23,24,33,15,63,10,18,28,51,9,45,34,16,33],
    (0,  7): [36,23,31,24,31,40,25,35,57,18,40,15,25,20,20,31,13,31,30,48,25],
    (0,  8): [22,23,18,22],
    (0,  9): [28,36,21,22,12,21,17,22,27,27,15,25,23,52,35,23,58,30,24,42,15,23,29,22,44,25,12,25,11,31,13],
    (0, 10): [27,32,39,12,25,23,29,18,13,19,27,31,39,33,37,23,29,33,43,26,22,51,39,25],
    (0, 11): [53,46,28,34,18,38,51,66,28,29,43,33,34,31,34,34,24,46,21,43,29,53],
    (0, 12): [18,25,27,44,27,33,20,29,37,36,21,21,25,29,38,20,41,37,37,21,26,20,37,20,30],
    (0, 13): [54,55,24,43,26,81,40,40,44,14,47,40,14,17,29,43,27,17,19,8,30,19,32,31,31,32,34,21,30],
    (0, 14): [17,18,17,22,14,42,22,18,31,19,23,16,22,15,19,14,19,34,11,37,20,12,21,27,28,23,9,27,36,27,21,33,25,33,27,23],
    (0, 15): [11,70,13,24,17,22,28,36,15,44],
    (0, 16): [11,20,32,23,19,19,73,18,38,39,36,47,31],
    (0, 17): [22,23,15,17,14,14,10,17,32,3],
    (0, 18): [22,13,26,21,27,30,21,22,35,22,20,25,28,22,35,22,16,21,29,29,34,30,17,25,6,14,23,28,25,31,40,22,33,37,16,33,24,41,30,24,34,17],
    (0, 19): [6,12,8,8,12,10,17,9,20,18,7,8,6,7,5,11,15,50,14,9,13,31,6,10,22,12,14,9,11,12,24,11,22,22,28,12,40,22,13,17,13,11,5,26,17,11,9,14,20,23,19,9,6,7,23,13,11,17,12,8,12,11,10,13,20,7,35,36,5,24,20,28,23,10,12,20,72,13,19,16,8,18,12,13,17,7,18,52,17,16,15,5,23,11,13,12,9,9,5,8,28,22,35,45,48,43,13,31,7,10,10,9,8,18,19,2,29,176,7,8,9,4,8,5,6,5,6,8,8,3,18,3,3,21,26,9,8,24,13,10,7,12,15,21,10,20,14,9,6],
    (0, 20): [33,22,35,27,23,35,27,36,18,32,31,28,25,35,33,33,28,24,29,30,31,29,35,34,28,28,27,28,27,33,31],
    (0, 21): [18,26,22,16,20,12,29,17,18,20,10,14],
    (0, 22): [17,17,11,16,16,13,13,14],
    (0, 23): [31,22,26,6,30,13,25,22,21,34,16,6,22,32,9,14,14,7,25,6,17,25,18,23,12,21,13,29,24,33,9,20,24,17,10,22,38,22,8,31,29,25,28,28,25,13,15,22,26,11,23,15,12,17,13,12,21,14,21,22,11,12,19,12,25,24],
    (0, 24): [19,37,25,31,31,30,34,22,26,25,23,17,27,22,21,21,27,23,15,18,14,30,40,10,38,24,22,17,32,24,40,44,26,22,19,32,21,28,18,16,18,22,13,30,5,28,7,47,39,46,64,34],
    (0, 25): [22,22,66,22,22],
    (0, 26): [28,10,27,17,17,14,27,18,11,22,25,28,23,23,8,63,24,32,14,49,32,31,49,27,17,21,36,26,21,26,18,32,33,31,15,38,28,23,29,49,26,20,27,31,25,24,23,35],
    (0, 27): [21,49,30,37,31,28,28,27,27,21,45,13],
    (0, 28): [11,23,5,19,15,11,16,14,17,15,12,14,16,9],
    (0, 29): [20,32,21],
    (0, 30): [15,16,15,13,27,14,17,14,15],
    (0, 31): [21],
    (0, 32): [17,10,10,11],
    (0, 33): [16,13,12,13,15,16,20],
    (0, 34): [15,13,19],
    (0, 35): [17,20,19],
    (0, 36): [18,15,20],
    (0, 37): [15,23],
    (0, 38): [21,13,10,14,11,15,14,23,17,12,17,14,9,21],
    (0, 39): [14,17,18,6],
    (1,  1): [25,23,17,25,48,34,29,34,38,42,30,50,58,36,39,28,27,35,30,34,46,46,39,51,46,75,66,20],
    (1,  2): [45,28,35,41,43,56,37,38,50,52,33,44,37,72,47,20],
    (1,  3): [80,52,38,44,39,49,50,56,62,42,54,59,35,35,32,31,37,43,48,47,38,71,56,53],
    (1,  4): [51,25,36,54,47,71,53,59,41,42,57,50,38,31,27,33,26,40,42,31,25],
    (1,  5): [26,47,26,37,42,15,60,40,43,48,30,25,52,28,41,40,34,28,41,38,40,30,35,27,27,32,44,31],
    (1,  6): [32,29,31,25,21,23,25,39,33,21,36,21,14,23,33,27],
    (1,  7): [31,16,23,21,13,20,40,13,27,33,34,31,13,40,58,24],
    (1,  8): [24,17,18,18,21,18,16,24,15,18,33,21,14],
    (1,  9): [24,21,29,31,26,18],
    (1, 10): [23,22,21,32,33,24],
    (1, 11): [30,30,21,23],
    (1, 12): [29,23,25,18],
    (1, 13): [10,20,13,18,28],
    (1, 14): [12,17,18],
    (1, 15): [20,15,16,16,25,21],
    (1, 16): [18,26,17,22],
    (1, 17): [16,15,15],
    (1, 18): [25],
    (1, 19): [14,18,19,16,14,20,28,13,28,39,40,29,25],
    (1, 20): [27,26,18,17,20],
    (1, 21): [25,25,22,19,14],
    (1, 22): [21,22,18],
    (1, 23): [10,29,24,21,21],
    (1, 24): [13],
    (1, 25): [14],
    (1, 26): [25],
    (1, 27): [20,29,22,11,14,17,17,13,21,11,19,18,18,20,8,21,18,24,21,15,27,21],
}

def validate_ref(bv, bso, ch, vs):
    key = (bv, bso)
    if key not in VERSE_COUNTS:
        return False, "책 정보를 찾을 수 없습니다."
    chapters = VERSE_COUNTS[key]
    ch_int = int(ch)
    if ch_int < 1 or ch_int > len(chapters):
        book = KOREAN_ABBREV_MAP.get(key, '?')
        return False, f"{book} {ch}장은 존재하지 않습니다. (최대 {len(chapters)}장)"
    if vs:
        vs_int = int(vs)
        max_vs = chapters[ch_int - 1]
        if vs_int < 1 or vs_int > max_vs:
            book = KOREAN_ABBREV_MAP.get(key, '?')
            return False, f"{book} {ch}:{vs}은 존재하지 않습니다. ({ch}장 최대 {max_vs}절)"
    return True, None

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
        soup = CHAPTER_CACHE[cache_key]
    else:
        url = f"http://rv.or.kr/read_recovery.php?bibleVer={bible_ver}&bibOutline=&bibleSelOp={bible_sel_op}&bibChapt={chapter}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = 'utf-8' if 'utf-8' in response.headers.get('content-type', '').lower() else 'euc-kr'
            soup = BeautifulSoup(response.text, 'html.parser')
            CHAPTER_CACHE[cache_key] = soup
        except Exception as e:
            return f"(오류 발생: {e})"

    def extract_v(v):
        # <div class="num" id="절번호"> 구조를 직접 찾아서 정확한 절 텍스트 추출
        num_div = soup.find('div', class_='num', id=str(v))
        if num_div:
            parent_verse = num_div.parent
            text_div = parent_verse.find('div', class_='text')
            if text_div:
                return text_div.get_text(strip=True)
        return None

    if verse:
        res = extract_v(verse)
        return res if res else "해당 구절을 웹페이지에서 찾을 수 없습니다."
    else:
        verses = []
        v = 1
        consecutive_misses = 0
        while True:
            v_text = extract_v(str(v))
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
    status_label.config(text="가져오기 진행 중... 잠시만 기다려주세요.")
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

    def append_result(bv, bso, ch, vs):
        valid, err_msg = validate_ref(bv, bso, ch, vs)
        if not valid:
            results.append(f"[오류] {err_msg}")
            return
        ko_ref = get_korean_ref(bv, bso, ch, vs)
        text = fetch_verse_text(bv, bso, ch, vs)
        line = f"[{ko_ref}] {text}"
        if include_english:
            en_text = fetch_english_verse_text(bv, bso, ch, vs)
            en_ref = get_english_ref(bv, bso, ch, vs)
            line += f"\n[{en_ref}] {en_text}"
        results.append(line)

    # 장 횡단 범위 처리: "히 1:1-3:1" → 1장1절 ~ 3장1절 전체 구절
    def expand_cross_range(m):
        book_raw = m.group(1)
        if book_raw not in BIBLE_MAP:
            return m.group(0)
        bv, bso = BIBLE_MAP[book_raw]
        ch1, v1, ch2, v2 = int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))
        key = (bv, bso)
        if key not in VERSE_COUNTS or ch1 > ch2:
            return m.group(0)
        chapters = VERSE_COUNTS[key]
        for ch in range(ch1, min(ch2, len(chapters)) + 1):
            max_v = chapters[ch - 1]
            start_v = v1 if ch == ch1 else 1
            end_v = v2 if ch == ch2 else max_v
            for v in range(start_v, min(end_v, max_v) + 1):
                ukey = f"{bv}_{bso}_{ch}:{v}"
                if ukey not in seen_verses:
                    seen_verses.add(ukey)
                    append_result(bv, bso, str(ch), str(v))
        return ''  # 본 루프에서 중복 처리되지 않도록 제거

    cross_pattern = r'([가-힣]+)\s*(\d+):(\d+)\s*-\s*(\d+):(\d+)'
    text_input = re.sub(cross_pattern, expand_cross_range, text_input)

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

        try:
            if is_jang_word and jang_verse:
                unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}:{jang_verse}"
                if unique_key not in seen_verses:
                    seen_verses.add(unique_key)
                    append_result(bible_ver, bible_sel_op, chapter, jang_verse)

            elif is_jang_word and not jang_verse:
                key = (bible_ver, bible_sel_op)
                ch_int = int(chapter)
                max_v = VERSE_COUNTS.get(key, [0] * ch_int)[ch_int - 1] if key in VERSE_COUNTS and ch_int <= len(VERSE_COUNTS[key]) else 0
                for v in range(1, max_v + 1):
                    unique_key = f"{bible_ver}_{bible_sel_op}_{chapter}:{v}"
                    if unique_key not in seen_verses:
                        seen_verses.add(unique_key)
                        append_result(bible_ver, bible_sel_op, chapter, str(v))

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
            
    status_label.config(text="가져오기 완료!")
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
    width=10, height=2, bg="#43a047", fg="black",
    activebackground="#2e7d32", activeforeground="black",
    relief=tk.FLAT, cursor="hand2", bd=0,
    highlightbackground="#43a047", highlightthickness=2
)
fetch_btn.config(command=lambda: on_fetch_click(input_box, output_box, status_label, fetch_btn, include_english_var))
fetch_btn.pack(fill=tk.X, pady=(0, 6))

clear_btn = tk.Button(
    btn_group, text="지우기", font=(_FONT, 11, "bold"),
    width=10, height=2, bg="#e53935", fg="black",
    activebackground="#b71c1c", activeforeground="black",
    relief=tk.FLAT, cursor="hand2", bd=0,
    highlightbackground="#e53935", highlightthickness=2,
    command=lambda: (input_box.delete('1.0', tk.END), output_box.delete('1.0', tk.END), status_label.config(text="대기 중..."))
)
clear_btn.pack(fill=tk.X)

tk.Frame(mid_frame, bg="#f0f0f0").pack(expand=True, fill=tk.BOTH)

root.mainloop()