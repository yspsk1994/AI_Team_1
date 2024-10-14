import threading
import time
import mysql.connector
import cv2
import pandas as pd


def xls2list_arr():
    # 파일 읽어옴
    file_path = '8.similr.xls'
    df = pd.read_excel(file_path)
    
    # 상위 5개의 행을 가져와 tmp_book_data에 저장
    arr = df.head(5)
    
    # DataFrame을 튜플 리스트로 변환
    tuple_list = [tuple(row) for row in arr.itertuples(index=False, name=None)]
    
    return tuple_list

# MySQL 데이터베이스 연결 설정
db_config = {
    'user': 'pushingman',
    'password': 'p###hoHO1357',
    'host': 'localhost',
    'database': 'smartlibrary'
}

# 신간 도서 등록 기능 (OCR 사용)
def add_new_books():
    
    # 신간 도서(타겟) 탐지
    print("책장별 카메라 프레임 얻어오기...")
    print("신간 도서(타겟) 탐지...")
    
    # 신간 도서(타겟) 이미지 추출
    print("신간 도서(타겟) 이미지 추출...")
    
    # 탐지한 책 이미지 -> OCR 전달
    print("신간 도서(타겟)이미지 OCR 전달...")
    
    # OCR을 사용하여 책 정보 스캔 및 추출
    print("신간 도서 등록을 위한 OCR 스캔 중...")
    
    # 추출한 정보 저장
    tmp_book_data = xls2list_arr()
    print(tmp_book_data)
    
    
    
    # MySQL DB에 등록
    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()

    add_book_query = "INSERT INTO bookcase1 (title, writer, publisher, turn, bookcaseSubject) VALUES (%s, %s, %s, %s, %s)"
    
    # 튜플 리스트를 사용하여 데이터베이스에 삽입
    cursor.execute(add_book_query, tmp_book_data)
    
    db_connection.commit()
    print("신간 도서가 데이터베이스에 등록되었습니다.")

    cursor.close()
    db_connection.close()
    
    

# 프로그램 실행
if __name__ == "__main__":
    add_new_books()
