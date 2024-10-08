import requests
import json

# 알라딘 API 설정
API_KEY = 'ttbyspsk19941021001'  # 알라딘에서 발급받은 API 키를 입력하세요.
API_URL = 'http://www.aladin.co.kr/ttb/api/ItemSearch.aspx'

# 검색할 쿼리 (책 제목 또는 키워드)
query = '무협'  # 검색할 책 키워드를 입력하세요.

# API 호출 파라미터 설정
params = {
    'ttbkey': API_KEY,            # API 키
    'Query': query,               # 검색어
    'QueryType': 'Title',         # 검색 타입: 제목 기준
    'MaxResults': 100000,             # 최대 결과 개수
    'start': 1,                   # 시작 페이지
    'SearchTarget': 'Book',       # 검색 대상: 도서
    'output': 'js',               # 출력 포맷: JSON
    'Version': '20131101'         # API 버전
}

# API 호출
response = requests.get(API_URL, params=params)

# 응답 데이터 확인
if response.status_code == 200:
    data = response.json()

    # 결과가 정상적으로 들어온 경우 처리
    books = []
    for item in data['item']:
        book_info = {
            'text': item['title'],  # 책 제목
            'label': 0              # 책 제목은 label 0
        }
        books.append(book_info)

        # 저자 정보 추가
        author_info = {
            'text': item['author'],  # 저자
            'label': 1               # 저자는 label 1
        }
        books.append(author_info)

        # 출판사 정보 추가
        publisher_info = {
            'text': item['publisher'],  # 출판사
            'label': 2                  # 출판사는 label 2
        }
        books.append(publisher_info)

    # 결과 출력
    with open('books_info.json', 'a', encoding='utf-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=4)

    print("책 정보를 books_info.json 파일에 저장했습니다.")
else:
    print(f"API 요청 실패: {response.status_code}")
