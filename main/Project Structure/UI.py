import sys
from tkinter import Widget
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QWidget, QPushButton
import threading
import cv2
import queue
from ConcreteMediator import ConcreteMediator

frame_que = queue.Queue()

## Main window
class MyWindow(QMainWindow):
    def __init__(self, mt_ui):
        super().__init__()
        self.Init_Main()
        self.Init_Widget()
        self.Init_btn()
        self.Init_Sub_Instance()
        self.Init_UI()
        self.mt_ui = mt_ui

    def Init_Main(self):
        self.setWindowTitle("도서 관리 프로그램")
        self.setGeometry(300,300,1000,800)

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
        layout = QVBoxLayout()
        layout.addWidget(self.widget_cam1)
        layout.addWidget(self.widget_cam2)

        layout.addWidget(self.btn_LiveMode)

        # 중앙 위젯 설정
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def Init_btn(self):
        #btn_Live : live on/off btn
        self.btn_LiveMode = QPushButton("Live", self)
        self.btn_LiveMode.setCheckable(True)
        self.btn_LiveMode.resize(100,50)
        self.btn_LiveMode.move(850,200)
        self.btn_LiveMode.clicked[bool].connect(self.toggleLiveMode)
    
    def changeColor(self, e):
        color = self.sender()

    def toggleLiveMode(self, checked):
        if checked:
            self.mt_ui.send_message("MT_CAM","CAM_1","START_GRABBING","WIDGET_CAM_1",None)
            print("Live mode ON, 메시지 전송")
        else:
            self.mt_ui.send_message("MT_CAM","CAM_1","STOP_GRABBING","WIDGET_CAM_1",None)
            print("Live mode OFF, 메시지 전송")

class Widget_Cam1_Thread(threading.Thread):
    def __init__(self,widget_cam1):
        super().__init__()
        self.running = True
        self.widget_cam1_que = queue.Queue()
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
        self.widget_cam2_que = queue.Queue()
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
        self.setFixedSize(640, 480)
        
    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.setPixmap(pixmap)

        
class Widget_Cam2(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(640, 480)

    def update_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.setPixmap(pixmap)




