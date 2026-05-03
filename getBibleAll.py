"""
getBibleAll.py
회복역 성경 전체(66권) 다운로드 및 XML 저장 스크립트
한국어: http://rv.or.kr/read_recovery.php
영어: https://text.recoveryversion.bible/
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import os
import sys
import argparse
from xml.etree import ElementTree as ET
from xml.dom import minidom

# ── 책 메타데이터 ────────────────────────────────────────────────────────────

BOOKS = [
    # (bible_ver, bible_sel_op, book_num, korean_name, english_name, abbrev_ko, abbrev_en, testament)
    (0,  1, '01', '창세기',       'Genesis',         '창',   'Gen.',      'OT'),
    (0,  2, '02', '출애굽기',     'Exodus',           '출',   'Exo.',      'OT'),
    (0,  3, '03', '레위기',       'Leviticus',        '레',   'Lev.',      'OT'),
    (0,  4, '04', '민수기',       'Numbers',          '민',   'Num.',      'OT'),
    (0,  5, '05', '신명기',       'Deuteronomy',      '신',   'Deut.',     'OT'),
    (0,  6, '06', '여호수아',     'Joshua',           '수',   'Josh.',     'OT'),
    (0,  7, '07', '사사기',       'Judges',           '삿',   'Judg.',     'OT'),
    (0,  8, '08', '룻기',         'Ruth',             '룻',   'Ruth',      'OT'),
    (0,  9, '09', '사무엘상',     '1Samuel',          '삼상', '1 Sam.',    'OT'),
    (0, 10, '10', '사무엘하',     '2Samuel',          '삼하', '2 Sam.',    'OT'),
    (0, 11, '11', '열왕기상',     '1Kings',           '왕상', '1 Kings',   'OT'),
    (0, 12, '12', '열왕기하',     '2Kings',           '왕하', '2 Kings',   'OT'),
    (0, 13, '13', '역대상',       '1Chronicles',      '대상', '1 Chron.',  'OT'),
    (0, 14, '14', '역대하',       '2Chronicles',      '대하', '2 Chron.',  'OT'),
    (0, 15, '15', '에스라',       'Ezra',             '스',   'Ezra',      'OT'),
    (0, 16, '16', '느헤미야',     'Nehemiah',         '느',   'Neh.',      'OT'),
    (0, 17, '17', '에스더',       'Esther',           '에',   'Esth.',     'OT'),
    (0, 18, '18', '욥기',         'Job',              '욥',   'Job',       'OT'),
    (0, 19, '19', '시편',         'Psalms',           '시',   'Psa.',      'OT'),
    (0, 20, '20', '잠언',         'Proverbs',         '잠',   'Prov.',     'OT'),
    (0, 21, '21', '전도서',       'Ecclesiastes',     '전',   'Eccl.',     'OT'),
    (0, 22, '22', '아가',         'SongofSongs',      '아',   'S.S.',      'OT'),
    (0, 23, '23', '이사야',       'Isaiah',           '사',   'Isa.',      'OT'),
    (0, 24, '24', '예레미야',     'Jeremiah',         '렘',   'Jer.',      'OT'),
    (0, 25, '25', '예레미야애가', 'Lamentations',     '애',   'Lam.',      'OT'),
    (0, 26, '26', '에스겔',       'Ezekiel',          '겔',   'Ezek.',     'OT'),
    (0, 27, '27', '다니엘',       'Daniel',           '단',   'Dan.',      'OT'),
    (0, 28, '28', '호세아',       'Hosea',            '호',   'Hos.',      'OT'),
    (0, 29, '29', '요엘',         'Joel',             '욜',   'Joel',      'OT'),
    (0, 30, '30', '아모스',       'Amos',             '암',   'Amos',      'OT'),
    (0, 31, '31', '오바댜',       'Obadiah',          '옵',   'Obad.',     'OT'),
    (0, 32, '32', '요나',         'Jonah',            '욘',   'Jon.',      'OT'),
    (0, 33, '33', '미가',         'Micah',            '미',   'Mic.',      'OT'),
    (0, 34, '34', '나훔',         'Nahum',            '나',   'Nah.',      'OT'),
    (0, 35, '35', '하박국',       'Habakkuk',         '합',   'Hab.',      'OT'),
    (0, 36, '36', '스바냐',       'Zephaniah',        '습',   'Zeph.',     'OT'),
    (0, 37, '37', '학개',         'Haggai',           '학',   'Hag.',      'OT'),
    (0, 38, '38', '스가랴',       'Zechariah',        '슥',   'Zech.',     'OT'),
    (0, 39, '39', '말라기',       'Malachi',          '말',   'Mal.',      'OT'),
    (1,  1, '40', '마태복음',     'Matthew',          '마',   'Matt.',     'NT'),
    (1,  2, '41', '마가복음',     'Mark',             '막',   'Mark',      'NT'),
    (1,  3, '42', '누가복음',     'Luke',             '눅',   'Luke',      'NT'),
    (1,  4, '43', '요한복음',     'John',             '요',   'John',      'NT'),
    (1,  5, '44', '사도행전',     'Acts',             '행',   'Acts',      'NT'),
    (1,  6, '45', '로마서',       'Romans',           '롬',   'Rom.',      'NT'),
    (1,  7, '46', '고린도전서',   '1Corinthians',     '고전', '1 Cor.',    'NT'),
    (1,  8, '47', '고린도후서',   '2Corinthians',     '고후', '2 Cor.',    'NT'),
    (1,  9, '48', '갈라디아서',   'Galatians',        '갈',   'Gal.',      'NT'),
    (1, 10, '49', '에베소서',     'Ephesians',        '엡',   'Eph.',      'NT'),
    (1, 11, '50', '빌립보서',     'Philippians',      '빌',   'Phil.',     'NT'),
    (1, 12, '51', '골로새서',     'Colossians',       '골',   'Col.',      'NT'),
    (1, 13, '52', '데살로니가전서','1Thessalonians',  '살전', '1 Thes.',   'NT'),
    (1, 14, '53', '데살로니가후서','2Thessalonians',  '살후', '2 Thes.',   'NT'),
    (1, 15, '54', '디모데전서',   '1Timothy',         '딤전', '1 Tim.',    'NT'),
    (1, 16, '55', '디모데후서',   '2Timothy',         '딤후', '2 Tim.',    'NT'),
    (1, 17, '56', '디도서',       'Titus',            '딛',   'Titus',     'NT'),
    (1, 18, '57', '빌레몬서',     'Philemon',         '몬',   'Philem.',   'NT'),
    (1, 19, '58', '히브리서',     'Hebrews',          '히',   'Heb.',      'NT'),
    (1, 20, '59', '야고보서',     'James',            '약',   'James',     'NT'),
    (1, 21, '60', '베드로전서',   '1Peter',           '벧전', '1 Pet.',    'NT'),
    (1, 22, '61', '베드로후서',   '2Peter',           '벧후', '2 Pet.',    'NT'),
    (1, 23, '62', '요한일서',     '1John',            '요일', '1 John',    'NT'),
    (1, 24, '63', '요한이서',     '2John',            '요이', '2 John',    'NT'),
    (1, 25, '64', '요한삼서',     '3John',            '요삼', '3 John',    'NT'),
    (1, 26, '65', '유다서',       'Jude',             '유',   'Jude',      'NT'),
    (1, 27, '66', '요한계시록',   'Revelation',       '계',   'Rev.',      'NT'),
]

# ── 각 책의 장별 절 수 ────────────────────────────────────────────────────────

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
    (0, 19): [6,12,8,8,12,10,17,9,20,18,7,8,6,7,5,11,15,50,14,9,13,31,6,10,22,12,14,9,11,12,24,11,22,22,28,12,40,22,13,17,13,11,5,26,17,11,9,14,20,23,19,9,6,7,23,13,11,17,12,8,12,11,10,13,20,7,35,36,5,24,20,28,23,10,12,20,72,13,19,16,8,18,12,13,17,7,18,52,17,16,15,5,23,11,13,12,9,9,5,8,28,22,35,45,48,43,13,31,7,10,10,9,8,18,19,2,29,176,7,8,9,4,8,5,6,5,6,8,8,3,18,3,3,21,26,9,8,24,13,10,7,12,15,21,10,20,14,9,6,6],
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

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# ── 크롤링 함수 ───────────────────────────────────────────────────────────────

def fetch_korean_chapter(bible_ver, bible_sel_op, chapter, retries=3):
    url = (f"http://rv.or.kr/read_recovery.php"
           f"?bibleVer={bible_ver}&bibOutline=&bibleSelOp={bible_sel_op}&bibChapt={chapter}")
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            ct = resp.headers.get('content-type', '').lower()
            resp.encoding = 'utf-8' if 'utf-8' in ct else 'euc-kr'
            return BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"한국어 다운로드 실패 ({bible_ver},{bible_sel_op},{chapter}): {e}")


def fetch_english_chapter(book_num, book_name, chapter, retries=3):
    url = f"https://text.recoveryversion.bible/{book_num}_{book_name}_{chapter}.htm"
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.encoding = 'utf-8'
            return BeautifulSoup(resp.text, 'html.parser')
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise RuntimeError(f"영어 다운로드 실패 ({book_num},{book_name},{chapter}): {e}")


def extract_korean_verse(soup, verse_num):
    num_div = soup.find('div', class_='num', id=str(verse_num))
    if num_div:
        parent = num_div.parent
        text_div = parent.find('div', class_='text')
        if text_div:
            return text_div.get_text(strip=True)
    return None


def extract_english_verse(soup, chapter, verse_num):
    p_tag = soup.find('p', id=re.compile(rf'^[A-Za-z]+{chapter}-{verse_num}$'), class_='verse')
    if not p_tag:
        return None
    b_tag = p_tag.find('b')
    if b_tag:
        b_tag.extract()
    text = p_tag.get_text(separator=' ', strip=True)
    return re.sub(r'\s+', ' ', text).strip() or None

# ── XML 빌더 ─────────────────────────────────────────────────────────────────

def prettify_xml(elem):
    rough = ET.tostring(elem, encoding='unicode')
    reparsed = minidom.parseString(rough.encode('utf-8'))
    return reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')

# ── 메인 다운로드 루프 ────────────────────────────────────────────────────────

def download_bible(lang='ko', output_path=None, delay=0.3, book_range=None, bilingual=False):
    """
    lang       : 'ko' | 'en'  (bilingual=True 이면 무시되고 둘 다 저장)
    bilingual  : True 이면 <Verse> 안에 <Ko>/<En> 둘 다 저장
    output_path: 저장할 xml 파일 경로 (None 이면 자동 결정)
    delay      : 요청 간 대기 시간(초)
    book_range : (start, end) 1-based 인덱스 (포함). None 이면 전체 66권
    """
    if output_path is None:
        output_path = 'recovery_bible_bilingual.xml' if bilingual else f"recovery_bible_{lang}.xml"

    root_elem = ET.Element('Bible')
    root_elem.set('version', 'RecoveryVersion')
    root_elem.set('language', 'Korean+English' if bilingual else ('Korean' if lang == 'ko' else 'English'))
    root_elem.set('books', '66')

    books_to_process = BOOKS
    if book_range:
        s, e = book_range
        books_to_process = BOOKS[s - 1: e]

    total_books = len(books_to_process)
    total_verses_downloaded = 0

    for book_idx, book in enumerate(books_to_process):
        bv, bso, book_num, ko_name, en_name, abbrev_ko, abbrev_en, testament = book
        key = (bv, bso)
        chapters = VERSE_COUNTS.get(key, [])
        book_display = f"{ko_name} / {en_name}" if bilingual else (ko_name if lang == 'ko' else en_name)

        print(f"\n[{book_idx+1:2d}/{total_books}] {book_display} ({len(chapters)}장) 다운로드 중...", flush=True)

        book_elem = ET.SubElement(root_elem, 'Book')
        book_elem.set('num', str(int(book_num)))
        book_elem.set('nameKo', ko_name)
        book_elem.set('nameEn', en_name)
        book_elem.set('abbrevKo', abbrev_ko)
        book_elem.set('abbrevEn', abbrev_en)
        book_elem.set('testament', testament)
        book_elem.set('chapters', str(len(chapters)))

        for ch_idx, max_verse in enumerate(chapters):
            ch_num = ch_idx + 1

            chapter_elem = ET.SubElement(book_elem, 'Chapter')
            chapter_elem.set('num', str(ch_num))
            chapter_elem.set('verses', str(max_verse))

            try:
                if bilingual:
                    ko_soup = fetch_korean_chapter(bv, bso, ch_num)
                    time.sleep(delay)
                    en_soup = fetch_english_chapter(book_num, en_name, ch_num)
                    for v in range(1, max_verse + 1):
                        ko_text = extract_korean_verse(ko_soup, v)
                        en_text = extract_english_verse(en_soup, ch_num, v)
                        verse_elem = ET.SubElement(chapter_elem, 'Verse')
                        verse_elem.set('num', str(v))
                        ET.SubElement(verse_elem, 'Ko').text = ko_text if ko_text else ''
                        ET.SubElement(verse_elem, 'En').text = en_text if en_text else ''
                        if not ko_text:
                            print(f"  경고: {ko_name} {ch_num}:{v} 한국어 본문 없음", flush=True)
                        if not en_text:
                            print(f"  경고: {en_name} {ch_num}:{v} 영어 본문 없음", flush=True)
                elif lang == 'ko':
                    soup = fetch_korean_chapter(bv, bso, ch_num)
                    for v in range(1, max_verse + 1):
                        text = extract_korean_verse(soup, v)
                        verse_elem = ET.SubElement(chapter_elem, 'Verse')
                        verse_elem.set('num', str(v))
                        verse_elem.text = text if text else ''
                        if not text:
                            print(f"  경고: {ko_name} {ch_num}:{v} 본문 없음", flush=True)
                else:
                    soup = fetch_english_chapter(book_num, en_name, ch_num)
                    for v in range(1, max_verse + 1):
                        text = extract_english_verse(soup, ch_num, v)
                        verse_elem = ET.SubElement(chapter_elem, 'Verse')
                        verse_elem.set('num', str(v))
                        verse_elem.text = text if text else ''
                        if not text:
                            print(f"  경고: {en_name} {ch_num}:{v} 본문 없음", flush=True)

                total_verses_downloaded += max_verse
                print(f"  {ch_num:3d}장 완료 ({max_verse}절) | 누적 {total_verses_downloaded:,}절", end='\r', flush=True)

            except RuntimeError as e:
                print(f"\n  오류: {e} — 빈 장으로 기록 후 계속", flush=True)

            time.sleep(delay)

        print(f"  {len(chapters)}장 완료 — {book_display} 다운로드 완료          ", flush=True)

        # 책 단위로 중간 저장 (중단 시 데이터 보호)
        _save_xml(root_elem, output_path)

    print(f"\n전체 완료: {total_verses_downloaded:,}절 → {output_path}", flush=True)
    return output_path


def _save_xml(root_elem, path):
    xml_str = prettify_xml(root_elem)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(xml_str)

# ── CLI 진입점 ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='회복역 성경 전체(66권) 다운로드 → XML 저장',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""예시:
  python getBibleAll.py                    # 한국어 전체 66권
  python getBibleAll.py --lang en          # 영어 전체 66권
  python getBibleAll.py --both             # 한국어/영어 각각 별도 파일로 저장
  python getBibleAll.py --bilingual        # 한국어+영어 하나의 파일로 저장
  python getBibleAll.py --books 40 66      # 신약만 (40~66번째 책)
  python getBibleAll.py --output my.xml    # 저장 파일명 지정 (단일 언어 시)
  python getBibleAll.py --delay 0.5        # 요청 간격 0.5초
"""
    )
    parser.add_argument(
        '--lang', choices=['ko', 'en'], default='ko',
        help="다운로드 언어: ko(한국어) | en(영어). 기본: ko"
    )
    parser.add_argument(
        '--both', action='store_true',
        help="한국어(recovery_bible_ko.xml)와 영어(recovery_bible_en.xml)를 각각 별도 파일로 저장"
    )
    parser.add_argument(
        '--bilingual', action='store_true',
        help="한국어+영어를 하나의 XML에 저장 (<Verse> 안에 <Ko>/<En> 태그)"
    )
    parser.add_argument(
        '--output', '-o', type=str, default=None,
        help="저장 파일명 지정 (단일 언어 또는 --bilingual 시)"
    )
    parser.add_argument(
        '--books', nargs=2, type=int, metavar=('START', 'END'),
        help="다운로드할 책 범위 (1~66). 예: --books 40 66 → 신약"
    )
    parser.add_argument(
        '--delay', type=float, default=0.3,
        help="요청 간 대기 시간(초). 기본: 0.3"
    )

    args = parser.parse_args()
    book_range = tuple(args.books) if args.books else None

    try:
        if args.both:
            for lang, label, out in [
                ('ko', '한국어', 'recovery_bible_ko.xml'),
                ('en', '영어',   'recovery_bible_en.xml'),
            ]:
                print(f"\n{'='*60}")
                print(f"  회복역 성경 다운로드 시작")
                print(f"  언어  : {label}")
                print(f"  범위  : {f'책 {book_range[0]}~{book_range[1]}' if book_range else '전체 66권'}")
                print(f"  출력  : {out}")
                print(f"  대기  : {args.delay}초/장")
                print(f"{'='*60}\n")
                download_bible(lang=lang, output_path=out, delay=args.delay, book_range=book_range)
        elif args.bilingual:
            out = args.output or 'recovery_bible_bilingual.xml'
            print(f"\n{'='*60}")
            print(f"  회복역 성경 다운로드 시작")
            print(f"  언어  : 한국어 + 영어 (이중 언어)")
            print(f"  범위  : {f'책 {book_range[0]}~{book_range[1]}' if book_range else '전체 66권'}")
            print(f"  출력  : {out}")
            print(f"  대기  : {args.delay}초/장")
            print(f"{'='*60}\n")
            download_bible(lang='ko', output_path=out, delay=args.delay, book_range=book_range, bilingual=True)
        else:
            out = args.output or f"recovery_bible_{args.lang}.xml"
            label = '한국어' if args.lang == 'ko' else '영어'
            print(f"\n{'='*60}")
            print(f"  회복역 성경 다운로드 시작")
            print(f"  언어  : {label}")
            print(f"  범위  : {f'책 {book_range[0]}~{book_range[1]}' if book_range else '전체 66권'}")
            print(f"  출력  : {out}")
            print(f"  대기  : {args.delay}초/장")
            print(f"{'='*60}\n")
            download_bible(lang=args.lang, output_path=out, delay=args.delay, book_range=book_range)
    except KeyboardInterrupt:
        print("\n\n중단됨 — 현재까지 저장된 내용은 파일에 보존됩니다.")
        sys.exit(0)


if __name__ == '__main__':
    main()
