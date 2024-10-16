import mysql.connector

# MySQL 데이터베이스에 연결
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",       # MySQL 서버 주소
        user="pushingman",   # MySQL 사용자 이름
        password="p###hoHO1357",  # MySQL 사용자 비밀번호
        database="smartlibrary"   # 사용할 데이터베이스 이름
    )

# txt 파일 읽기 및 테이블에 데이터 삽입
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

# txt 파일 경로 설정
file_path = "/home/liam/workspace/virtual/10_project/storage/insert01.txt"

# 함수 호출
insert_data_from_txt(file_path)
