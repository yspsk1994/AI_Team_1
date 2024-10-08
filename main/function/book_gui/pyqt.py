import sys
import cv2
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QMainWindow, QStackedWidget, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QImage, QPixmap


class LoginWindow(QWidget):
    def __init__(self, switch_window):
        super().__init__()
        self.switch_window = switch_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('스마트 도서관 AI 관리 시스템')
        self.setFixedSize(800, 600)  # 창 크기 고정

        layout = QVBoxLayout()
        layout.setSpacing(10)  # 위젯 간 간격 설정

        # 타이틀 레이블
        title_label = QLabel('스마트 도서관 AI 관리 시스템')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(title_label)

        # 아이디 입력
        self.username_label = QLabel('아이디:')
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # 비밀번호 입력
        self.password_label = QLabel('비밀번호:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        self.password_input.returnPressed.connect(self.handle_login)

        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        
        # 로그인 버튼
        self.login_button = QPushButton('로그인')
        self.login_button.clicked.connect(self.handle_login)
        button_layout.addWidget(self.login_button)

        # 종료 버튼
        self.exit_button = QPushButton('종료')
        self.exit_button.clicked.connect(QApplication.instance().quit)
        button_layout.addWidget(self.exit_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    # 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 25px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # 간단한 인증 로직 (실제 구현 시 보안 강화 필요)
        if username == 'admin' and password == '1234':
            self.switch_window()
        else:
            QMessageBox.warning(self, '오류', '잘못된 사용자명 또는 비밀번호입니다.')

class MainDashboard(QMainWindow):
    def __init__(self, switch_login):
        super().__init__()
        self.switch_login = switch_login
        self.setWindowTitle('스마트 도서관 AI 관리 시스템')
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()

        # 스택 위젯 생성
        self.stacked_widget = QStackedWidget()

        # 메인 대시보드 페이지
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)

        self.wrongfind_button = QPushButton('도서 검색')
        self.wrongfind_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        dashboard_layout.addWidget(self.wrongfind_button)

        self.bookfind_button = QPushButton('.')
        self.bookfind_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        dashboard_layout.addWidget(self.bookfind_button)

        self.register_button = QPushButton('신간 도서 등록')
        self.register_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        dashboard_layout.addWidget(self.register_button)

        back_button = QPushButton('뒤로')
        back_button.setStyleSheet("background-color: gray; color: black")
        back_button.clicked.connect(self.switch_login)
        dashboard_layout.addWidget(back_button)

        # 스택 위젯에 페이지 추가
        self.stacked_widget.addWidget(dashboard_page)                       #setCurrentIndex(0)
        self.stacked_widget.addWidget(WrongFindPage(self.stacked_widget))   #setCurrentIndex(1)
        self.stacked_widget.addWidget(BookFindPage(self.stacked_widget))    #setCurrentIndex(2)
        self.stacked_widget.addWidget(RegisterPage(self.stacked_widget))    #setCurrentIndex(3)

        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        
        # 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 25px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

class WrongFindPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('오배치 도서 찾기 기능을 구현하세요.'))
        back_button = QPushButton('뒤로')
        back_button.setStyleSheet("background-color: gray; color: black")
        back_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_button)
        
        # 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 25px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

class BookFindPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('원하는 도서 찾기 기능을 구현하세요.'))
        back_button = QPushButton('뒤로')
        back_button.setStyleSheet("background-color: gray; color: black")
        back_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_button)
        
        # 스타일 설정
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 25px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

class RegisterPage(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # 웹캠 화면을 표시할 QLabel
        self.webcam_label = QLabel(self)
        self.webcam_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.webcam_label)

        # 도서 정보 입력 필드 (예시)
        self.book_title = QLineEdit(self)
        self.book_title.setPlaceholderText("도서 제목")
        self.book_title.returnPressed.connect(self.register_book)
        layout.addWidget(self.book_title)

        # 등록 버튼
        register_button = QPushButton('도서 등록', self)
        register_button.clicked.connect(self.register_book)
        layout.addWidget(register_button)

        # 뒤로 가기 버튼
        back_button = QPushButton('뒤로', self)
        back_button.setStyleSheet("background-color: gray; color: black")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_button)

        # 웹캠 설정
        self.capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 30ms마다 프레임 업데이트

    def update_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(convert_to_qt_format)
            self.webcam_label.setPixmap(pixmap)

    def register_book(self):
        # 여기에 도서 등록 로직을 구현하세요
        print("도서가 등록되었습니다.")
        QMessageBox.information(self, '정보', '도서가 등록되었습니다.') #공란이 아닐때 하기

    def closeEvent(self, event):
        self.capture.release()

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("함초롬바탕"))
    stacked_widget = QStackedWidget()
    
    # 로그인 창 인스턴스
    login_window = LoginWindow(lambda: switch_to_dashboard(stacked_widget, main_dashboard))

    # 메인 대시보드 인스턴스
    main_dashboard = MainDashboard(lambda: switch_to_login(stacked_widget, login_window))
    
    stacked_widget.addWidget(login_window)
    stacked_widget.addWidget(main_dashboard)

    stacked_widget.setCurrentWidget(login_window)
    stacked_widget.show()

    sys.exit(app.exec_())

def switch_to_dashboard(stacked_widget, dashboard):
    stacked_widget.setCurrentWidget(dashboard)

def switch_to_login(stacked_widget, login_window):
    stacked_widget.setCurrentWidget(login_window)

if __name__ == '__main__':
     main()