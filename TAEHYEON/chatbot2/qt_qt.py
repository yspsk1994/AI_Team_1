import sys
import openai
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox
from datetime import datetime

# OpenAI API 호출 함수
def ask_openai(messages):
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 사용할 모델
        messages=messages,
        max_tokens=500, # 응답의 최대 길이를 설정
        temperature=0.7, # 응답의 창의성을 조절
    )
    return response['choices'][0]['message']['content'].strip()

# 책 정보를 Excel 파일에서 로드하는 함수
def load_books_from_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df.to_dict(orient='records')  # 리스트 형태로 변환
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []

# 책 제목, 저자, 장르로 정보 검색하는 함수
def search_book(keyword, books):
    def safe_lower(value):
        if isinstance(value, str):
            return value.lower()
        return ''
    
    return [book for book in books if (keyword.lower() in safe_lower(book.get('제목')) or 
                                        keyword.lower() in safe_lower(book.get('저자')) or 
                                        keyword.lower() in safe_lower(book.get('출판사')) or
                                        keyword.lower() in safe_lower(book.get('출판일')) or
                                        keyword.lower() in safe_lower(book.get('청구기호')))]

# 건의 사항 저장 함수
def save_suggestion(suggestion):
    with open('suggestions.txt', 'a', encoding='utf-8') as f:
        timestamp = datetime.now().strftime('%Y-%m-%d\t')
        f.write(f"[{timestamp}]:{suggestion}\n")

# GUI 클래스 정의
class ChatBotApp(QWidget):
    def __init__(self, books):
        super().__init__()
        self.books = books
        self.chat_history = []
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('도서관 챗봇')
        self.setGeometry(100, 100, 500, 560)

        # 위젯 설정
        self.chat_label = QLabel('챗봇과 함께 나누는 즐거운 대화!!!~~~~')
        self.chat_label.setStyleSheet('font-size: 14pt;')
        self.chat_display = QTextEdit()
        self.chat_display.setStyleSheet('font-size: 12pt;')
        self.chat_display.setReadOnly(True)

        self.input_label = QLabel('질문:')
        self.input_label.setStyleSheet('font-size: 14pt;')
        
        # 콤보 박스 추가
        self.combo_box = QComboBox()
        self.combo_box.addItems(["챗봇", "건의"])

        self.user_input = QLineEdit()
        
        self.send_button = QPushButton('보내기')
        self.send_button.clicked.connect(self.handle_user_input)
        
        self.reset_button = QPushButton('리셋')
        self.reset_button.clicked.connect(self.clear_chat)
        
        self.user_input.returnPressed.connect(self.handle_user_input)

        # 레이아웃 설정
        layout = QVBoxLayout()
        layout.addWidget(self.chat_label)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.combo_box)
        input_layout.addWidget(self.user_input)
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
        
        selected_option = self.combo_box.currentText()
        
        if selected_option == "건의":
            # 건의 사항 저장
            save_suggestion(user_input)
            self.chat_display.append("챗봇: 건의 사항이 저장되었습니다.")
        else:
            # 도서 검색 및 응답 처리
            response = self.search_or_ask_openai(user_input)
            self.chat_display.append(f"챗봇: {response}")

        self.chat_display.append("")
        self.user_input.clear()
        
    def clear_chat(self):
        self.chat_display.clear()
        self.chat_history.clear()
        self.user_input.clear()
        
    def search_or_ask_openai(self, user_input):
        guide_prompt = '''
        도서(책)에 관한 정보의 질문(제목,저자,출판사,출판일,청구기호,도서상태)들은 대답하게 해줘 
        일반적인 질문들은 대화를 좀 더 친근하고 유머러스하게 만들어, 마치 친구와 대화하는 것처럼 자연스럽고 즐겁게 구성해줘
        '''
        self.chat_history.append({"role": "system", "content": guide_prompt})

        matched_books = search_book(user_input, self.books)

        if matched_books:
            unique_books = {book['제목']: book for book in matched_books}.values()
            formatted_results = "\n".join([f"제목: {book['제목']}, 저자: {book['저자']}, 출판사: {book['출판사']}, 출판일: {book['출판일']}, 청구기호: {book['청구기호']}, 도서상태: {book['도서상태']}" 
                                            for book in unique_books])
            book_prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 다음은 검색된 정보입니다:\n{formatted_results}\n관련된 책들을 소개해줘."
            messages = self.chat_history + [{"role": "system", "content": book_prompt}]
            response = ask_openai(messages)
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            return response
        else:
            prompt = f"사용자가 '{user_input}'에 대해 물어봤습니다. 관련된 정보를 알려주세요."
            messages = self.chat_history + [{"role": "user", "content": prompt}]
            response = ask_openai(messages)
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            return response

# 메인 함수
def main():
    # Excel 파일에서 책 정보 로드
    file_path = '/home/jeong-tae-hyeon/다운로드/total_book_list.xlsx'
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
