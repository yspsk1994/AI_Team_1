import oop_ui
import oop_db
import oop_cam
import oop_funcN

import threading
import time

import oop_db
oop_db.함수1()


# Mediator 클래스
class Mediator:
    def __init__(self):
        self.ui_thread = UIComponent(self)
        self.db_thread = DatabaseComponent(self)
        self.cam_thread = CamComponent(self)
        self.func_thread = FunctionsComponent(self)
        
    # Mediator가 관리하는 실행 메서드
    def start(self):
        # 동시에 여러 스레드를 실행
        threads = []
        threads.append(threading.Thread(target=self.ui_thread.run))
        threads.append(threading.Thread(target=self.db_thread.run))
        threads.append(threading.Thread(target=self.cam_thread.run))
        threads.append(threading.Thread(target=self.func_thread.run))
        
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()  # 스레드들이 모두 종료될 때까지 기다림
        

# UI Thread Component
class UIComponent:
    def __init__(self, mediator):
        self.mediator = mediator

    def run(self):
        oop_ui.exec_ui()  #실제 동작 부분

# Database Thread Component
class DatabaseComponent:
    def __init__(self, mediator):
        self.mediator = mediator

    def run(self):
        oop_db.exec_db()  #실제 동작 부분

# Cam Thread Component
class CamComponent:
    def __init__(self, mediator):
        self.mediator = mediator

    def run(self):
        oop_cam.exec_cam()  #실제 동작 부분

# Functions Thread Component
class FunctionsComponent:
    def __init__(self, mediator):
        self.mediator = mediator

    def run(self):
        print("Functions Thread started")
        for i in range(3):
            time.sleep(20)  # Simulate function execution
            print(f"Functions Component running cnt: {20*(i+1)}")
        print("Functions Thread finished")

# Mediator 실행
if __name__ == "__main__":
     mediator = Mediator()
     mediator.start()
