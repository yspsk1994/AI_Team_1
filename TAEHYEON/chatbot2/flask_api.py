import sys
import openai
import pymysql
import xlwt
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Flask 애플리케이션 초기화
app = Flask(__name__)

# MySQL 데이터베이스에 연결하는 함수
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="10.10.16.157",
            database="smartlibrary",
            user="pushingman",
            password="p###hoHO1357",
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def make_db():
    conn = connect_to_db()
    cursor = conn.cursor()
    sql = "SELECT * FROM bookcase1"
    cursor.execute(sql)
    results = cursor.fetchall()

    # 워크북 및 시트 생성
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("bookcase1")

    # 첫 번째 행에 컬럼명 추가
    columns = [desc[0] for desc in cursor.description]
    for col_num, column_title in enumerate(columns):
        sheet.write(0, col_num, column_title)

    # 데이터 행 추가
    for row_num, row in enumerate(results, start=1):
        for col_num, value in enumerate(row):
            sheet.write(row_num, col_num, value)

    workbook.save("make_db_list.xls")
    cursor.close()
    conn.close()

def sending_suggestion(input_data):
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT MAX(번호) FROM suggestions"
    cursor.execute(query)
    max_number = cursor.fetchone()[0]

    next_number = (max_number + 1) if max_number else 1
    date_str = datetime.now().strftime("%Y%m%d")
    query = "INSERT INTO suggestions (번호, 내용, 날짜) VALUES (%s, %s, %s)"
    cursor.execute(query, (next_number, input_data, date_str))
    conn.commit()
    cursor.close()
    conn.close()

def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=500,
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"].strip()

def load_books_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

def search_book(keyword, books):
    def safe_lower(value):
        return value.lower() if isinstance(value, str) else ""

    return [
        book
        for book in books
        if (
            keyword.lower() in safe_lower(book.get("제목")) or
            keyword.lower() in safe_lower(book.get("저자")) or
            keyword.lower() in safe_lower(book.get("출판사")) or
            keyword.lower() in safe_lower(book.get("출판일")) or
            keyword.lower() in safe_lower(book.get("청구기호"))
        )
    ]

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input")
    selected_function = request.form.get("function")

    # 책 정보 로드
    file_path = "/home/jeong-tae-hyeon/다운로드/total_book_list.xlsx"
    books = load_books_from_excel(file_path)

    if selected_function == "도서관 챗봇":
        response = search_or_ask_openai(user_input, books)
    else:
        suggestion = user_input.strip()
        #date_str = datetime.now().strftime("%Y-%m-%d \t")
        full_suggestion = f"{suggestion}"
        sending_suggestion(full_suggestion)
        response = "건의사항이 전송되었습니다."

    return jsonify(response=response)

def search_or_ask_openai(user_input, books):
    guide_prompt = """
    도서(책)에 관한 정보의 질문(제목, 저자, 출판사, 출판일, 청구기호, 도서상태)들은 대답하게 해줘 
    일반적인 질문들은 대화를 좀 더 친근하고 유머러스하게 만들어, 마치 친구와 대화하는 것처럼 자연스럽고 즐겁게 구성해줘
    """
    matched_books = search_book(user_input, books)

    if matched_books:
        unique_books = {book["제목"]: book for book in matched_books}.values()
        formatted_results = "\n".join(
            [
                f"제목: {book['제목']}, 저자: {book['저자']}, 출판사: {book['출판사']}, 출판일: {book['출판일']}, 청구기호: {book['청구기호']}, 도서상태: {book['도서상태']}"
                for book in unique_books
            ]
        )
        book_prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 정보입니다:\n{formatted_results}\n관련된 책들을 소개해줘."
        messages = [{"role": "system", "content": guide_prompt}, {"role": "user", "content": book_prompt}]
        response = ask_openai(messages)
        return response
    else:
        prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 관련된 정보를 알려주세요."
        messages = [{"role": "user", "content": prompt}]
        response = ask_openai(messages)
        return response

if __name__ == "__main__":
    make_db()
    app.run(host="0.0.0.0", port=5000)  # 서버 실행
