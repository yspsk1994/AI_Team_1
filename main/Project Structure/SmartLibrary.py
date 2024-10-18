from ConcreteMediator import ConcreteMediator
from MT_Cam import MT_Cam
from MT_UI import MT_UI
from UI import MyWindow, Widget_Login
from MT_Function import MT_Function
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import queue
from MT_DB import MT_DB
import multiprocessing

IsCorrect_ID = False
class SmartLibrary:
    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator

    @staticmethod
    def handle_login():
        global IsCorrect_ID
        if login_window.ChekcIsCorrect():
            IsCorrect_ID = True

def check_login():
    global IsCorrect_ID
    if IsCorrect_ID:
        timer.stop()  
        login_window.close()
        open_main_window()

def open_main_window():
    global window

    # Mediator와 큐 설정
    mt_cam = MT_Cam(mediator, "MT_CAM")
    shared_queue = multiprocessing.Queue()  # 새로운 큐 생성
    mt_cam.set_queue(shared_queue)  # 큐 설정

    mt_function_thread = MT_Function(mediator, "MT_FUNCTION")

    # UI 창 생성 및 보여주기
    mt_ui_thread = MT_UI(mediator, "MT_UI")
    window = MyWindow(mt_ui_thread)
    window.show()   
    window.mt_ui = mt_ui_thread
    mt_db_thread = MT_DB(mediator, "MT_DB")

    # Mediator에 각 프로세스 추가
    mediator.add_user(mt_cam)
    mediator.add_user(mt_function_thread)
    mediator.add_user(mt_ui_thread)
    mediator.add_user(mt_db_thread)

    # 각 프로세스 시작
    mt_cam.start()
    mt_function_thread.start()
    mt_db_thread.start()

    # mt_ui_thread 시작은 마지막에
    mt_ui_thread.start()
    
mediator = ConcreteMediator()
shared_queue = queue.Queue()
app = QApplication(sys.argv)

login_window = Widget_Login(None) 
login_window.show()

login_window.login_btn.clicked.connect(SmartLibrary.handle_login)

timer = QTimer()
timer.timeout.connect(check_login)
timer.start(100)  # 100ms마다 확인

sys.exit(app.exec())