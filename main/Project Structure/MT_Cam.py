import multiprocessing
import queue
from Cam import Cam1_Process, Cam2_Process
import time

class MT_Cam(multiprocessing.Process):
    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = multiprocessing.Value('b', True)
        self.main_cam_queue = None  # 큐는 None으로 초기화
        self.cam1_process = Cam1_Process()  # Cam1 프로세스
        self.cam2_process = Cam2_Process()  # Cam2 프로세스

        self.cam1_process.start()
        self.cam2_process.start()

    def set_queue(self, cam_queue):
        self.main_cam_queue = cam_queue
        print(f"{self.name}: Queue has been set.")  # 큐가 설정되었는지 확인


    def receive_message(self, target, final_target, message, sender, data=None):
        if self.main_cam_queue is not None:
            self.main_cam_queue.put((target, final_target, message, sender, data))
        else:
            print(f"Error: Queue is not set in {self.name}.")

    def send_message(self, target, final_target, message, sender, data=None):
        print(f"Sending message: {message} from {sender} to {final_target}")  # 로그 추가
        self._mediator.send_message(target, final_target, message, sender, data)

    def run(self):
        if self.main_cam_queue is None:
            print(f"Error: main_cam_queue is not set for {self.name}. Exiting.")
            return

        while self.running.value:
            try:
                # Cam1, Cam2에서 받은 데이터를 처리하는 코드
                if not self.cam1_process.cam1_send_que.empty():
                    target, final_target, message, sender, frame = self.cam1_process.cam1_send_que.get(timeout=1)
                    print(f"Cam1 frame received: {frame.shape}")  # 프레임 로그 추가
                    self.send_message(target, final_target, message, sender, frame)

                if not self.cam2_process.cam2_send_que.empty():
                    target, final_target, message, sender, frame = self.cam2_process.cam2_send_que.get(timeout=1)
                    self.send_message(target, final_target, message, sender, frame)

                # 다른 메시지 처리 (START/STOP GRABBING)
                if not self.main_cam_queue.empty():
                    target, final_target, message, sender, data = self.main_cam_queue.get(timeout=1)
                    if message == 'START_GRABBING':
                        if final_target == 'CAM_1':
                            with self.cam1_process.is_start_grabbing.get_lock():
                                self.cam1_process.is_start_grabbing.value = True
                            print(f"{self.name}: Start grabbing for CAM_1")
                        elif final_target == 'CAM_2':
                            with self.cam2_process.is_start_grabbing.get_lock():
                                self.cam2_process.is_start_grabbing.value = True
                            print(f"{self.name}: Start grabbing for CAM_2")
                    elif message == 'STOP_GRABBING':
                        if final_target == 'CAM_1':
                            with self.cam1_process.is_start_grabbing.get_lock():
                                self.cam1_process.is_start_grabbing.value = False
                            print(f"{self.name}: Stop grabbing for CAM_1")
                        elif final_target == 'CAM_2':
                            with self.cam2_process.is_start_grabbing.get_lock():
                                self.cam2_process.is_start_grabbing.value = False
                            print(f"{self.name}: Stop grabbing for CAM_2")
                    # 메시지를 처리했으므로 일정 시간 대기
                    time.sleep(0.01)

            except queue.Empty:
                time.sleep(0.1)  # 큐가 비었을 경우 잠시 대기
                continue

    def stop(self):
        """ 프로세스 안전 종료 """
        self.running.value = False
        if self.cam1_process is not None:
            self.cam1_process.stop()
            self.cam1_process.join()
        if self.cam2_process is not None:
            self.cam2_process.stop()
            self.cam2_process.join()
