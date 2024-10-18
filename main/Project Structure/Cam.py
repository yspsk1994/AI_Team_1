import cv2
import time

def cam1_process(ui_queue, function_queue):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    last_send_time = time.time()
    running = True

    try:
        while running:
            ret, frame = cap.read()
            if ret:
                # 프레임을 UI 큐에 추가하여 UI로 전송
                ui_queue.put(('WIDGET_CAM_1', frame.copy()))
                current_time = time.time()
                if current_time - last_send_time >= 5:
                    # 기능 큐에 프레임을 추가하여 5초마다 처리 요청
                    function_queue.put(('CAM_1_CHECK_BOOK_STATUS', frame.copy()))
                    last_send_time = current_time
            time.sleep(0.1)
    finally:
        cap.release()
        print("Camera 1 released.")

def cam2_process(ui_queue, function_queue):
    cap = cv2.VideoCapture(3)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    last_send_time = time.time()
    running = True

    try:
        while running:
            ret, frame = cap.read()
            if ret:
                # 프레임을 UI 큐에 추가하여 UI로 전송
                ui_queue.put(('WIDGET_CAM_2', frame.copy()))
                current_time = time.time()
                if current_time - last_send_time >= 5:
                    # 기능 큐에 프레임을 추가하여 5초마다 처리 요청
                    function_queue.put(('CAM_2_CHECK_BOOK_STATUS', frame.copy()))
                    last_send_time = current_time
            time.sleep(0.1)
    finally:
        cap.release()
        print("Camera 2 released.")
