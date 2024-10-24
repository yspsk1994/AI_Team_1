import os
import torch
import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox


# GPU가 사용 가능한지 확인
# device = 0 if torch.cuda.is_available() else -1


# **********<책에 관한 정보 검색할때 제목,저자,출판사,장르따로>************

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
            return connection
    except Error as e:
        messagebox.showerror("Database Connection Error", f"Error: '{e}'")
        return None

# 책 정보 검색
def search_book(connection, search_type, search_term):
    try:
        cursor = connection.cursor(dictionary=True)
        
        # 검색 유형에 따라 쿼리 변경
        if search_type == "제목":
            query = "SELECT * FROM bookcase2 WHERE title LIKE %s"
        elif search_type == "작가":
            query = "SELECT * FROM bookcase2 WHERE writer LIKE %s"
        elif search_type == "장르":
            query = "SELECT * FROM bookcase2 WHERE bookcaseSubject LIKE %s"
        elif search_type == "출간일":
            query = "SELECT * FROM bookcase2 WHERE publishingDate LIKE %s"

        cursor.execute(query, ("%" + search_term + "%",))
        results = cursor.fetchall()

        if results:
            return results
        else:
            return None

    except Error as e:
        messagebox.showerror("Query Error", f"Error: '{e}'")
        return None

# 검색 버튼 클릭 시 실행되는 함수
def on_search():
    search_type = search_type_var.get()  # 사용자가 선택한 검색 유형 (제목, 작가, 장르, 출간일)
    search_term = search_entry.get()  # 사용자가 입력한 검색어
    
    if not search_type or not search_term:
        messagebox.showwarning("Input Error", "검색 유형과 검색어를 모두 입력하세요.")
        return
    
    connection = connect_to_db()
    if connection:
        results = search_book(connection, search_type, search_term)
        connection.close()

        # 검색 결과 처리
        if results:
            result_text = "\n".join([f"제목: {row['title']}, 작가: {row['writer']}, 장르: {row['bookcaseSubject']},출간일: {row['publishingDate']}" for row in results])
            result_box.config(state=tk.NORMAL)
            result_box.delete(1.0, tk.END)
            result_box.insert(tk.END, result_text)
            result_box.config(state=tk.DISABLED)
        else:
            messagebox.showinfo("No Results", "해당 조건에 맞는 책을 찾을 수 없습니다.")

# GUI 초기 설정
root = tk.Tk()
root.title("도서 검색 애플리케이션")
root.geometry("780x600")

# 검색 유형 선택
search_type_var = tk.StringVar()
ttk.Label(root, text="검색 유형을 선택하세요:").pack(pady=10)
search_type_combobox = ttk.Combobox(root, textvariable=search_type_var, values=["제목", "작가", "장르", "출간일"], state="readonly")
search_type_combobox.pack()

# 검색어 입력 필드
ttk.Label(root, text="검색어를 입력하세요:").pack(pady=10)
search_entry = ttk.Entry(root, width=50)
search_entry.pack()

# 검색 버튼
search_button = ttk.Button(root, text="검색", command=on_search)
search_button.pack(pady=20)

# 검색 결과 표시
ttk.Label(root, text="검색 결과:").pack(pady=10)
result_box = tk.Text(root, height=15, width=90, state=tk.DISABLED)
result_box.pack()

# GUI 실행
root.mainloop()
