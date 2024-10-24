import tkinter as tk
import openai
import mysql.connector
from mysql.connector import Error

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

# MySQL에서 책 정보를 검색하는 함수
def search_book_info(query):
    connection = connect_to_db()
    if connection is None:
        return "데이터베이스 연결에 실패했습니다."

    try:
        cursor = connection.cursor()
        # 간단한 책 제목 또는 저자 검색 쿼리 예시 (사용자 입력을 바탕으로)
        search_query = f"SELECT title, writer, bookcaseSubject, publishingDate FROM bookcase2 WHERE title LIKE '%{query}%' OR writer LIKE '%{query}%'"
        cursor.execute(search_query)
        result = cursor.fetchall()

        if not result:
            return "검색 결과가 없습니다."
        
        # 검색 결과를 문자열로 변환
        response = ""
        for row in result:
            title, writer, bookcaseSubject, publishingDate = row
            response += f"제목: {title}, 저자: {writer}, 장르: {bookcaseSubject}, 출간일: {publishingDate}\n"
        return response
    except Error as e:
        return f"Error: '{e}'"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# GPT-4를 사용하여 응답 생성 함수
def generate_response(user_input):
    # MySQL 데이터베이스에서 책 정보 검색 여부 판단
    if '책 제목' in user_input or '도서' in user_input:
        return search_book_info(user_input)
    
    # 기본적으로 OpenAI API를 사용하여 질문에 답변
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "넌 도서관 사서을 도움주는 챗봇이야"},
                {"role": "user", "content": user_input}
            ]
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# 사용자 입력 처리 및 응답 표시 함수
def send_message():
    user_input = entry.get()
    if user_input:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"User: {user_input}\n")
        chat_log.config(state=tk.DISABLED)
        entry.delete(0, tk.END)

        # GPT-4 응답 가져오기
        response = generate_response(user_input)

        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, f"Bot: {response}\n\n")
        chat_log.config(state=tk.DISABLED)

        # 자동 스크롤
        chat_log.yview(tk.END)

# 인사 및 소개 메시지 표시 함수
def welcome_message():
    intro_message = "안녕하세요! 저는 도서관 사서 챗봇입니다.\n" \
                    "책 정보 검색, 추천, 그리고 도서관 이용에 대한 질문을 도와드릴 수 있습니다.\n" \
                    "궁금한 점이 있으면 언제든지 질문해주세요!"
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"Bot: {intro_message}\n\n")
    chat_log.config(state=tk.DISABLED)

# GUI 초기화
root = tk.Tk()
root.title("Library Chat_Bot")
root.geometry("610x690")

# 채팅 로그 창
chat_log = tk.Text(root, height=29, width=70, state=tk.DISABLED)
chat_log.grid(row=0, column=0, padx=10, pady=10)

# 사용자 입력 필드
entry = tk.Entry(root, width=60)
entry.grid(row=1, column=0, padx=10, pady=10)
entry.focus()

# 전송 버튼
send_button = tk.Button(root, text="전송", command=send_message)
send_button.grid(row=1, column=1, padx=10, pady=10)

# Enter 키로 메시지 전송
def on_enter_key(event):
    send_message()

entry.bind("<Return>", on_enter_key)

# 초기 환영 메시지 표시
welcome_message()

# GUI 실행
root.mainloop()
