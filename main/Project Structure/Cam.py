import cv2
import time

def cam1_process(widget_cam_1_queue, function_1_queue):
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    last_send_time = time.time()
    running = True

    try:
        while running:
            ret, frame = cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (426, 240))
                widget_cam_1_queue.put(('WIDGET_CAM_1', frame_resized.copy()))
                current_time = time.time()
                if current_time - last_send_time >= 3:
                    # 기능 큐에 프레임을 추가하여 5초마다 처리 요청
                    function_1_queue.put(('FUNCTION_1_CHECK_BOOK_STATUS', frame.copy()))
                    last_send_time = current_time
            time.sleep(0.01)
    finally:
        cap.release()
        print("Camera 1 released.")
        
def cam2_process(widget_cam_2_queue, function_2_queue):
    cap = cv2.VideoCapture(2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    last_send_time = time.time()
    running = True

    try:
        while running:
            ret, frame = cap.read()
            if ret:
                frame_resized = cv2.resize(frame, (426, 240))
                widget_cam_2_queue.put(('WIDGET_CAM_2', frame_resized.copy()))
                current_time = time.time()
                if current_time - last_send_time >= 3:
                    function_2_queue.put(('FUNCTION_2_CHECK_BOOK_STATUS', frame.copy()))
                    last_send_time = current_time
            time.sleep(0.01)
    finally:
        cap.release()
        print("Camera 2 released.")
