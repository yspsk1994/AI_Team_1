from operator import truediv
from ConcreteMediator import ConcreteMediator
import threading
import queue
import UI

## Mediator event que thread
class MT_UI(threading.Thread) :
    def __init__(self, mediator, name, widget_cam1, widget_cam2, widget_cam1_thread, widget_cam2_thread):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True

        self.mt_ui_event_que = queue.Queue()
        self.widget_cam1 = widget_cam1
        self.widget_cam2 = widget_cam2
        self.widget_cam1_thread = widget_cam1_thread
        self.widget_cam2_thread = widget_cam2_thread
  


    def receive_message(self, target, final_target, message, sender, data=None):
        self.mt_ui_event_que.put((target,final_target, message,sender, data))

    def send_message(self, target, final_target, message, sender, data=None):
        self._mediator.send_message(target, final_target, message, sender, data)


    def run(self):
        while self.running:
            if not self.mt_ui_event_que.empty():
                target, final_target, message, sender, data = self.mt_ui_event_que.get()

                if final_target == 'WIDGET_CAM_1':
                    self.widget_cam1_thread.widget_cam1_que.put(data)
                elif message == 'WIDGET_CAM_2':
                    self.widget_cam2_thread.widget_cam2_que.put(data)

    def stop(self):
        self.running = False
