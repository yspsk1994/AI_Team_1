import pandas as pd
import re

def get_first_consonant(text):
    if not text or not isinstance(text, str):
        return 'X'
    
    consonants = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    first_char = text[0]
    
    if '가' <= first_char <= '힣':
        char_code = ord(first_char) - ord('가')
        consonant_index = char_code // 588
        return consonants[consonant_index]
    elif 'A' <= first_char.upper() <= 'Z':
        return first_char.upper()
    else:
        return 'X'

def get_first_char(text):
    if not text or not isinstance(text, str):
        return 'X'
    return text[0].upper()

def generate_call_number(row):
    existing_call_number = str(row['청구기호']) if pd.notna(row['청구기호']) else '000'  # 기존 청구기호
    
    # 저자 처리 (첫 글자 그대로 사용)
    author_initial = get_first_char(row['저자'])
    
    # 제목 처리 (첫 글자의 자음만 사용)
    title_initial = get_first_consonant(row['제목'])
    
    # 출판일 처리
    if pd.isna(row['출판일']):
        year = 'XXXX'
    else:
        year = str(row['출판일'])[:4]  # 연도 추출
    
    new_call_number = f"{author_initial}{title_initial} {year}"
    
    return f"{existing_call_number} {new_call_number}"

# 엑셀 파일 읽기
df = pd.read_excel('random_korean_books_naver.xlsx')

# 청구기호 업데이트
updated_call_numbers = []
for index, row in df.iterrows():
    updated_call_number = generate_call_number(row)
    updated_call_numbers.append(updated_call_number)
    
    # 업데이트된 청구기호를 포함한 진행 상황 출력
    print(f"Processing book {index + 1}/{len(df)}: {row['제목']} - 업데이트된 청구기호: {updated_call_number}")

df['청구기호'] = updated_call_numbers

# 결과를 새 엑셀 파일로 저장
df.to_excel('random_books_with_updated_number.xlsx', index=False)

print("업데이트된 청구기호가 추가된 새 엑셀 파일이 생성되었습니다.")