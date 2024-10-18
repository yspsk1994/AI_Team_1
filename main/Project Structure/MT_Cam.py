# MT_Cam.py
import multiprocessing
from Cam import cam1_process, cam2_process

class MT_Cam(multiprocessing.Process):
    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = multiprocessing.Value('b', True)

    def set_mediator(self, mediator):
        self._mediator = mediator

    def run(self):
        # Cam1과 Cam2를 별도의 프로세스로 실행
        cam1 = multiprocessing.Process(target=cam1_process, args=(self._mediator, 'CAM_1'))
        cam2 = multiprocessing.Process(target=cam2_process, args=(self._mediator, 'CAM_2'))

        cam1.start()
        cam2.start()

        # 별도의 루프가 필요하지 않으므로 프로세스 관리만 수행
        cam1.join()
        cam2.join()

    def stop(self):
        self.running.value = False
