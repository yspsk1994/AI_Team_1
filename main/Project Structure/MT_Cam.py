from operator import truediv
from pickle import TRUE
from tkinter.tix import Tree
from ConcreteMediator import ConcreteMediator
import threading
import queue
import Cam




class MT_Cam(threading.Thread) :
    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True

        self.mt_cam_event_que = queue.Queue()
        
        self.cam1_thread = Cam.Cam1_Thread()
        self.cam2_thread = Cam.Cam2_Thread()

        self.cam1_thread.start()
        self.cam2_thread.start()
        
        
    def receive_message(self, target, final_target, message, sender, data=None):
        self.mt_cam_event_que.put((target, final_target, message, sender, data))

    def send_message(self, target, final_target, message, sender, data=None):
        self._mediator.send_message(target, final_target, message, sender, data)


    def run(self):
        while self.running:
            if not self.mt_cam_event_que.empty():
                target, final_target, message, sender, data = self.mt_cam_event_que.get()
                
                if final_target == 'CAM_1':
                    if message == 'START_GRABBING':
                        self.cam1_thread.Is_Start_Grabbing = True
                        self.cam1_thread.cam1_receive_que.put((message,sender))                       
                    elif message == 'STOP_GRABBING':
                        self.cam1_thread.Is_Start_Grabbing = False


                elif final_target == 'CAM_2':
                    if message == 'START_GRABBING':
                        self.cam2_thread.Is_Start_Grabbing = True
                        self.cam2_thread.cam2_receive_que.put((message,sender))                       
                    elif message == 'STOP_GRABBING':
                        self.cam2_thread.Is_Start_Grabbing = False


            if not self.cam1_thread.cam1_send_que.empty():
                target, final_target, message, sender, data = self.cam1_thread.cam1_send_que.get()
                self.send_message(target,final_target,message,sender,data)

            if not self.cam2_thread.cam2_send_que.empty():
                target, final_target, message, sender, data = self.cam2_thread.cam2_send_que.get()
                self.send_message(target,final_target,message,sender,data)
                return


    def stop(self):
        self.running = False



