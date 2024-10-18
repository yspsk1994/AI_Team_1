from threading import Thread
from function.Checking_Book_Status import BookStatus
import time
from queue import Queue

class MT_Function(Thread):
    def __init__(self, mediator, name, function_queue):
        super().__init__()
        self._mediator = mediator
        self.name = name
        self.running = True
        self.checking_book_status = BookStatus()
        self.function_queue = function_queue
        self.cam1_function_queue = Queue()
        self.cam2_function_queue = Queue()

    def set_mediator(self, mediator):
        self._mediator = mediator

    def run(self):
        cam1_thread = Thread(target=self.process_cam1_frames)
        cam2_thread = Thread(target=self.process_cam2_frames)
        cam1_thread.start()
        cam2_thread.start()

        while self.running:
            if not self.function_queue.empty():
                target, frame = self.function_queue.get()
                if target == 'CAM_1_CHECK_BOOK_STATUS':
                    self.cam1_function_queue.put(frame)
                elif target == 'CAM_2_CHECK_BOOK_STATUS':
                    self.cam2_function_queue.put(frame)
            time.sleep(0.1)
        cam1_thread.join()
        cam2_thread.join()

    def process_cam1_frames(self):
        while self.running:
            if not self.cam1_function_queue.empty():
                frame = self.cam1_function_queue.get()
                highest_books = self.checking_book_status.Do_Process(frame)
                self._mediator.send_message("UI", "UPDATE_BOOK_LIST_1", highest_books)
            time.sleep(0.1)

    def process_cam2_frames(self):
        while self.running:
            if not self.cam2_function_queue.empty():
                frame = self.cam2_function_queue.get()
                highest_books = self.checking_book_status.Do_Process(frame)
                self._mediator.send_message("UI", "UPDATE_BOOK_LIST_2", highest_books)
            time.sleep(0.1)

    def stop(self):
        self.running = False
