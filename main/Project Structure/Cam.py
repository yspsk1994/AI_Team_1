import threading
import queue
import cv2
# import shared
import time
from multiprocessing import shared_memory
 
class Cam1_Thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # self.width = 1280
        # self.height = 720
        self.cam1_receive_que = queue.Queue()
        self.cam1_send_que = queue.Queue()
        self.Is_Start_Grabbing = False
        
    def run(self):
        while self.running:
               if self.Is_Start_Grabbing :
            
                ret, frame = self.cap.read()
                if ret:
                    self.cam1_send_que.put(("MT_UI","WIDGET_CAM_1","GET_FRAME","CAM_1",frame))
          
    def stop(self):
        self.running = False
    


class Cam2_Thread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        # self.cap = cv2.VideoCapture(0)
        self.width = 1280
        self.height = 720
        self.cam2_receive_que = queue.Queue()
        self.cam2_send_que = queue.Queue()
        
    def run(self):
        while self.running:
            if not self.cam2_receive_que.empty():
               ret, frame = self.cap.read()
               if ret:
                    self.cam2_send_que.put(frame)
                    time.sleep(1000)

    def stop(self):
        self.running = False