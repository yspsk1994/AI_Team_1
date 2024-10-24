import mysql.connector
from mysql.connector import Error
import tkinter as tk
from tkinter import ttk, messagebox
import os
import torch
from transformers import pipeline
from huggingface_hub import login


# GPU가 사용 가능한지 확인
device = 0 if torch.cuda.is_available() else -1

# Hugging Face에 로그인
login(api_key)

# 의도 분류기 로드
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=device)

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

# MySQL에서 label_name 가져오기
def get_labels_from_db(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT label_name FROM etc")  # etc 테이블에서 label_name 가져오기
        labels = [row[0] for row in cursor.fetchall()]
        return labels
    except Error as e:
        messagebox.showerror("Database Error", f"Error: '{e}'")
        return []
    finally:
        cursor.close()

# MySQL에서 가장 높은 라벨에 대한 응답 가져오기
def get_response_for_label(connection, label):
    try:
        cursor = connection.cursor(buffered=True)
        query = "SELECT answer FROM etc WHERE label_name = %s"
        cursor.execute(query, (label,))
        response = cursor.fetchone()
        return response[0] if response else "응답을 찾을 수 없습니다."
    except Error as e:
        messagebox.showerror("Database Error", f"Error: '{e}'")
        return "데이터베이스 오류"
    finally:
        cursor.close()

# 검색어 입력 후 분석
def on_search(event=None):
    search_text = search_entry.get()
    if not search_text:
        messagebox.showwarning("Input Error", "검색어를 입력해주세요.")
        return
    
    # MySQL 데이터베이스 연결
    connection = connect_to_db()
    if connection is None:
        return
    
    # 데이터베이스에서 label 가져오기
    labels = get_labels_from_db(connection)
    if not labels:
        return
    
    # 입력 텍스트에 대한 의도 분류
    result = classifier(search_text, labels)
    
    #print("점수: ",result) #디버깅
    
    best_label = result['labels'][0]  # 가장 높은 확률의 라벨 가져오기
    score = result['scores'][0]
    
    # 신뢰도 기준 설정
    if score > 0.0401:
        # 가장 높은 라벨에 해당하는 응답 가져오기
        response = get_response_for_label(connection, best_label)
    else:
        response = "죄송합니다, 이해하지 못했습니다."
        
    # 가장 높은 라벨에 해당하는 응답 가져오기
    response = get_response_for_label(connection, best_label)
    
    # 결과 출력
    display_result(response)

    #검색어 입력 필드 비우기
    search_entry.delete(0, tk.END)
    
# 결과 창에 출력
def display_result(result):
    result_box.config(state=tk.NORMAL)
    result_box.delete(1.0, tk.END)
    result_box.insert(tk.END, f"챗봇:{result}")
    result_box.config(state=tk.DISABLED)

# GUI 초기 설정
root = tk.Tk()
root.title("Chat Bot")
root.geometry("780x600")
root.resizable(width=False, height=False)
root["bg"] = "#99f5dd"

# 검색어 입력 필드
ttk.Label(root, text="검색어를 입력하세요:").pack(pady=10)
search_entry = ttk.Entry(root, width=70)
search_entry.pack()
# 검색어 입력 상자 포커스
search_entry.focus()
# Enter 키로 검색 실행
search_entry.bind('<Return>', on_search)

# 검색 버튼
search_button = ttk.Button(root, text="검색", command=on_search)
search_button.pack(pady=20)

# 검색 결과 표시
ttk.Label(root, text="챗봇이랑 같이 놀아요!~~", font=("굴림체", 14)).pack(pady=10)
result_box = tk.Text(root, height=15, width=90, state=tk.DISABLED)
result_box.pack()

# GUI 실행
root.mainloop()
