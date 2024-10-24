import openai
import mysql.connector
from mysql.connector import Error


# MySQL 데이터베이스에 연결
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='10.10.16.157',       # MySQL 서버 주소
            database='smartlibrary',   # 사용할 데이터베이스 이름
            user='pushingman',         # MySQL 사용자 이름
            password='p###hoHO1357'    # MySQL 비밀번호
        )
        if connection.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def get_book_info(connection, query):
    try:
        cursor = connection.cursor()
        # SQL 쿼리 작성 (예: 제목 또는 저자로 책 검색)
        sql = "SELECT title, writer, publishingDate FROM bookcase2 WHERE title LIKE %s OR writer LIKE %s"
        cursor.execute(sql, ('%' + query + '%', '%' + query + '%'))
        return cursor.fetchall()
    except Error as e:
        print(f"Error: '{e}'")
        return []
    finally:
        cursor.close()  

def get_response(user_input):
    # OpenAI API에 요청할 프롬프트 생성
    prompt = (
        f"사용자가 도서관에 대해 다음과 같은 질문을 했습니다: '{user_input}'. "
        "이 질문에 대해 도서관과 관련된 정보를 바탕으로 적절한 답변을 제공하세요."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 사용할 모델 선택
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def chatbot():
    connection = connect_to_db()
    if not connection:
        return  # 데이터베이스 연결 실패 시 종료

    print("반가워요! 도서관 챗봇입니다. 궁금한 사항을 물어보세요.")
    
    while True:
        user_input = input("질문: ")
        if user_input.lower() in ['exit', 'quit','종료']:
            break
        
        # 책 정보 검색
        book_info = get_book_info(connection, user_input)
        if book_info:
            for book in book_info:
                print(f"제목: {book[0]}, 저자: {book[1]}, 출간일: {book[2]}")
        else:
            # API를 통한 응답 생성
            response = get_response(user_input)
            print(f"챗봇: {response}")

    connection.close()  # 연결 닫기

# 챗봇 시작
chatbot()
