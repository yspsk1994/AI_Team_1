import multiprocessing
from multiprocessing import Process, Manager
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
import sys
from UI import Widget_Login, Ui_MainWindow
from ConcreteMediator import ConcreteMediator
from MT_Function import MT_Function
from MT_UI import MT_UI
from Cam import cam1_process, cam2_process
import threading
from Function.DB import DB_Function
from Function.Checking_Book_Status import BookStatus

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

    mediator = ConcreteMediator(cam1_queue,cam2_queue,widget_cam_1_queue, widget_cam_2_queue, function_1_queue,function_2_queue)

    window = QMainWindow()

    mt_ui_thread = MT_UI(
        mediator=mediator,
        name="MT_UI",
        widget_cam_1_queue=widget_cam_1_queue,
        widget_cam_2_queue = widget_cam_2_queue,
        update_data_queue_1= update_data_queue_1,
        update_data_queue_2 = update_data_queue_2,
        main_ui=None  
    )
    main_ui = Ui_MainWindow(mt_ui_thread=mt_ui_thread)
    mt_ui_thread.main_ui = main_ui 
    main_ui.cam1_queue = mt_ui_thread.cam1_queue
    main_ui.cam2_queue = mt_ui_thread.cam2_queue

    db_function = DB_Function()
    book_status_1 = BookStatus(db_function, update_data_queue_1)
    book_status_2 = BookStatus(db_function, update_data_queue_2)

    mt_function_1_thread = MT_Function(mediator, "FUNCTION_1", function_1_queue, update_data_queue_1,db_function)
    mt_function_2_thread = MT_Function(mediator, "FUNCTION_2", function_2_queue, update_data_queue_2,db_function)
    
    mt_function_1_thread.checking_book_status = book_status_1
    mt_function_2_thread.checking_book_status = book_status_2


    mediator.add_user(mt_function_1_thread)
    mediator.add_user(mt_function_2_thread)
    
    mediator.add_user(mt_ui_thread)

    mt_function_1_thread.start()
    mt_function_2_thread.start()
    
    mt_ui_thread.start()

    main_ui.setupUi(window)
    main_ui.start_threads()
    window.show()

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')

    with Manager() as manager:
        cam1_queue = manager.Queue()
        cam2_queue = manager.Queue()

        widget_cam_1_queue = manager.Queue()
        widget_cam_2_queue = manager.Queue()
        
        function_1_queue = manager.Queue()
        function_2_queue = manager.Queue()
        
        update_data_queue_1 = manager.Queue()
        update_data_queue_2 = manager.Queue()

        cam1_proc = Process(target=cam1_process, args=(widget_cam_1_queue, function_1_queue))
        cam1_proc.start()

        cam2_proc = Process(target=cam2_process, args=(widget_cam_2_queue, function_2_queue))
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
            cam1_proc.join()
            cam2_proc.terminate()
            cam2_proc.join()
