from operator import truediv
from ConcreteMediator import ConcreteMediator
import threading
import queue
import Cam




class MT_Cam(threading.Thread) :
    def __init__(self, mediator, name, shared_queue):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True
        self.mt_cam_event_que = queue.Queue()
        self.mt_cam1_que = queue.Queue()
        self.mt_cam2_que = queue.Queue()
        
        self.cam1 = Cam.Cam1()
        self.cam2 = Cam.Cam2()
        self.cam1_msg = Cam.Cam1_Msg(shared_queue)
        self.cam2_msg = Cam.Cam2_Msg(shared_queue)
        self.cam_shared_queue = shared_queue
        
        self.cam1.start()
        self.cam2.start()
        self.cam1_msg.start()
        self.cam2_msg.start()
        
        
    def receive_message(self, message, sender, data=None):
        self.mt_cam_event_que.put((message,sender))

    def send_message(self, target, message, data=None):
        self._mediator.send_message(target, message, self, data)


    def run(self):
        while self.running:
            if not self.mt_cam_event_que.empty():
                message , sender = self.mt_cam_event_que.get()

                if message == 'Cam1':
                    self.cam_shared_queue.put((message,sender))
                elif message == 'Cam2':
                    self.cam_shared_queue.put((message,sender))

    def stop(self):
        self.running = False

import shared

shared.mt_cam_instance = MT_Cam(mediator="mediator_instance", name="MT_Cam_1")
