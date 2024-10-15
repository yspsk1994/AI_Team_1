설치 및 실행 방법
환경 설정
Python 3.8 이상이 필요합니다.
requirements.txt 파일의 라이브러리를 설치합니다:
bash
pip install -r requirements.txt

모델 다운로드
YOLO 및 PaddleOCR 모델 파일을 model/ 디렉토리에 다운로드하고 배치합니다.
엑셀 파일 준비
data/total_book_list.xlsx 파일에 도서 목록을 준비합니다. 이 파일은 '제목', '저자', '출판사' 열이 포함되어야 합니다.
프로그램 실행
main.py 파일을 실행하여 프로그램을 시작합니다:
bash
python main.py

결과 확인
프로그램은 cropped_images/ 폴더에 크롭된 이미지를 저장하고, data/current_book_list.xlsx에 매칭된 도서 정보를 저장합니다.
사용법
프로그램은 기본적으로 5초 간격으로 웹캠에서 이미지를 캡처하고 처리합니다.
'q' 키를 눌러 프로그램을 종료할 수 있습니다.
주의사항
웹캠이 제대로 연결되어 있어야 하며, 해상도는 1920x1080으로 설정됩니다.
엑셀 파일 경로와 모델 경로가 정확한지 확인해야 합니다.