import threading
import queue
import cv2
# import shared
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
import pymysql
import xlwt
from collections import defaultdict

class DB_Function:
    # DB 연결하기 함수
    def connect_to_db(self):
        try:
            connection = mysql.connector.connect(
                host='10.10.16.157',       # MySQL 서버 주소
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

    # XLS(X) 파일을 DB에 삽입하는 함수
    def insert_data_from_xls(self, file_path, table_name):
        # XLS 파일 읽기
        df = pd.read_excel(file_path)

        # MySQL 데이터베이스 연결
        connection = self.connect_to_db()
        if connection is None:
            return

        cursor = connection.cursor()

        # 데이터프레임의 각 행을 데이터베이스에 삽입
        for index, row in df.iterrows():
            # 테이블 컬럼에 맞게 쿼리 작성
            sql = f"""
                INSERT INTO {table_name} (title, writer, bookcaseSubject, series, seriesNo, publishingDate, price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
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

    # TXT 파일을 DB에 삽입하는 함수
    def insert_data_from_txt(self, file_path):
        # MySQL 데이터베이스 연결
        connection = self.connect_to_db()
        if connection is None:
            return

        cursor = connection.cursor()

        # TXT 파일 열기 및 데이터 삽입
        with open(file_path, 'r') as file:
            for line in file:
                data = line.strip().split(',')  # 콤마로 구분
                query = """
                    INSERT INTO bookcase1 (title, writer, publisher, turn, bookcaseSubject) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, data)

        # 변경 사항 커밋 및 연결 종료
        connection.commit()
        cursor.close()
        connection.close()

    # DB 데이터를 XLS 파일로 추출하는 함수
    def db_data_to_xls_file(self):
        connection = self.connect_to_db()
        if connection is None:
            return

        cursor = connection.cursor()
        sql = "SELECT * FROM bookcase1"
        cursor.execute(sql)
        results = cursor.fetchall()

        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("bookcase1")

        # 컬럼명 삽입
        columns = [desc[0] for desc in cursor.description]
        for col_num, column_title in enumerate(columns):
            sheet.write(0, col_num, column_title)

        # 데이터 삽입
        for row_num, row in enumerate(results, start=1):
            for col_num, value in enumerate(row):
                sheet.write(row_num, col_num, value)

        workbook.save("bk1_data241016.xls")
        cursor.close()
        connection.close()

        print("데이터가 bk1_data241016.xls 파일로 저장되었습니다.")

    # XLS 파일을 이용해 도서 상태를 DB에 업데이트하는 함수
    def bookStatus2db_xls(self, file_path):
        # XLS 파일 읽기
        df = pd.read_excel(file_path)

        # MySQL 데이터베이스 연결
        connection = self.connect_to_db()
        if connection is None:
            return

        cursor = connection.cursor()

        # 데이터프레임의 각 행을 데이터베이스에 업데이트
        for index, row in df.iterrows():
            sql = """
                INSERT bookcase1 
                SET 
                    제목 = %s,
                    저자 = %s,
                    출판사 = %s,
                    ISBN = %s,
                    출판일 = %s,
                    청구기호 = %s,
                    도서상태 = %s,
                    주제 = %s,
                    책장 = %s
            """
            values = (
                row['제목'],
                row['저자'],
                row['출판사'],
                row['ISBN'],
                row['출판일'],
                row['청구기호'],
                row['도서상태'],
                row['주제'],
                row['책장'],
            )

            try:
                cursor.execute(sql, values)
                connection.commit()
                print("신간 도서 등록 완료!")
            except Error as e:
                print(f"Error: '{e}' on row {index}")

        # 변경 사항 커밋
        connection.commit()
        print("데이터가 성공적으로 업데이트 되었습니다.")

        # 연결 종료
        cursor.close()
        connection.close()
        
        
        
    def show_suggestions_list(self):

        # MySQL 연결 정보
        db = pymysql.connect(
            host="10.10.16.157",  # MySQL 서버 주소
            user="pushingman",  # MySQL 사용자 이름
            password="p###hoHO1357",  # MySQL 비밀번호
            database="smartlibrary"  # 사용할 데이터베이스 이름
        )

        # 커서 생성
        cursor = db.cursor()

        # 데이터를 추출할 SQL 쿼리
        sql = "SELECT * FROM suggestions"

        # SQL 쿼리 실행
        cursor.execute(sql)

        # 쿼리 결과를 가져옴
        results = cursor.fetchall()

        # 컬럼명 가져오기
        columns = [desc[0] for desc in cursor.description]  
            
        for row_num, row in enumerate(results, start=1):
            (f"{row[1]}")

        # MySQL 연결 종료
        cursor.close()
        db.close()
        
        return results
    
    def suggestions_by_date(self):
        # MySQL 연결 정보
        db = pymysql.connect(
            host="10.10.16.157",
            user="pushingman",
            password="p###hoHO1357",
            database="smartlibrary"
        )

        # 커서 생성
        cursor = db.cursor()

        # 데이터를 추출할 SQL 쿼리
        sql = "SELECT * FROM suggestions"
        cursor.execute(sql)
        results = cursor.fetchall()

        # 컬럼명 가져오기
        columns = [desc[0] for desc in cursor.description]

        # 날짜별 건의사항 개수를 저장할 딕셔너리
        suggestion_count = defaultdict(int)

        # 건의사항 데이터를 날짜별로 집계
        for row in results:
            # 날짜 열의 인덱스 (예: 세 번째 열이 날짜라면 인덱스는 2)
            date = row[2]  # row[2]가 날짜 정보라고 가정
            suggestion_count[date] += 1

        # MySQL 연결 종료
        cursor.close()
        db.close()

        # 결과를 튜플 형태로 변환하여 반환
        # 예: [('2024-10-22', 3), ('2024-10-21', 5)]
        suggestion = [(date, count) for date, count in suggestion_count.items()]
        return suggestion