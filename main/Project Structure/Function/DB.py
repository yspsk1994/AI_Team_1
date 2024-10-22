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

# 초성 리스트. 00 ~ 18
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
# 중성 리스트. 00 ~ 20
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
# 종성 리스트. 00 ~ 27 + 1(1개 없음)
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def korean_to_be_englished(korean_word):
        r_lst = []
        for w in list(korean_word.strip()):
            ## 영어인 경우 구분해서 작성함. 
            if '가'<=w<='힣':
                ## 588개 마다 초성이 바뀜. 
                ch1 = (ord(w) - ord('가'))//588
                ## 중성은 총 28가지 종류
                ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
                ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
                r_lst.append([CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]])
            else:
                r_lst.append(w)
        return r_lst

def assign_unique_num(pick_data):

    global wrt_mid_name
    #청구기호 생성 및 부여
    # 1) xxx. &
    label = '500.'
    # 2) 작가 성씨 한글자 추출 &
    #print(pick_data[1][0])
    wrt_last_name = pick_data[1][0]
    #print(wrt_last_name)
    label += wrt_last_name
    #print(label)
    #print('작가 성씨 추출 완료')
    
    # 3) 작가 가운데 이름 한 글자를 숫자화 &
    wrt_mid_name = pick_data[1][1]
    idx = 1
    while wrt_mid_name == " " or wrt_mid_name == ".":
        idx += 1
        wrt_mid_name = pick_data[1][idx]

    tmp = korean_to_be_englished(wrt_mid_name)
    #print(tmp)
    #print('작가 가운데 이름 한글자 추출한게 위에야')
    s = ''
    for n in tmp:
        for x in range(len(n)):
            s += n[x]
            #print(n[x])
            x += 1
    #print(s)

    #label = label + s[0] +s[1]
    #print(label)
    #print('line 57')

    # 숫자화 남았음
    ch_num1 = str(CHOSUNG_LIST.index(s[0]))     #작가 이름 영어 해결 못함
    ch_num2 = str(JUNGSUNG_LIST.index(s[1]))
    label = label + ch_num1 + ch_num2
    #print(label)
    #print('line 64')
    
    # 4) 책 제목 첫글자의 초성
    first_bookname = pick_data[0][0]
    #print(first_bookname)
    tmp = korean_to_be_englished(first_bookname)
    #print(tmp)
    s =""
    x = 0
    for n in tmp:
        s += n[x]
        #print(n[x])
        x += 1

    label += s
    #print(label)
    return label

def adding_new_books():
    #카메라로 책 인식
    print("카메라 인식...")

    #책의 데이터 추출
    print("책에서 데이터 추출...")

    #추출 값과 신간 도서 리스트 유사성 검색
    print("추출 데이터 / 신간 도서 리스트 유사성 판단...")

    #신간 도서에서 데이터 픽!

        #신간 도서 목록 열기
    candi_file_path = '/home/taejoon/workspace/team_project/Project_Structure/data/bk1_label_status.xlsx'
    candi_list = pd.read_excel(candi_file_path)
    #print(candi_list)
    x = 0
    for index, row in candi_list.iterrows():
        rrr = assign_unique_num(row) #청구기호 부여
        candi_list.at[index, '청구기호'] = rrr
    candi_list.to_excel('/home/taejoon/workspace/team_project/Project_Structure/data/updated_file.xlsx', index=False, engine='openpyxl')

    #픽 한 데이터 DB에 저장!
    #파일 경로와 테이블 이름 입력
    #file_path = 'updated_file.xlsx'
    #insert_data_from_xls(file_path)


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
        df = pd.read_excel(file_path)
        connection = self.connect_to_db()
        if connection is None:
            return

        cursor = connection.cursor()
        
        for index, row in df.iterrows():
            sql = f"""
                INSERT INTO {table_name} (title, writer, bookcaseSubject, series, seriesNo, publishingDate, price) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (row['제목'], row['작가'], row['분류'], row['시리즈'], row['시리즈번호'], row['출간일'], row['가격'])

            try:
                cursor.execute(sql, values)
            except Error as e:
                print(f"Error: '{e}'")

        connection.commit()
        print("데이터가 성공적으로 삽입되었습니다.")

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