import sys
from tkinter import Widget
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import *
import threading
from PyQt6.QtCore import QThread
import cv2
import queue
from ConcreteMediator import ConcreteMediator
import time

frame_que = queue.Queue()

class MyWindow(QMainWindow):
    def __init__(self, mt_ui):
        super().__init__()
        self.mt_ui = mt_ui
        self.Init_Main()
        self.Init_Widget()  # 먼저 위젯을 초기화해야 함
        self.Init_btn()
        self.Init_Sub_Instance()
        self.Init_UI()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Close', 
                                    'Are you sure you want to close the window?', 
                                    QMessageBox.Yes | QMessageBox.No, 
                                    QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept() 
        else:
            event.ignore()

    def Init_Main(self):
        self.setWindowTitle("도서 관리 프로그램")
        monitor_size = self.screen().availableGeometry()
        self.setGeometry(monitor_size.x(), monitor_size.y(), monitor_size.width(), monitor_size.height())

    def Init_Widget(self):
        # widget_cam1과 widget_cam2를 초기화
        self.widget_cam1 = Widget_Cam1(self)
        self.widget_cam2 = Widget_Cam2(self)
        self.tableWIdget_checkout = QTableWidget(self)
        self.tableWIdget_checkout.setRowCount(20)
        self.tableWIdget_checkout.setColumnCount(5)
        self.tableWIdget_checkout.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWIdget_checkout.setHorizontalHeaderLabels(["제목", "저자", "출판사", "ISBN", "도서상태"])

        self.tableWIdget_checkout.move(50, 50)  # x, y 좌표
        self.tableWIdget_checkout.resize(500, 600)  # width, height


        # 테이블에 데이터 추가
        for i in range(20):
            for j in range(5):
                self.tableWIdget_checkout.setItem(i, j, QTableWidgetItem(f"Item {i+1}-{j+1}"))        

    def Init_Sub_Instance(self):
        # widget_cam1과 widget_cam2가 초기화된 후에 thread 생성
        self.widget_cam1_thread = Widget_Cam1_Thread(self.widget_cam1)
        self.widget_cam2_thread = Widget_Cam2_Thread(self.widget_cam2)
        self.widget_cam1_thread.start()
        self.widget_cam2_thread.start()

    def Init_btn(self):
        # 버튼 초기화
        self.btn_LiveMode = QPushButton("Live", self)
        self.btn_LiveMode.setCheckable(True)
        self.btn_LiveMode.resize(300, 100)
        self.btn_LiveMode.move(100,1200)
        self.btn_LiveMode.clicked[bool].connect(self.toggleLiveMode)

        self.btn_Checking_BookStatus = QPushButton("책 상태 검사", self)
        self.btn_Checking_BookStatus.setCheckable(True)
        self.btn_Checking_BookStatus.resize(300, 100)
        self.btn_Checking_BookStatus.move(500, 1200)
        self.btn_Checking_BookStatus.clicked[bool].connect(self.Checking_BookStatus_Mode)

    def Init_UI(self):
        # UI 초기화 부분 (필요 시 추가 작업)
        pass

    def toggleLiveMode(self, checked):
        if checked:
            self.mt_ui.send_message("MT_CAM", "CAM_2", "START_GRABBING", "WIDGET_CAM_2", None)
            print("Live mode ON, 메시지 전송")
        else:
            self.mt_ui.send_message("MT_CAM", "CAM_2", "STOP_GRABBING", "WIDGET_CAM_2", None)
            print("Live mode OFF, 메시지 전송")

    def Checking_BookStatus_Mode(self, checked):
        self.dialog = BookStatus_Window(self.mt_ui, self.widget_cam1_thread)  # 기존 스레드를 전달합니다.
        self.dialog.exec()


            
class Widget_Cam1_Thread(threading.Thread):
    def __init__(self,widget_cam1):
        super().__init__()
        self.running = True
        self.widget_cam1_que = queue.Queue(maxsize=10)
        self.widget_cam1 = widget_cam1
        self.frame = None
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
    def run(self):
        while(self.running):
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
                self.widget_cam1.update_frame(frame)
    def stop(self):
        self.running = False
    
    def Get_Frame(self):
            return self.frame  
              
class Widget_Cam2_Thread(threading.Thread):
    def __init__(self,widget_cam2):
        super().__init__()
        self.running = True
        self.widget_cam2_que = queue.Queue(maxsize=10)
        self.widget_cam2 = widget_cam2
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        
    def run(self):
        while(self.running):
            ret, frame = self.cap.read()
            if ret:
                self.widget_cam2.update_frame(frame)   

    def stop(self):
        self.running = False

class Widget_Cam1(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(200, 100)

    def update_frame(self, frame):
        widget_width = self.width()
        widget_height = self.height()
        frame = cv2.resize(frame,(widget_width, widget_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.setPixmap(pixmap)
               
class Widget_Cam2(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(200, 100)

        
    def update_frame(self, frame):
        widget_width = self.width()
        widget_height = self.height()
        frame = cv2.resize(frame,(widget_width, widget_height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        h, w, c = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.setPixmap(pixmap)

class BookStatus_Window(QDialog):
    def __init__(self, mt_ui, widget_cam1_thread):
        super().__init__()
        self.setWindowTitle("책 상태 검사")
        self.setGeometry(300, 300, 1000, 600)  # 창의 크기 설정
        self.widget_cam1_thread = widget_cam1_thread  # 기존 스레드를 사용합니다.
        self.mt_ui = mt_ui  
  
        # UI 요소 추가
        self.btn_Checking_BookStatus = QPushButton("책 검사 실행", self)
        self.btn_Checking_BookStatus.setCheckable(True)
        self.btn_Checking_BookStatus.resize(300, 100)
        self.btn_Checking_BookStatus.move(300,200)
        self.btn_Checking_BookStatus.clicked[bool].connect(self.check_event)  
                
        self.btn_close = QPushButton("닫기", self)
        self.btn_close.move(150, 200)
        self.btn_close.clicked.connect(self.close)  # 닫기 버튼 클

    def check_event(self, checked):
        if checked:
            frame = self.widget_cam1_thread.Get_Frame()
            self.mt_ui.send_message("MT_FUNCTION", "FUNC1", "START_PROCESS", "BOOK_STATUS_BTN", frame)
            print("Checking book status 메세지 전송")
        else:
            print("Checking book status 메세지 실패")




class Widget_Login(QWidget):
    def __init__(self, mt_ui):
        super().__init__()
        self.setWindowTitle("Login")
        self.mt_ui = mt_ui  
        monitor_size = self.screen().availableGeometry()
        self.setGeometry(int(monitor_size.x() + monitor_size.width() / 2 - 100),
                         int(monitor_size.y() + monitor_size.height() / 2 - 50),
                         400, 200)
        self.main_window = None

        self.result_label = QLabel('', self)
        self.id_label = QLabel('ID : ', self)
        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText('아이디를 입력 해 주세요')

        self.password_label = QLabel('Password : ', self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText('비밀번호를 입력 해 주세요')

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.ChekcIsCorrect)

        form_layout = QVBoxLayout()

        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_label)
        id_layout.addWidget(self.id_input)

        password_layout = QHBoxLayout()
        password_layout.addWidget(self.password_label)
        password_layout.addWidget(self.password_input)

        form_layout.addLayout(id_layout)
        form_layout.addLayout(password_layout)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.result_label)

        self.setLayout(form_layout)
              
    def ChekcIsCorrect(self):
        if self.id_input.text() == 'yspsk1994' and self.password_input.text() == "1234":
            self.result_label.setText("Login successful")
            # self.StartMainWindow()
            return True            
        else:
            self.result_label.setText('Invalid ID or Password')
            return False
