# 0) 신간 도서 구입 목록 txt파일 불러오기
# 1) 해당 책장의 카메라가 신간 도서 객체 인식
# 2) 타겟 도서 책 제목/저자명/출판사 추출
# 3) (0단계에서 시스템에 입력된 신간 도서 구입 목록과)유사성 검토
# 4) 타겟 도서의 정확한 정보 확정
# 5) 도서관 DB에 타겟 도서 데이터(책장 정보 포함) 등록
# 6) 필요하다면, 분류 관련 정보는 네이버 도서 api 활용 분류 분야(ex. 과학/인문/에세이 등 파악)

import threading
import time
import mysql.connector
import cv2
import pandas as pd
#import pytesseract
"""
# AI 모델 및 OCR 사용을 위한 기본 설정
# (YOLOv5 또는 다른 모델 불러오기)
# AI 모델 로드 부분은 실제 모델로 대체
def load_ai_model():
    print("AI 모델 로드 중...")
    time.sleep(2)
    print("AI 모델이 성공적으로 로드되었습니다.")
    return True

# 도서 오배치 알림 기능
def misplaced_books_notification():
    print("오배치 도서 탐색 중...")
    # 카메라 연결 및 영상 처리 로직
    cap = cv2.VideoCapture(0)  # 첫 번째 웹캠 사용
    while True:
        ret, frame = cap.read()
        if not ret:
            print("카메라 영상 불러오기 실패")
            break
        
        # AI 모델을 이용한 도서 오배치 감지
        # frame에 대한 AI 모델 예측 로직 추가 (가정)
        # 결과에 따라 알림
        time.sleep(1)

    cap.release()
"""

def xls2list_arr():
    #파일 읽어옴
    file_path = '8.similr.xls'
    df = pd.read_excel(file_path)
    
    #상위 6개의 행을 가져와 tmp_book_data에 저장
    arr = df.head(5)
    
    return arr
    # 6행 잘 받아왔는지 확인용
    print(tmp_book_data) 

# MySQL 데이터베이스 연결 설정
db_config = {
    'user': 'pushingman',
    'password': 'p###hoHO1357',
    'host': 'localhost',
    'database': 'smartlibrary'
}

# 신간 도서 등록 기능 (OCR 사용)
def add_new_books():
    
    #신간 도서(타겟) 탐지
    print("책장별 카메라 프레임 얻어오기...")
    print("신간 도서(타겟) 탐지...")
    
    #신간 도서(타겟) 이미지 추출
    print("신간 도서(타겟) 이미지 추출...")
    
    #탐지한 책 이미지 -> OCR 전달
    print("신간 도서(타겟)이미지 OCR 전달...")
    
    # OCR을 사용하여 책 정보 스캔 및 추출
        # image_path = "book_cover.jpg"  # 예시 이미지 경로
        # img = cv2.imread(image_path)
        # text = pytesseract.image_to_string(img)
    print("신간 도서 등록을 위한 OCR 스캔 중...")
    #추출한 정보 저장
    # 파일을 읽어옴
    #tmp_book_data = ("추출된 책 제목1", "추출된 작가1", "추출 출판사1", "99", "추출 카테고리1")
    tmp_book_data = xls2list_arr()
    print(tmp_book_data)

    
    # MySQL DB에 등록
    db_connection = mysql.connector.connect(**db_config)
    cursor = db_connection.cursor()

    for n in range(6):
        
        add_book_query = "INSERT INTO bookcase1 (title, writer, publisher, turn, bookcaseSubject) VALUES (%s, %s, %s, %s, %s)"
        #values = (row['title'], row['writer'], row['publisher'], row['turn'], row['bookcaseSubject'])
        
        cursor.execute(add_book_query, tmp_book_data)
    
    db_connection.commit()
    print("신간 도서가 데이터베이스에 등록되었습니다.")

    cursor.close()
    db_connection.close()
    
    

# 프로그램 실행
if __name__ == "__main__":
    add_new_books()



# 0) 신간 도서 구입 목록 txt파일 불러오기

# 1) 해당 책장의 카메라가 신간 도서 객체 인식

# 2) 타겟 도서 책 제목/저자명/출판사 추출

# 3) (0단계에서 시스템에 입력된 신간 도서 구입 목록과)유사성 검토

# 4) 타겟 도서의 정확한 정보 확정

# 5) 도서관 DB에 타겟 도서 데이터(책장 정보 포함) 등록

# 6) 필요하다면, 분류 관련 정보는 네이버 도서 api 활용 분류 분야(ex. 과학/인문/에세이 등 파악)