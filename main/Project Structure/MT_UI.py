import threading
import queue
from PyQt6 import QtCore

class MT_UI(threading.Thread):
    def __init__(self, mediator, name, widget_cam_1_queue,widget_cam_2_queue, update_data_queue_1, update_data_queue_2, main_ui):
        super().__init__()
        self.mediator = mediator
        self.name = name
        self.widget_cam_1_queue = widget_cam_1_queue
        self.widget_cam_2_queue = widget_cam_2_queue
        self.update_data_queue_1 = update_data_queue_1
        self.update_data_queue_2 = update_data_queue_2
        
        self.main_ui = main_ui 
        self.running = True
        self.cam1_queue = queue.Queue(maxsize=15)
        self.cam2_queue = queue.Queue(maxsize=15)

    def run(self):
        ui_thread = threading.Thread(target=self.process_widget_cam_1_queue)
        ui_thread.start()

        ui_thread_2 = threading.Thread(target=self.process_widget_cam_2_queue)
        ui_thread_2.start()
        
        update_data_queue_1_thread = threading.Thread(target=self.process_data_queue_1)
        update_data_queue_1_thread.start()

        update_data_queue_2_thread = threading.Thread(target=self.process_data_queue_2)
        update_data_queue_2_thread.start()

        ui_thread.join()
        update_data_queue_1_thread.join()
        update_data_queue_2_thread.join()

    def process_widget_cam_1_queue(self):
        while self.running:
            try:
                target, frame = self.widget_cam_1_queue.get()
                if target == 'WIDGET_CAM_1':
                    self.cam1_queue.put(frame)
            except Exception as e:
                print(f"Error processing UI queue: {e}")

    def process_widget_cam_2_queue(self):
        while self.running:
            try:
                target, frame = self.widget_cam_2_queue.get()  
                if target == 'WIDGET_CAM_2':
                    self.cam2_queue.put(frame)
            except Exception as e:
                print(f"Error processing UI queue: {e}")
                
    def process_data_queue_1(self):
        while self.running:
            try:
                message_type, data = self.update_data_queue_1.get()  
                if message_type == "UPDATE_BOOK_LIST":
                    QtCore.QMetaObject.invokeMethod(
                        self.main_ui,
                        "update_book_list_1",
                        QtCore.Qt.ConnectionType.QueuedConnection,
                        QtCore.Q_ARG(object, data)
                    )
            except Exception as e:
                print(f"Error processing data queue: {e}")
                
    def process_data_queue_2(self):
        while self.running:
            try:
                message_type, data = self.update_data_queue_2.get()  
                if message_type == "UPDATE_BOOK_LIST":
                    QtCore.QMetaObject.invokeMethod(
                        self.main_ui,
                        "update_book_list_2",
                        QtCore.Qt.ConnectionType.QueuedConnection,
                        QtCore.Q_ARG(object, data)
                    )
            except Exception as e:
                print(f"Error processing data queue: {e}")
    def stop(self):
        self.running = False
    def set_mediator(self, mediator):
        self._mediator = mediator