import sys
from PyQt6 import QtWidgets , QtGui
from PyQt6.QtWidgets import (QCheckBox, QPushButton, QMainWindow, QApplication, QGridLayout, QSizePolicy, QVBoxLayout, QFrame)
from PyQt6.QtGui import QColor
import threading
import cv2
import queue

frame_que = queue.Queue()

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.Init_main()
        self.Init_btn()
        self.display_thread = DisplayFrame()
        self.display_thread.start()
            
    def Init_main(self):
        self.setWindowTitle("도서 관리 프로그램")
        self.setGeometry(300,300,1000,800)
        self.cfrm = QFrame()
        self.setCentralWidget(self.cfrm)



        
    def Init_btn(self):
        #btn_Live : live on/off btn
        btn_LiveMode = QPushButton("Live", self)
        btn_LiveMode.setCheckable(True)
        btn_LiveMode.resize(100,50)
        btn_LiveMode.move(850,200)
        btn_LiveMode.click
        btn_LiveMode.clicked[bool].connect(self.changeColor)
    
    def changeColor(self, e):
        color = self.sender()

        


class DisplayFrame(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(1)
        self.Init_Widget()
        
    def Init_Widget(self):
        self.label = QtWidgets.QLabel()
        self.vbox = QtWidgets.QVBoxLayout()
        self.win = QtWidgets.QWidget() 
    def run(self):
        ret , frame = self.cap.read()
        while self.running:
            if ret :
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h,w,c = frame.shape
                qImg = QtGui.QImage(frame.data, w,h,w*c, QtGui.QImage.Format.Format_RGB32)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                frame_que.put(frame)
                
    def stop(self):
        self.running = False


app = QApplication(sys.argv)
window = MyWindow()
window.show()
# app.exec_()

