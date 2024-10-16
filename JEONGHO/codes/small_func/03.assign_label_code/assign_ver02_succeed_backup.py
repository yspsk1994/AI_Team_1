import pandas as pd
import mysql.connector
from mysql.connector import Error

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


def assign_a_new_book(pick_data):
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
    return index, label

#카메라로 책 인식
print("카메라 인식...")

#책의 데이터 추출
print("책에서 데이터 추출...")

#추출 값과 신간 도서 리스트 유사성 검색
print("추출 데이터 / 신간 도서 리스트 유사성 판단...")

#신간 도서에서 데이터 픽!

    #신간 도서 목록 열기
candi_file_path = '/home/liam/workspace/virtual/10_project/codes/each_func/01.switch_data/test(local)label_test_bk1.xls'
candi_list = pd.read_excel(candi_file_path)
#print(candi_list)
x = 0
for index, row in candi_list.iterrows():
    index, rrr = assign_a_new_book(row) #청구기호 부여
    candi_list.at[index, 'labelNum'] = rrr
candi_list.to_excel('updated_file.xlsx', index=False, engine='openpyxl')

    

#픽 한 데이터 DB에 저장!

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
def insert_data_from_xls(file_path):
    # XLS 파일 읽기
    df = pd.read_excel(file_path)

    # MySQL 데이터베이스 연결
    connection = connect_to_db()
    if connection is None:
        return

    cursor = connection.cursor()
    
    #해당 테이블 행 전체 삭제
    sql = f"TRUNCATE TABLE bookcase1"
    try:
        cursor.execute(sql)
    except Error as e:
        print(f"Error: '{e}'")

    # 데이터프레임의 각 행을 데이터베이스에 삽입
    for index, row in df.iterrows():
        # 테이블 컬럼에 맞게 쿼리 작성 (예시)
        sql = f"INSERT INTO bookcase1 (title, writer, publisher, turn, bookcaseSubject, labelNum) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (row['title'], row['writer'], row['publisher'], row['turn'], row['bookcaseSubject'], row['labelNum'])
        
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
file_path = '/home/liam/workspace/virtual/10_project/codes/each_func/03.assign_label_code/updated_file.xlsx'
insert_data_from_xls(file_path)

