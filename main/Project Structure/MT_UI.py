import threading
import queue

class MT_UI(threading.Thread):
    def __init__(self, mediator, name, ui_queue, data_queue ):
        super().__init__()
        self.mediator = mediator
        self.name = name
        self.ui_queue = ui_queue
        self.running = True
        self.cam1_queue = queue.Queue()
        self.cam2_queue = queue.Queue()
        self.data_queue = data_queue 

    def run(self):
        while self.running:
            if not self.ui_queue.empty():
                target, frame = self.ui_queue.get()
                if target == 'WIDGET_CAM_1':
                    self.cam1_queue.put(frame)
                elif target == 'WIDGET_CAM_2':
                    self.cam2_queue.put(frame)
            if not self.data_queue.empty():
                message_type, data = self.data_queue.get()
                if message_type == "UPDATE_BOOK_LIST_1":
                    self.mediator.send_message("UI", "UPDATE_BOOK_LIST_1", data)
                elif message_type == "UPDATE_BOOK_LIST_2":
                    self.mediator.send_message("UI", "UPDATE_BOOK_LIST_2", data)


    def set_mediator(self, mediator):
        self._mediator = mediator
    def stop(self):
        self.running = False
