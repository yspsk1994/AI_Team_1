import openai
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import scrolledtext, simpledialog, messagebox

# OpenAI API 호출 함수
def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()

# MySQL 데이터베이스에 연결하는 함수
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='10.10.16.157', 
            database='smartlibrary',
            user='pushingman',
            password='p###hoHO1357'
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
        cursor.execute(query, ('%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    return []

# 사용자 입력 처리 함수
def handle_user_input(user_input, chat_history):
    if any(greet in user_input for greet in ["안녕하세요", "안녕", "hi", "반가워", "반가워요"]):
        response = "안녕하세요! 스마트 도서관에 오신 것을 환영합니다. 도서 검색, 도서관 안내 등 다양한 서비스를 제공해드리고 있습니다. 무엇을 도와드릴까요?"
        chat_history.append({"role": "assistant", "content": response})
        return response

    matched_books = []
    words = user_input.split()

    for word in words:
        search_results = search_book(word)
        matched_books.extend(search_results)

    if matched_books:
        unique_books = {book['title']: book for book in matched_books}.values()
        formatted_results = "\n".join([f"제목: {book['title']}, 저자: {book['writer']}, 장르: {book['bookcaseSubject']}, 출판일: {book['publishingDate']}" 
                                        for book in unique_books])
        prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 책 정보입니다:\n{formatted_results}\n관련된 책을 소개해줄게요."
        messages = chat_history + [{"role": "user", "content": prompt}]
        response = ask_openai(messages)
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        return response
    else:
        prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 관련된 정보를 알려주세요."
        messages = chat_history + [{"role": "user", "content": prompt}]
        response = ask_openai(messages)
        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "assistant", "content": response})
        return response

############################################3
# 건의사항 제출 처리 함수
def handle_suggestion_submission(suggestion_entry, popup):
    suggestion = suggestion_entry.get("1.0", tk.END).strip()  # 사용자 입력 가져오기
    if suggestion:  # 건의사항이 비어있지 않은 경우
        #save_suggestion(suggestion)  # 건의사항 저장 함수 호출
        with open("suggestions.txt", "a", encoding="utf-8") as file:
            file.write(suggestion + "\n")
        suggestion_entry.delete("1.0", tk.END)  # 입력 필드 내용 지우기
        messagebox.showinfo("저장 완료", "건의사항이 저장되었습니다.")
        #popup.destroy()  # 팝업 창 닫기
    else:
        messagebox.showwarning("경고", "건의사항을 입력해주세요.")  # 비어있을 경우 경고 메시지 표시

# 건의사항 입력을 위한 팝업 창
def open_suggestion_popup():
    popup = tk.Toplevel(window)
    popup.title("건의사항")
    popup.geometry("400x300")
    
    label = tk.Label(popup, text="건의사항을 입력하세요:")
    label.pack(pady=10)

    suggestion_entry = tk.Text(popup, height=10)
    suggestion_entry.pack(padx=10)
    
    # 버튼을 포함할 프레임 생성
    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)
    
    submit_button = tk.Button(button_frame, text="제출", 
                              command=lambda: handle_suggestion_submission(suggestion_entry, popup))
    submit_button.pack(side=tk.LEFT, padx=(0, 20))  # 오른쪽에 패딩 추가

    cancel_button = tk.Button(button_frame, text="취소", command=popup.destroy)
    cancel_button.pack(side=tk.LEFT, padx=(20, 0))  # 왼쪽에 패딩 추가
########################################################3

# GUI 창 생성 및 메인 루프
def send_message(event=None):
    user_input = entry.get()
    if user_input.lower() in ["종료", "exit"]:
        chatbox.insert(tk.END, "챗봇: 감사합니다! 다음에 또 뵙겠습니다.\n")
        window.quit()
    else:
        chatbox.insert(tk.END, f"사용자: {user_input}\n")
        response = handle_user_input(user_input, chat_history)
        chatbox.insert(tk.END, f"챗봇: {response}\n")
        entry.delete(0, tk.END)

# GUI 구성
window = tk.Tk()
window.title("스마트 도서관 챗봇")
window.geometry("600x800")

chat_history = []  # 대화 기록 저장

# 스크롤 가능한 텍스트 상자
chatbox = scrolledtext.ScrolledText(window, wrap=tk.WORD, width=70, height=35)
chatbox.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

# 입력 필드
entry = tk.Entry(window, width=65)
entry.grid(row=1, column=0, padx=10, pady=10)
entry.focus()

# 엔터 키를 누르면 send_message 호출
entry.bind("<Return>", send_message)

# 건의사항 버튼
suggest_button = tk.Button(window, text="건의", command=open_suggestion_popup)
suggest_button.grid(row=0, column=2, padx=10, pady=10)

# 전송 버튼
send_button = tk.Button(window, text="전송", command=send_message)
send_button.grid(row=1, column=2, padx=10, pady=10)

window.mainloop()
