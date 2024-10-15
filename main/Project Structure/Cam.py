import threading
import queue
import cv2
# import shared
import time
from multiprocessing import shared_memory
 
 
class Cam1_Msg(threading.Thread):
    def __init__(self,shared_queue):
        super().__init__()
        self.running = True
        self.cam_shared_queue = shared_queue
        
        
    def run(self):
        while self.running:
            # if not self.mt_cam.mt_cam1_que.empty():
                # message, sender = self.mt_cam.mt_cam1_que.get()
            continue
    def stop(self):
        self.running = False
        


class Cam1(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(1)

        # self.width = 1280
        # self.height = 720
        self.cam1_que = queue.Queue()
        
    def run(self):
        while self.running:
            # time.sleep(1000)
            ret, frame = self.cap.read()
            if ret:
                self.cam1_que.put(frame)
                cv2.imshow("cam1_frmae", frame)
                cv2.waitKey(1)
         
            
            
            
    def stop(self):
        self.running = False
    



class Cam2_Msg(threading.Thread):
    def __init__(self,shared_queue):
        super().__init__()
        self.running = True
        self.cam_shared_queue = shared_queue
    
        # self.mt_cam = shared.mt_cam_instance
        
    def run(self):
        while self.running:
            if not self.cam_shared_queue.empty():
                message, sender = self.cam_shared_queue.get()
            continue
                    
    def stop(self):
        self.running = False
        


class Cam2(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        # self.cap = cv2.VideoCapture(0)
        self.width = 1280
        self.height = 720
        self.cam2_que = queue.Queue()
        
    def run(self):
        while self.running:
            # ret, frame = self.cap.read(1)
            # self.cam2_que.put(frame)
            continue
    def stop(self):
        self.running = False