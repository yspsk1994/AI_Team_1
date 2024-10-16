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
        self.Init_Main()
        self.Init_Widget()
        self.Init_btn()
        self.Init_Sub_Instance()
        self.Init_UI()
        self.mt_ui = mt_ui
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
        # self.setGeometry(400, 200, int(monitor_size.width()/1.5), int(monitor_size.height()/1.5))

    def Init_Widget(self):
        self.widget_cam1 = Widget_Cam1(self)
        self.widget_cam2 = Widget_Cam2(self)
        
        
    def Init_Sub_Instance(self):
        self.widget_cam1_thread = Widget_Cam1_Thread(self.widget_cam1)
        self.widget_cam2_thread = Widget_Cam2_Thread(self.widget_cam2)
        self.widget_cam1_thread.start()
        self.widget_cam2_thread.start()
        
    def Init_UI(self):
        # 레이아웃 설정
        self.widget_cam1.setParent(self)
        self.widget_cam1.move(50, 50)  # (50, 50)에 배치
        self.widget_cam1.resize(800, 450)  # 크기 설정

        self.widget_cam2.setParent(self)
        self.widget_cam2.move(1500, 50)  # (900, 50)에 배치
        self.widget_cam2.resize(800, 450)  # 크기 설정
        
        # layout = QVBoxLayout()
        # layout.addWidget(self.widget_cam1)
        # layout.addWidget(self.widget_cam2)
        
        # layout.addWidget(self.btn_LiveMode)

        # 중앙 위젯 설정
        # central_widget = QWidget()
        # central_widget.setLayout(layout)
        # self.setCentralWidget(central_widget)

    def Init_btn(self):
        #btn_Live : live on/off btn
        self.btn_LiveMode = QPushButton("Live", self)
        self.btn_LiveMode.setCheckable(True)
        self.btn_LiveMode.resize(300,100)
        self.btn_LiveMode.move(100,1200)
        self.btn_LiveMode.clicked[bool].connect(self.toggleLiveMode)
  
        self.btn_Checking_BookStatus = QPushButton("책 상태 검사", self)
        self.btn_Checking_BookStatus.setCheckable(True)
        self.btn_Checking_BookStatus.resize(300,100)
        self.btn_Checking_BookStatus.move(500,1200)
        self.btn_Checking_BookStatus.clicked[bool].connect(self.toggleLiveMode)  
        
    def changeColor(self, e):
        color = self.sender()

    def toggleLiveMode(self, checked):
        if checked:
            self.mt_ui.send_message("MT_CAM","CAM_2","START_GRABBING","WIDGET_CAM_2",None)
            print("Live mode ON, 메시지 전송")
        else:
            self.mt_ui.send_message("MT_CAM","CAM_2","STOP_GRABBING","WIDGET_CAM_2",None)
            print("Live mode OFF, 메시지 전송")

class Widget_Cam1_Thread(threading.Thread):
    def __init__(self,widget_cam1):
        super().__init__()
        self.running = True
        self.widget_cam1_que = queue.Queue(maxsize=10)
        self.widget_cam1 = widget_cam1

    def run(self):
        while(self.running):
            if not self.widget_cam1_que.empty():
                frame= self.widget_cam1_que.get()
                self.widget_cam1.update_frame(frame)
    def stop(self):
        self.running = False
class Widget_Cam2_Thread(threading.Thread):
    def __init__(self,widget_cam2):
        super().__init__()
        self.running = True
        self.widget_cam2_que = queue.Queue(maxsize=10)
        self.widget_cam2 = widget_cam2

    def run(self):
        while(self.running):
            if not self.widget_cam2_que.empty():
                frame= self.widget_cam2_que.get()
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

    # def StartMainWindow(self):
    #     if not self.main_window:
    #         self.main_window = MyWindow(self.mt_ui)  
    #     self.main_window.show() 
    #     self.close()  