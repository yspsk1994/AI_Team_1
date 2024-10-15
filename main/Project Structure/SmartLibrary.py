from ConcreteMediator import ConcreteMediator
from MT_Cam import MT_Cam
from MT_UI import MT_UI
from UI import MyWindow
from MT_Function import MT_Function
import sys
from PyQt6.QtWidgets import QApplication

import queue
import time


class SmartLibrary:
    def __init__(self, name, mediator):
        self.name = name
        self.mediator = mediator


mediator = ConcreteMediator()
shared_queue = queue.Queue()

mt_cam_thread = MT_Cam(mediator, "MT_CAM")
mt_function_thread = MT_Function(mediator, "MT_FUNCTION")
app = QApplication(sys.argv)
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

app.exec()