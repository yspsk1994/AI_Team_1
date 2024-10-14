from operator import truediv
from ConcreteMediator import ConcreteMediator
import threading
import queue
import shared



class MT_Cam(threading.Thread) :
    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True
        self.mt_cam_event_que = queue.Queue()
        self.mt_cam1_que = queue.Queue()
        self.mt_cam2_que = queue.Queue()

    def receive_message(self, message, sender, data=None):
        self.mt_cam_event_que.put((message,sender))

    def send_message(self, target, message, data=None):
        self._mediator.send_message(target, message, self, data)


    def run(self):
        while self.running:
            print("Running cam thread")
            if not self.mt_cam_event_que.empty():
                message , sender = self.mt_cam_event_que.get()

                if message == 'Cam1':
                    self.mt_cam1_que.put((message,sender))
                elif message == 'Cam2':
                    self.mt_cam2_que.put((message,sender))

    def stop(self):
        self.running = False

shared.mt_cam_instance = MT_Cam(mediator="mediator_instance", name="MT_Cam_1")
