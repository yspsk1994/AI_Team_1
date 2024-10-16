import pymysql
import xlwt

# MySQL 연결 정보
db = pymysql.connect(
    host="localhost",  # MySQL 서버 주소
    user="pushingman",  # MySQL 사용자 이름
    password="p###hoHO1357",  # MySQL 비밀번호
    database="smartlibrary"  # 사용할 데이터베이스 이름
)

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
