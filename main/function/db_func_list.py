1. DB 연결하기 함수
import pandas as pd
import mysql.connector
from mysql.connector import Error

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

2. xls(x)파일 -> DB 삽입 함수
import pandas as pd
import mysql.connector
from mysql.connector import Error

def insert_data_from_xls(file_path, table_name):
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
        sql = f"INSERT INTO bookcase2 (title, writer, bookcaseSubject, series, seriesNo, publishingDate, price) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (row['제목'], row['작가'], row['분류'], row['시리즈'], row['시리즈번호'], row['출간일'], row['가격'])
        
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


3. txt파일 -> DB 삽입 함수
import mysql.connector

def insert_data_from_txt(file_path):
    # MySQL에 연결
    conn = connect_to_db()
    cursor = conn.cursor()

    # txt 파일 열기
    with open(file_path, 'r') as file:
        for line in file:
            # txt 파일에서 데이터를 분리
            data = line.strip().split(',')  # 콤마(,)로 데이터 구분 시 사용
            # 데이터 삽입 쿼리 작성
            query = "INSERT INTO bookcase1 (title, writer, publisher, turn, bookcaseSubject) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, data)

    # 변경 사항 커밋 및 연결 종료
    conn.commit()
    cursor.close()
    conn.close()


4. DB데이터 -> xls(x)파일 추출 함수
import pymysql
import xlwt

# 커서 생성
cursor = db.cursor()

# 데이터를 추출할 SQL 쿼리
sql = "SELECT * FROM bookcase1"

# SQL 쿼리 실행
cursor.execute(sql)

# 쿼리 결과를 가져옴
results = cursor.fetchall()

# 워크북 및 시트 생성
workbook = xlwt.Workbook()
sheet = workbook.add_sheet("bookcase1")

# 첫 번째 행에 컬럼명 추가
columns = [desc[0] for desc in cursor.description]  # 컬럼명 가져오기
for col_num, column_title in enumerate(columns):
    sheet.write(0, col_num, column_title)

# 데이터 행 추가
for row_num, row in enumerate(results, start=1):
    for col_num, value in enumerate(row):
        sheet.write(row_num, col_num, value)

# 결과를 엑셀 파일로 저장
workbook.save("bk1_data241016.xls")

# MySQL 연결 종료
cursor.close()
db.close()

print("데이터가 bk1_data241016.xls 파일로 저장되었습니다.")


5. 도서상태(XLS파일) -> DB 삽입 함수
import pandas as pd
import mysql.connector
from mysql.connector import Error

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
    print("데이터가 성공적으로 업데이트 되었습니다.")

    # 연결 종료
    cursor.close()
    connection.close()
