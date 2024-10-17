from ConcreteMediator import ConcreteMediator
import threading
import queue
class MT_DB(threading.Thread):

    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self._name = name
        self.running = True
        self.main_db_que = queue.Queue()
        
    def receive_message(self, target, final_target, message, sender, data=None):
        self.main_db_que.put((target, final_target, message,sender, data))

    def send_message(self, target, final_target, message, sender, data=None):
        self._mediator.send_message(target, final_target, message, sender, data)

    
    def run(self):
        while self.running:
            try:
                print("MT_DB_THREAD")
                message, sender = self.main_db_que.get()
                if message == 'function1':
                    return
                elif message == 'function2':
                    return
                elif message == 'function2':
                    return
                elif message == 'function3':
                    return
            except queue.Empty:
                continue
    def stop(self):
        self.main_db_que._stop()