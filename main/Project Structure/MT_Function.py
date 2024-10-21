import threading
import queue
from Function.Checking_Book_Status import BookStatus
import time
from concurrent.futures import ThreadPoolExecutor

class MT_Function(threading.Thread):
    def __init__(self, mediator, name, function_queue,update_data_queue, db_function):
        super().__init__()
        self.mediator = mediator
        self.name = name
        self.function_queue = function_queue
        self.update_data_queue = update_data_queue
        self.db_function = db_function
        self.running = True
        self.checking_book_status = BookStatus(db_function,update_data_queue)
        
        self.executor = ThreadPoolExecutor(max_workers=2) 

    def run(self):
        function_thread = threading.Thread(target = self.process_function_frames)
        update_data_thread = threading.Thread(target=self.process_update_data_queue)
     
        function_thread.start()
        update_data_thread.start()

        function_thread.join()
        update_data_thread.join()

    def process_function_frames(self):
        while self.running:
            try:
                target, frame = self.function_queue.get(timeout=0.1)
                if target == f'{self.name}_CHECK_BOOK_STATUS':
                    self.executor.submit(self.checking_book_status.Do_Process, frame.copy())
            except queue.Empty:
                pass

    def process_update_data_queue(self):
        while self.running:
            try:
                message_type, data = self.update_data_queue.get(timeout=0.1)
                if message_type == "UPDATE_BOOK_LIST":
                    self.mediator.message_queue.put(("UI", "UPDATE_BOOK_LIST", data))
            except queue.Empty:
                pass
            
    def stop(self):
        self.running = False
        self.executor.shutdown(wait=True) 
        self.join()
    def set_mediator(self, mediator):
        self._mediator = mediator