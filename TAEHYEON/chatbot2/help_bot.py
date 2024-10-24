import openai
import pandas as pd

# OpenAI API 호출 함수
def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 사용할 모델
        messages=messages,
        max_tokens=500, # 응답의 최대 길이를 설정
        temperature=0.7, # 응답의 창의성을 조절
    )
    return response['choices'][0]['message']['content'].strip()

# 책 정보를 Excel 파일에서 로드하는 함수
def load_books_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient='records')  # 리스트 형태로 변환
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

# 책 제목, 저자, 장르로 정보 검색하는 함수
def search_book(keyword, books):
    # 검색 전에 각 필드가 문자열인지 확인하고, 문자열로 변환
    def safe_lower(value):
        if isinstance(value, str):
            return value.lower()
        return ''
    
    # 키워드로 책 검색
    return [book for book in books if (keyword.lower() in safe_lower(book.get('제목')) or 
                                        keyword.lower() in safe_lower(book.get('저자')) or 
                                        keyword.lower() in safe_lower(book.get('출판사')) or
                                        keyword.lower() in safe_lower(book.get('출판일')) or
                                        keyword.lower() in safe_lower(book.get('청구기호')))]

# 사용자 입력 및 역할 처리 함수
def handle_user_input(user_input, chat_history, books):
    guide_prompt = '''
    도서(책)에 관한 정보의 질문(제목,저자,출판사,출판일,청구기호,도서상태)들은 대답하되
    '''
    chat_history.append({"role": "system", "content": guide_prompt})

    # 인사 및 기본 안내 처리
    if any(greet in user_input for greet in ["안녕하세요", "안녕", "hi", "반가워", "반가워요"]):
        response = "안녕하세요! 스마트 도서관에 오신 것을 환영합니다. 도서 검색, 도서관 안내 등 다양한 서비스를 제공해드리고 있습니다. 무엇을 도와드릴까요?"
        chat_history.append({"role": "assistant", "content": response})
        return response

    # 도서 검색 시도
    matched_books = search_book(user_input, books)  # 전체 사용자 입력으로 도서 검색

    if matched_books:
        # 검색된 책이 있을 경우 결과 반환(+장르: {book['장르']})
        unique_books = {book['제목']: book for book in matched_books}.values()
        formatted_results = "\n".join([f"제목: {book['제목']}, 저자: {book['저자']}, 출판사: {book['출판사']}, 출판일: {book['출판일']}, 청구기호: {book['청구기호']}, 도서상태: {book['도서상태']}" 
                                        for book in unique_books])
        book_prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 정보입니다:\n{formatted_results}\n관련된 책들을 소개해줘."
        messages = chat_history + [{"role": "system", "content": book_prompt}]
        response = ask_openai(messages)  # OpenAI API 호출
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        return response
    else:
        # 책 검색 결과가 없을 경우 또는 일반 질문에 대해 OpenAI에 묻기
        prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 관련된 정보를 알려주세요."
        messages = chat_history + [{"role": "user", "content": prompt}]
        response = ask_openai(messages)  # OpenAI API 호출
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        return response

# 메인 함수
def main():
    # Excel 파일에서 책 정보 로드
    file_path = '/home/jeong-tae-hyeon/다운로드/total_book_list.xlsx'  # 파일 경로를 설정하세요.
    books = load_books_from_excel(file_path)
    
    if not books:
        print("책 정보를 로드할 수 없습니다.")
        return
    
    chat_history = []  # 대화 기록 저장
    while True:
        user_input = input("사용자: ")
        if user_input.lower() in ["종료", "exit"]:  # 종료 명령어 추가
            print("챗봇: 감사합니다! 다음에 또 뵙겠습니다.")
            break
        
        response = handle_user_input(user_input, chat_history, books)
        print("챗봇:", response)

if __name__ == "__main__":
    main()
