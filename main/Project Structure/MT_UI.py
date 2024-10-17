from operator import truediv
from ConcreteMediator import ConcreteMediator
import threading
import queue
import UI
import cv2
import time
## Mediator event que thread
class MT_UI(threading.Thread):
    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True
        self.mt_ui_event_que = queue.Queue()
        self.widget_cam1_thread = None
        self.widget_cam2_thread = None

    def set_widget_threads(self, widget_cam1_thread, widget_cam2_thread):
        self.widget_cam1_thread = widget_cam1_thread
        self.widget_cam2_thread = widget_cam2_thread

    def receive_message(self, target, final_target, message, sender, data=None):
        if final_target == 'WIDGET_CAM_1':
            if self.widget_cam1_thread is not None:
                self.widget_cam1_thread.put_frame(data)
                print(f"Put frame into widget_cam1_thread: {data.shape}")
        elif final_target == 'WIDGET_CAM_2':
            if self.widget_cam2_thread is not None:
                self.widget_cam2_thread.put_frame(data)
                print(f"Put frame into widget_cam2_thread: {data.shape}")

    def send_message(self, target, final_target, message, sender, data=None):
        if self._mediator is not None:
            self._mediator.send_message(target, final_target, message, sender, data)
        else:
            print(f"Error: mediator is not set in {self.name}")

    def run(self):
        print(f"MT_UI is started")
        while self.running:
            try:
                # 큐에서 메시지를 가져오고 처리
                target, final_target, message, sender, data = self.mt_ui_event_que.get()
                print(f"MT_UI received message: {message} from {sender} to {final_target}")

                # 메시지에 따라 처리
                if final_target == 'WIDGET_CAM_1':
                    if self.widget_cam1_thread is not None:
                        self.widget_cam1_thread.put_frame(data)
                        print(f"Put frame into widget_cam1_thread: {data.shape}")
                elif final_target == 'WIDGET_CAM_2':
                    if self.widget_cam2_thread is not None:
                        self.widget_cam2_thread.put_frame(data)
                        print(f"Put frame into widget_cam2_thread: {data.shape}")

            except queue.Empty:
                print("MT_UI Queue is empty")
                continue  # 큐가 비어있으면 계속 대기

    def stop(self):
        self.running = False

