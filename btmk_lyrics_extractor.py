# -*- coding: utf-8 -*-
"""
btmk.org 찬송 앨범 가사 일괄 추출 스크립트

사용법:
    python btmk_lyrics_extractor.py              # 기본값: index 1 ~ 159
    python btmk_lyrics_extractor.py 200          # index 1 ~ 200
    python btmk_lyrics_extractor.py 50 100       # index 50 ~ 100

결과:
    lyrics/ 폴더 아래에 앨범별 텍스트 파일로 저장됩니다.
    예) lyrics/0159_[전체 찬송] 2025년 여름 권역별 어린이 특별 집회.txt

필요 패키지:
    pip install requests beautifulsoup4
"""
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ── 설정 ─────────────────────────────────────────────
BASE_URL = "https://btmk.org/praise/player.php?where=album&index={}"
OUT_DIR = Path("lyrics")   # 결과 저장 폴더
DELAY_SEC = 1.0            # 요청 간격(초) — 서버 부하 방지용, 너무 줄이지 마세요
TIMEOUT = 10               # 요청 타임아웃(초)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

SEP = "\n\n" + "=" * 40 + "\n\n"   # 곡 사이 구분선
# ─────────────────────────────────────────────────────


def sanitize_filename(name: str) -> str:
    """파일명에 쓸 수 없는 문자를 _ 로 치환"""
    return re.sub(r'[\\/:*?"<>|]+', "_", name).strip() or "untitled"


def parse_album(html: str):
    """앨범 페이지 HTML에서 (앨범 제목, [곡별 가사 리스트]) 추출"""
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("span.p_life_title")
    album_title = title_tag.get_text(strip=True) if title_tag else ""

    songs = []
    for div in soup.select("div.lyrics"):
        # <br/> 뒤에 소스 개행문자가 붙어 있어 단순 \n 치환 시 빈 줄이 두 배가 됨
        # → 마커로 치환 후 분리하는 방식으로 처리
        for br in div.find_all("br"):
            br.replace_with("[[BR]]")
        lines = [seg.strip() for seg in div.get_text().split("[[BR]]")]
        songs.append("\n".join(lines).strip())

    return album_title, songs


def main(start: int, end: int):
    OUT_DIR.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)

    ok = skipped = failed = 0
    print(f"index {start} ~ {end} 추출 시작 (요청 간격 {DELAY_SEC}초)\n")

    for idx in range(start, end + 1):
        # 이미 저장된 앨범은 건너뜀 → 중단 후 재실행해도 이어서 진행 가능
        if list(OUT_DIR.glob(f"{idx:04d}_*.txt")):
            print(f"[{idx}] 이미 존재 — 건너뜀")
            continue

        try:
            res = session.get(BASE_URL.format(idx), timeout=TIMEOUT)
            res.encoding = "utf-8"

            if res.status_code != 200:
                print(f"[{idx}] HTTP {res.status_code} — 건너뜀")
                skipped += 1
                time.sleep(DELAY_SEC)
                continue

            album_title, songs = parse_album(res.text)

            if not songs:
                print(f"[{idx}] 가사 없음 — 건너뜀")
                skipped += 1
                time.sleep(DELAY_SEC)
                continue

            fpath = OUT_DIR / f"{idx:04d}_{sanitize_filename(album_title)}.txt"
            header = f"앨범: {album_title}\nindex: {idx}\n수록곡: {len(songs)}곡"
            fpath.write_text(header + SEP + SEP.join(songs), encoding="utf-8")
            print(f"[{idx}] {album_title} — {len(songs)}곡 저장")
            ok += 1

        except requests.RequestException as e:
            print(f"[{idx}] 요청 실패: {e}")
            failed += 1

        time.sleep(DELAY_SEC)

    print(f"\n완료 — 저장 {ok} / 건너뜀 {skipped} / 실패 {failed}")
    print(f"결과 폴더: {OUT_DIR.resolve()}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 2:
        start, end = int(args[0]), int(args[1])
    elif len(args) == 1:
        start, end = 1, int(args[0])
    else:
        start, end = 1, 200   # 기본 범위

    if start < 1 or end < start:
        sys.exit("범위가 올바르지 않습니다. 예: python btmk_lyrics_extractor.py 1 159")

    main(start, end)