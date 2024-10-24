import os
from transformers import pipeline
from huggingface_hub import login


# Hugging Face에 로그인
login(api_key)

# 의도 분류기 로드
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# 후보 레이블 읽기
candidate_labels = [
    "운영시간","검색방법","책 반납","날씨","공휴일","휴관일","좋아","책 대출",
    "하는 일","무선 인터넷","와이파이","타 도서관","연체","반납연기","책 예약",
    "복사","프린트","출력","자원봉사자","회원가입","주소","우편번호","바로 대출",
    "타인의 도서카드","카드를 잃어","필요한 서류","프로그램","최대 책의 수","컴퓨터 사용",
    "필기구 대여","개인 연구 공간 예약","도서관의 역사","주의사항","분실한 책에 대한 벌금",
    "대출 기록을 삭제","소장 도서가 손상","장애인을 위한 서비스","주차공간","책의 후속작"
]

# 응답 읽기
responses = {}
with open('responses.txt', 'r', encoding='utf-8') as file:
    for line in file:
        label, response = line.strip().split(": ")
        responses[label] = response

while True:
    # 사용자 입력
    user_input = input("문장을 입력하세요 (종료하려면 'exit' 입력): ")
    if user_input.lower() == "exit":
        break

    # 분류 수행
    result = classifier(user_input, candidate_labels)
    
    #print("분류 결과:", result)
    
    # 가장 높은 점수를 받은 레이블
    top_label = result['labels'][0]
    score = result['scores'][0]

    # 최종 응답
    if score > 0.105:  # 신뢰도 기준 설정
        response = responses.get(top_label, "죄송합니다, 이해하지 못했습니다.")
    else:
        response = "죄송합니다, 이해하지 못했습니다."

    print(f"응답: {response}")
