import pandas as pd
import mysql.connector
from mysql.connector import Error

# MySQL 데이터베이스에 연결
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',       # MySQL 서버 주소
            database='smartlibrary', # 사용할 데이터베이스 이름
            user='pushingman',     # MySQL 사용자 이름
            password='p###hoHO1357'  # MySQL 비밀번호
        )
        if connection.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None
    

# XLS 파일 데이터를 MySQL에 삽입
def bookStatus2db_xls(file_path):
    # XLS 파일 읽기
    df = pd.read_excel(file_path)

    # MySQL 데이터베이스 연결
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()

    # 데이터프레임의 각 행을 데이터베이스에 삽입
    for index, row in df.iterrows():
        # 테이블 컬럼에 맞게 쿼리 작성 (예시)
        sql = f"UPDATE bookcase1 SET bookStatus = %s WHERE title = %s"
        values = (row['도서상태'], row['제목'])
        
        try:
            cursor.execute(sql, values)
        except Error as e:
            print(f"Error: '{e}'")

    # 변경 사항 커밋
    connection.commit()
    print("데이터가 성공적으로 삽입되었습니다.")

    # 연결 종료
    cursor.close()
    connection.close()

# 파일 경로와 테이블 이름 입력
file_path = '/home/liam/workspace/virtual/10_project/codes/each_func/test_bk_status.xlsx'
bookStatus2db_xls(file_path)
