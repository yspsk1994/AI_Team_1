from ConcreteMediator import ConcreteMediator
import threading
import queue
from Function import Checking_Book_Status
class MT_Function(threading.Thread):

    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self._name = name
        self.running = True
        self.main_function_que = queue.Queue()

        self.func1_thread = Checking_Book_Status.BookStatus_Thread()
        self.func1_thread.start()
        
    def receive_message(self, target, final_target, message, sender, data=None):
        self.main_function_que.put((target, final_target, message,sender, data))

    def send_message(self, target, final_target, message, sender, data=None):
        self._mediator.send_message(target, final_target, message, sender, data)

    
    def run(self):
        while self.running:
            try:
                print("MT_Function")
                target, final_target, message, sender, data = self.main_function_que.get()
                if final_target == 'FUNC1':
                    self.func1_thread.bookstatus_receive_que.put(data)
                    # self.func1_thread.running = True
                elif message == 'function2':
                    return
                elif message == 'function2':
                    return
                elif message == 'function3':
                    return
            except queue.Empty:
                continue
                

    def stop(self):
        self.main_function_que._stop()