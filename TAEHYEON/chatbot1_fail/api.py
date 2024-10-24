import os
import torch
from transformers import pipeline
from huggingface_hub import login
import mysql.connector
from mysql.connector import Error


# Hugging Face에 로그인
login(api_key)

# GPU가 사용 가능한지 확인
device = 0 if torch.cuda.is_available() else -1

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
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

# 책 제목의 일부 또는 전체로 검색
def search_book(connection, keyword):
    try:
        cursor = connection.cursor(dictionary=True)

        # 입력한 단어가 책 제목의 일부로 포함된 책 목록 조회
        sql_query = "SELECT * FROM bookcase2 WHERE title LIKE %s"
        cursor.execute(sql_query, ("%" + keyword + "%",))
        result = cursor.fetchall()

        # 일치하는 책이 있는 경우 그 목록을 출력
        if result:
            print(f"'{keyword}' 단어가 포함된 책 목록:")
            for row in result:
                print(f"제목: {row['title']}, 저자: {row['writer']}, 장르: {row['bookcaseSubject']}, 출간일: {row['publishingDate']}")
        else:
            print(f"해당 단어 '{keyword}'가 포함된 책을 찾을 수 없습니다.")

    except Error as e:
        print(f"Error: '{e}'")

# 메인 실행 함수
if __name__ == "__main__":
    # MySQL에 연결
    connection = connect_to_db()

    if connection:
        while True:
            # 사용자로부터 책 제목 입력 받기
            title = input("검색할 책 제목 또는 단어를 입력하세요 ('exit,종료' 입력 시 종료): ")

            # 'exit' 또는 'quit' 입력 시 프로그램 종료
            if title.lower() in ['exit', '종료']:
                print("프로그램을 종료합니다.")
                break

            # 입력된 제목 또는 단어에 맞는 책 정보 검색
            search_book(connection, title)

        # MySQL 연결 종료
        connection.close()
        print("MySQL 연결이 종료되었습니다.")
