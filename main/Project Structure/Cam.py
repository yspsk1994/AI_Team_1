import multiprocessing
import cv2
import time
from multiprocessing import Queue

class Cam1_Process(multiprocessing.Process):
    def __init__(self):
        super().__init__()
        self.running = multiprocessing.Value('b', True)  # 프로세스 실행 여부
        self.is_start_grabbing = multiprocessing.Value('b', False)  # 프레임 캡처 시작 여부
        self.cam1_send_que = Queue()  # 프레임을 전송할 큐

        self.cap = cv2.VideoCapture(1)  # 카메라 장치 5번 사용
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def run(self):
        try:
            while self.running.value:
                # print("Cam1_Process")
                if self.is_start_grabbing.value:
                    ret, frame = self.cap.read()
                    if ret:
                        # 프레임 전송
                        self.cam1_send_que.put(("MT_UI", "WIDGET_CAM_1", "GET_FRAME", "CAM_1", frame))
                time.sleep(0.5)  # CPU 부하를 줄이기 위한 대기
        except Exception as e:
            print(f"Exception in Cam1_Process: {e}")
        finally:
            self.cap.release()  # 프로세스 종료 시 카메라 자원 해제
            print("Cam1_Process stopped and camera released.")

    def stop(self):
        with self.running.get_lock():
            self.running.value = False  # 프로세스 종료


class Cam2_Process(multiprocessing.Process):
    def __init__(self):
        super().__init__()
        self.running = multiprocessing.Value('b', True)  # 프로세스 실행 여부
        self.is_start_grabbing = multiprocessing.Value('b', False)  # 프레임 캡처 시작 여부
        self.cam2_send_que = Queue()  # 프레임을 전송할 큐

        self.cap = cv2.VideoCapture(1)  # 카메라 장치 0번 사용
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    def run(self):
        try:
            while self.running.value:
                # print("Cam2_Process")
                if self.is_start_grabbing.value:
                    ret, frame = self.cap.read()
                    if ret:
                        # 프레임 전송
                        self.cam2_send_que.put(("MT_UI", "WIDGET_CAM_2", "GET_FRAME", "CAM_2", frame))
                time.sleep(0.5)  # CPU 부하를 줄이기 위한 대기
        except Exception as e:
            print(f"Exception in Cam2_Process: {e}")
        finally:
            self.cap.release()  # 프로세스 종료 시 카메라 자원 해제
            print("Cam2_Process stopped and camera released.")

    def stop(self):
        with self.running.get_lock():
            self.running.value = False  # 프로세스 종료
