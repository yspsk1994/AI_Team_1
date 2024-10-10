import os
import torch
import pandas as pd
from transformers import pipeline
from huggingface_hub import login
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 환경 변수에서 API 키 가져오기
os.environ["HF_API_KEY"] = "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"
api_key = os.getenv("HF_API_KEY")

# Hugging Face에 로그인
login(api_key)

# GPU가 사용 가능한지 확인
device = 0 if torch.cuda.is_available() else -1

# 1. 책 데이터 불러오기
file_path = 'vast_book.xlsx'  # 실제 데이터 파일 경로를 지정하세요.
df = pd.read_excel(file_path, engine='openpyxl')

# 2. 데이터 구조 확인 및 딕셔너리 형태로 저장
book_info = {}
for index, row in df.iterrows():
    title = row['제목']  # 데이터프레임 열 이름에 맞게 변경하세요.
    author = row['작가']
    date = row['출간일']
    price = row['가격']
    book_info[title] = {
        'author': author,
        'price': price,
        'date': date
    }

# 3. 후보 레이블 읽기
candidate_labels = []
with open('labels.txt', 'r', encoding='utf-8') as file:
    candidate_labels = [line.strip() for line in file]

# 4. 일반 질문 응답 파일 읽기
responses = {}
with open('responses.txt', 'r', encoding='utf-8') as file:
    for line in file:
        label, response = line.strip().split(": ")
        responses[label] = response

# 5. 책 제목 목록 추출 및 TF-IDF 벡터 생성
titles = list(book_info.keys())
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(titles)

# 6. Zero-shot classification 의도 분류기 로드
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

# 7. 책 정보 찾기 함수 정의
def get_book_info(user_input):
    # 사용자 입력과 책 제목 간의 유사도 계산
    input_tfidf = vectorizer.transform([user_input])
    cosine_similarities = cosine_similarity(input_tfidf, tfidf_matrix).flatten()

    # 가장 유사한 책 제목 찾기
    top_index = cosine_similarities.argmax()
    top_title = titles[top_index]
    top_score = cosine_similarities[top_index]

    # 신뢰도가 높은 경우 책 정보 반환
    if top_score > 0.1:
        book_details = book_info[top_title]
        response = (
            f"책 제목: {top_title}\n"
            f"저자: {book_details['author']}\n"
            f"출간일: {book_details['date']}\n"
            f"가격: {book_details['price']}"
        )
        return response
    else:
        return None

# 8. 일반 질문 응답 찾기 함수 정의
def get_general_response(user_input):
    # Zero-shot classification을 사용하여 의도 분류
    result = classifier(user_input, candidate_labels)
    
    # 가장 높은 점수를 받은 레이블 추출
    top_label = result['labels'][0]
    score = result['scores'][0]

    # 신뢰도 기준에 따라 응답 생성
    if score > 0.04:
        return responses.get(top_label, "죄송합니다, 해당 질문에 대한 답변을 찾을 수 없습니다.")
    else:
        return "죄송합니다, 이해하지 못했습니다."

# 9. 챗봇 실행
if __name__ == "__main__":
    while True:
        user_input = input("문장을 입력하세요 (종료하려면 '종료' 입력): ")
        if user_input.lower() == "종료":
            print("챗봇을 종료합니다.")
            break

        # 10. 책 정보 찾기 시도
        book_response = get_book_info(user_input)
        
        if book_response:
            # 책 정보가 있을 경우 출력
            print(f"책 정보 응답:\n{book_response}")
        else:
            # 책 정보가 없을 경우 일반 질문 응답 시도
            general_response = get_general_response(user_input)
            print(f"일반 질문 응답:\n{general_response}")
