import multiprocessing
from multiprocessing import Process, Manager
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
import sys
from UI import Widget_Login, Ui_MainWindow
from ConcreteMediator import ConcreteMediator
from MT_Function import MT_Function
from MT_UI import MT_UI
from MT_DB import MT_DB
from Cam import cam1_process, cam2_process 
import queue
IsCorrect_ID = False

def check_login():
    global IsCorrect_ID
    if IsCorrect_ID:
        timer.stop()
        login_window.close()
        open_main_window()

def set_is_correct_id():
    global IsCorrect_ID
    IsCorrect_ID = True
    
def open_main_window():
    global window

    mediator = ConcreteMediator(cam1_queue, cam2_queue, ui_queue, function_queue)

    mt_function_thread = MT_Function(mediator, "MT_FUNCTION", function_queue)
    mt_ui_thread = MT_UI(mediator, "MT_UI", ui_queue, data_queue)
    mt_db_thread = MT_DB(mediator, "MT_DB")

    mediator.add_user(mt_function_thread)
    mediator.add_user(mt_ui_thread)
    mediator.add_user(mt_db_thread)

    mt_function_thread.start()
    mt_ui_thread.start()
    mt_db_thread.start()

    window = QMainWindow()
    main_ui = Ui_MainWindow(mt_ui_thread)
    main_ui.setupUi(window)
    main_ui.start_threads()  
    window.show()


if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    with Manager() as manager:
        cam1_queue = manager.Queue()
        cam2_queue = manager.Queue()
        ui_queue = manager.Queue()
        function_queue = manager.Queue()
        data_queue = manager.Queue()

        cam1_proc = Process(target=cam1_process, args=(ui_queue, function_queue))
        cam2_proc = Process(target=cam2_process, args=(ui_queue, function_queue))
        cam1_proc.start()
        cam2_proc.start()

        app = QApplication(sys.argv)

        login_window = Widget_Login(None)
        login_window.show()

        login_window.login_btn.clicked.connect(set_is_correct_id)

        timer = QTimer()
        timer.timeout.connect(check_login)
        timer.start(100)

        try:
            sys.exit(app.exec())
        except KeyboardInterrupt:
            print("프로세스 종료 중...")
        finally:
            cam1_proc.terminate()
            cam2_proc.terminate()
            cam1_proc.join()
            cam2_proc.join()