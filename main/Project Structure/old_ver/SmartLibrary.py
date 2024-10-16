from ConcreteMediator import ConcreteMediator
from MT_Cam import MT_Cam
from MT_UI import MT_UI
from UI import MyWindow, Widget_Login
from MT_Function import MT_Function
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
import queue

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
        open_main_window()

def open_main_window():
    global window
    mt_cam_thread = MT_Cam(mediator, "MT_CAM")
    mt_function_thread = MT_Function(mediator, "MT_FUNCTION")

    window = MyWindow(None)
    window.show()

    widget_cam1 = window.widget_cam1
    widget_cam2 = window.widget_cam2
    widget_cam1_thread = window.widget_cam1_thread
    widget_cam2_thread = window.widget_cam2_thread

    mt_ui_thread = MT_UI(mediator, "MT_UI", widget_cam1, widget_cam2, widget_cam1_thread, widget_cam2_thread)

    window.mt_ui = mt_ui_thread

    mediator.add_user(mt_cam_thread)
    mediator.add_user(mt_function_thread)
    mediator.add_user(mt_ui_thread)

    mt_cam_thread.start()
    mt_function_thread.start()
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
