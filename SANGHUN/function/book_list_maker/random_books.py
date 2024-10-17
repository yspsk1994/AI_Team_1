import requests
import json
import pandas as pd
import random
import time
import re
from difflib import SequenceMatcher

# 네이버 API 인증 정보
client_id = "ZdFdgTcPMrhWAz6Ztjif"
client_secret = "lI7VqMZ8k_"

# 검색 키워드 리스트와 해당하는 청구기호
keywords_and_codes = {
    "소설": "800",
    "문학": "800",
    "시": "800",
    "에세이": "800",
    "경제": "320",
    "경영": "320",
    "자기계발": "180",
    "인문": "100",
    "역사": "900",
    "과학": "400",
    "예술": "600",
    "대중문화": "600",
    "사회": "300",
    "종교": "200",
}

# 결과를 저장할 리스트
books = []

# 한글 포함 여부를 확인하는 함수
def contains_korean(text):
    return bool(re.search('[가-힣]', text))

# 시리즈 도서인지 확인하는 함수
def is_series(title):
    series_patterns = [r'\d+권', r'시리즈', r'[0-9]+']
    return any(re.search(pattern, title) for pattern in series_patterns)

# 제목 유사도를 확인하는 함수
def title_similarity(title1, title2):
    return SequenceMatcher(None, title1, title2).ratio()

while len(books) < 1000:
    keyword, code = random.choice(list(keywords_and_codes.items()))
    start = random.randint(1, 900)
    
    url = f"https://openapi.naver.com/v1/search/book.json?query={keyword}&display=100&start={start}&sort=sim"
    
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = json.loads(response.text)
        for item in data['items']:
            title = item.get('title', '')
            
            # 한글 제목이고, 시리즈가 아니며, 기존 책들과 제목 유사도가 50% 미만인 경우에만 추가
            if contains_korean(title) and not is_series(title) and len(books) < 1000:
                # 제목 유사도 체크
                if not any(title_similarity(title, book['제목']) >= 0.5 for book in books):
                    books.append({
                        '제목': title,
                        '저자': item.get('author', ''),
                        '출판사': item.get('publisher', ''),
                        'ISBN': item.get('isbn', ''),
                        '출판일': item.get('pubdate', ''),
                        '청구기호': code
                    })
    else:
        print(f"Error: {response.status_code}")
    
    time.sleep(0.1)  # 네이버 API 사용 제한 고려

df = pd.DataFrame(books)
df.to_excel('random_korean_books_naver.xlsx', index=False)

print("1000권의 한국어 제목 도서 상세 정보가 'random_korean_books_naver.xlsx' 파일로 저장되었습니다.")