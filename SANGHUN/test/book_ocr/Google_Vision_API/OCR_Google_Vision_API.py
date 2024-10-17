import os
import io
import requests
from google.cloud import vision
import re
import xmltodict

# Google Vision API를 통해 이미지에서 텍스트 추출
def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description.strip()
    else:
        return None

# 알라딘 도서 검색 API를 통해 책 정보 검색
def search_book_on_aladin(query, ttb_key):
    url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
    params = {
        "TTBKey": ttb_key,
        "Query": query,
        "QueryType": "Keyword",
        "MaxResults": 10,
        "start": 1,
        "SearchTarget": "Book",
        "output": "xml",
        "Version": "20131101"
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        result = xmltodict.parse(response.content)
        items = result['object'].get('item', [])
        if isinstance(items, dict):
            items = [items]
        return items if items else None
    else:
        print(f"Error: {response.status_code}")
        return None

# 책 정보를 알라딘 도서 검색 API에서 검색
def main(image_path, ttb_key):
    extracted_text = extract_text_from_image(image_path)
    if extracted_text:
        extracted_text = re.sub(r'[^-!~\w\s]', '\n', extracted_text)
        print(f"추출된 텍스트: {extracted_text}")   
    
        lines = extracted_text.splitlines()
        best_book = None
        best_score = 0
        
        for line in lines:
            if not line:
                continue
            print(f"검색 중: {line}")
            book_info = search_book_on_aladin(line.strip(), ttb_key)
            
            if book_info:
                for book in book_info:
                    score = calculate_relevance_score(book.get('title', ''), line)
                    if score > best_score:
                        best_score = score
                        best_book = book
        
        if best_book:
            print("\n가장 일치하는 도서 정보:")
            print(f"제목: {best_book.get('title', '정보 없음')}")
            print(f"저자: {best_book.get('author', '정보 없음')}")
            print(f"출판사: {best_book.get('publisher', '정보 없음')}")
            print(f"출판일: {best_book.get('pubDate', '정보 없음')}")
            print(f"링크: {best_book.get('link', '정보 없음')}")
        else:
            print("알라딘 API에서 적합한 도서를 찾지 못했습니다.")
    else:
        print("이미지에서 텍스트를 감지하지 못했습니다.")

def calculate_relevance_score(book_title, search_term):
    if search_term.lower() in book_title.lower():
        return len(search_term)
    return 0
        
# 실행 부분
if __name__ == "__main__":
    IMAGE_PATH = 'book_path'
    TTB_KEY = "ttbradon992330001"  # 알라딘 TTB 키 입력
    main(IMAGE_PATH, TTB_KEY)
