import openai
import mysql.connector
from mysql.connector import Error

# OpenAI API 호출 함수
def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 사용할 모델
        messages=messages,
        max_tokens=500, # 응답의 최대 길이를 설정
        temperature=0.7, # 응답의 창의성을 조절
    )
    return response['choices'][0]['message']['content'].strip()

# MySQL 데이터베이스에 연결하는 함수
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='10.10.16.157',       # MySQL 서버 주소
            database='smartlibrary',   # 사용할 데이터베이스 이름
            user='pushingman',         # MySQL 사용자 이름
            password='p###hoHO1357'    # MySQL 비밀번호
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None
    

# 책 제목, 저자, 장르로 정보 검색하는 함수
def search_book(keyword):
    connection = connect_to_db()
    if connection:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT title, writer, bookcaseSubject, publishingDate 
            FROM bookcase2 
            WHERE title LIKE %s OR writer LIKE %s OR bookcaseSubject LIKE %s
        """
        cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))  # 제목, 저자, 장르 부분 검색
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    return []

# 사용자 입력 및 역할 처리 함수
def handle_user_input(user_input, chat_history):
    # 인사 및 기본 안내 처리
    if any(greet in user_input for greet in ["안녕하세요", "안녕", "hi", "반가워", "반가워요"]):
        response = "안녕하세요! 스마트 도서관에 오신 것을 환영합니다. 도서 검색, 도서관 안내 등 다양한 서비스를 제공해드리고 있습니다. 무엇을 도와드릴까요?"
        chat_history.append({"role": "assistant", "content": response})
        return response

    # 도서 검색 시도
    matched_books = []
    words = user_input.split()

    # 사용자 입력의 각 단어로 도서 검색
    for word in words:
        search_results = search_book(word)
        matched_books.extend(search_results)

    if matched_books:
        # 검색된 책이 있을 경우 결과 반환
        unique_books = {book['title']: book for book in matched_books}.values()
        formatted_results = "\n".join([f"제목: {book['title']}, 저자: {book['writer']}, 장르: {book['bookcaseSubject']}, 출판일: {book['publishingDate']}" 
                                        for book in unique_books])
        prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 책 정보입니다:\n{formatted_results}\n관련된 책을 소개해줄게요."
        messages = chat_history + [{"role": "user", "content": prompt}]
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
    chat_history = []  # 대화 기록 저장
    while True:
        user_input = input("사용자: ")
        if user_input.lower() in ["종료", "exit"]:  # 종료 명령어 추가
            print("챗봇: 감사합니다! 다음에 또 뵙겠습니다.")
            break
        
        response = handle_user_input(user_input, chat_history)
        print("챗봇:", response)

if __name__ == "__main__":
    main()
