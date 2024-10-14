import threading
import queue
import cv2
import shared

class Cam1(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mt_cam = shared.mt_cam_instance

    def run(self):
        while self.running:
            if not self.mt_cam.mt_cam1_que.empty():
                message, sender = self.mt_cam.mt_cam1_que.get()
                

    def stop(self):
        self.running = False




class Cam2(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mt_cam = shared.mt_cam_instance

    def run(self):
        while self.running:
            if not self.mt_cam.mt_cam2_que.empty():
                message, sender = self.mt_cam.mt_cam2_que.get()
                

    def stop(self):
        self.running = False