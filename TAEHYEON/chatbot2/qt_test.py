import sys
import openai
import pymysql
import xlwt
import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QMessageBox,
)

# MySQL 데이터베이스에 연결하는 함수
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="10.10.16.157",
            database="smartlibrary",
            user="pushingman",
            password="p###hoHO1357",
        )
        if connection.is_connected():
            return connection
    except Error as e: 
        print(f"Error: '{e}'")
        return None


def make_db():
    # 커서 생성
    conn = connect_to_db()
    cursor = conn.cursor()

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
    workbook.save("make_db_list.xls")

    # MySQL 연결 종료
    cursor.close()
    conn.close()

    # print("데이터가 make_db_list.xls 파일로 저장되었습니다.")1 2 3 4


def sending_suggestion(input_data):
    # MySQL에 연결
    conn = connect_to_db()
    cursor = conn.cursor()

    # 현재 추가될 번호 추출
    # 가장 큰 번호를 추출하는 쿼리
    query = "SELECT MAX(번호) FROM suggestions"
    cursor.execute(query)

    # 가장 큰 번호 값을 가져옴
    max_number = cursor.fetchone()[0]

    if max_number is None:
        next_number = 1  # 데이터가 없으면 번호 1부터 시작
    else:
        next_number = max_number + 1  # 가장 큰 번호에 1을 더해 다음 번호 생성
        # 현재 날짜와 시간 가져오기
        date_str = datetime.now().strftime("%Y%m%d")

    # 데이터 삽입 쿼리 작성
    query = "INSERT INTO suggestions (번호, 내용, 날짜) VALUES (%s, %s, %s)"
    cursor.execute(query, (next_number, input_data, date_str))

    # 변경 사항 커밋 및 연결 종료
    conn.commit()
    cursor.close()
    conn.close()


# OpenAI API 호출 함수
def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 사용할 모델
        messages=messages,
        max_tokens=500,  # 응답의 최대 길이를 설정
        temperature=0.7,  # 응답의 창의성을 조절
    )
    return response["choices"][0]["message"]["content"].strip()


# 책 정보를 Excel 파일에서 로드하는 함수
def load_books_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient="records")  # 리스트 형태로 변환
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []


# 책 제목, 저자, 장르로 정보 검색하는 함수
def search_book(keyword, books):
    # 검색 전에 각 필드가 문자열인지 확인하고, 문자열로 변환
    def safe_lower(value):
        if isinstance(value, str):
            return value.lower()
        return ""

    # 키워드로 책 검색
    return [
        book
        for book in books
        if (
            keyword.lower() in safe_lower(book.get("제목"))
            or keyword.lower() in safe_lower(book.get("저자"))
            or keyword.lower() in safe_lower(book.get("출판사"))
            or keyword.lower() in safe_lower(book.get("출판일"))
            or keyword.lower() in safe_lower(book.get("청구기호"))
        )
    ]


# GUI 클래스 정의
class ChatBotApp(QWidget):
    def __init__(self, books):
        super().__init__()
        self.books = books
        self.chat_history = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("도서관 챗봇")
        self.setGeometry(100, 100, 540, 560)

        # 위젯 설정
        self.chat_label = QLabel("챗봇과 함께 나누는 즐거운 대화!!!~~~~")
        self.chat_label.setStyleSheet("font-size: 14pt;")
        self.chat_display = QTextEdit()
        self.chat_display.setStyleSheet("font-size: 12pt;")
        self.chat_display.setReadOnly(True)

        self.user_input = QLineEdit()

        # 기능 선택을 위한 콤보 박스 추가
        self.function_combo = QComboBox()
        self.function_combo.addItems(["도서관 챗봇", "건의"])

        self.send_button = QPushButton("보내기")
        self.send_button.clicked.connect(self.handle_user_input)

        self.reset_button = QPushButton("리셋")
        self.reset_button.clicked.connect(self.clear_chat)

        # 엔터 키 활성화 (returnPressed 시그널을 handle_user_input 메서드에 연결)
        self.user_input.returnPressed.connect(self.handle_user_input)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.chat_label)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.function_combo)  # 콤보 박스 추가
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.reset_button)

        layout.addLayout(input_layout)
        self.setLayout(layout)

    def handle_user_input(self):
        user_input = self.user_input.text()
        if not user_input:
            return

        self.chat_display.append(f"사용자: {user_input}")

        if user_input.lower() in ["종료", "exit"]:  # 종료 명령어 추가
            self.chat_display.append("챗봇: 감사합니다! 다음에 또 뵙겠습니다.")
            return

        # 선택한 기능에 따라 분기 처리
        selected_function = self.function_combo.currentText()
        if selected_function == "도서관 챗봇":
            response = self.search_or_ask_openai(user_input)
            self.chat_display.append(f"챗봇: {response}")
        else:
            response = self.handle_suggestion(user_input)  # 건의 기능 처리

        self.chat_display.append("")
        self.user_input.clear()

    def clear_chat(self):
        self.chat_display.clear()  # 채팅 기록 지우기
        self.chat_history.clear()  # 채팅 히스토리 초기화
        self.user_input.clear()  # 사용자 입력 초기화

    def search_or_ask_openai(self, user_input):
        guide_prompt = """
        도서(책)에 관한 정보의 질문(제목,저자,출판사,출판일,청구기호,도서상태)들은 대답하게 해줘 
        일반적인 질문들은 대화를 좀 더 친근하고 유머러스하게 만들어, 마치 친구와 대화하는 것처럼 자연스럽고 즐겁게 구성해줘
        """
        self.chat_history.append({"role": "system", "content": guide_prompt})

        # 인사 및 기본 안내 처리
        if any(
            greet in user_input
            for greet in [
                "안녕하세요",
                "안녕",
                "hi",
                "반가워",
                "반가워요",
                "하이",
                "방가방가",
                "저기",
            ]
        ):
            response = "안녕하세요! 스마트 도서관에 오신 것을 환영합니다. 도서 검색, 도서관 안내 등 다양한 서비스를 제공해드리고 있습니다. 무엇을 도와드릴까요?"
            self.chat_history.append({"role": "assistant", "content": response})
            return response

        matched_books = search_book(
            user_input, self.books
        )  # 전체 사용자 입력으로 도서 검색

        if matched_books:
            # 검색된 책이 있을 경우 결과 반환
            unique_books = {book["제목"]: book for book in matched_books}.values()
            formatted_results = "\n".join(
                [
                    f"제목: {book['제목']}, 저자: {book['저자']}, 출판사: {book['출판사']}, 출판일: {book['출판일']}, 청구기호: {book['청구기호']}, 도서상태: {book['도서상태']}, 책장위치: {book['책장']}"
                    for book in unique_books
                ]
            )
            book_prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 정보입니다:\n{formatted_results}\n 관련된 책들을 소개해줘."
            messages = self.chat_history + [{"role": "system", "content": book_prompt}]
            response = ask_openai(messages)  # OpenAI API 호출
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            return response
        else:
            # 책 검색 결과가 없을 경우 또는 일반 질문에 대해 OpenAI에 묻기
            prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 관련된 정보를 알려주세요."
            messages = self.chat_history + [{"role": "user", "content": prompt}]
            response = ask_openai(messages)  # OpenAI API 호출
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            return response

    def handle_suggestion(self, *args):
        suggestion = self.user_input.text().strip()  # 사용자 입력 가져오기
        if suggestion:  # 건의 사항이 비어있지 않은 경우
            # 날짜와 건의 내용을 함께 전송
            full_suggestion = f"{suggestion}"
            sending_suggestion(full_suggestion)  # 건의사항 전송 함수 호출
            self.chat_display.clear()
            QMessageBox.information(self, "전송 완료", "건의사항이 전송되었습니다.")
        else:
            QMessageBox.warning(self, "주의", "건의사항을 입력해주세요.")


# 메인 함수
def main():
    make_db()
    # Excel 파일에서 책 정보 로드
    #file_path = (
    #    "/home/jeong-tae-hyeon/다운로드/total_book_list.xlsx"  # 파일 경로를 설정하세요.
    #)
    file_path = 'make_db_list.xls'
    books = load_books_from_excel(file_path)

    if not books:
        print("책 정보를 로드할 수 없습니다.")
        return

    # 애플리케이션 실행
    app = QApplication(sys.argv)
    chatbot_app = ChatBotApp(books)
    chatbot_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
