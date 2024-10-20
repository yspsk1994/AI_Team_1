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
        cam1 = multiprocessing.Process(target=cam1_process, args=(self._mediator, 'CAM_1'))
        cam2 = multiprocessing.Process(target=cam2_process, args=(self._mediator, 'CAM_2'))
        cam1.start()
        cam2.start()

        cam1.join()
        cam2.join()

    def stop(self):
        self.running.value = False
