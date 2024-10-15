from ConcreteMediator import ConcreteMediator
import threading
import queue

class MT_Function(threading.Thread):

    def __init__(self, mediator, name):
        super().__init__()
        self._mediator = mediator
        self._name = name
        self.running = True
        self.main_function_que = queue.Queue()
        
    def receive_message(self, target, final_target, message, sender, data=None):
        self.main_function_que.put((target, final_target, message,sender, data))

    def send_message(self, target, final_target, message, sender, data=None):
        self._mediator.send_message(target, final_target, message, sender, data)

    
    def run(self):
        while self.running:
            if not self.main_function_que.empty() :
                message, sender = self.main_function_que.get()
                if message == 'function1':
                    return
                elif message == 'function2':
                    return
                elif message == 'function2':
                    return
                elif message == 'function3':
                    return
                

    def stop(self):
        self.main_function_que._stop()