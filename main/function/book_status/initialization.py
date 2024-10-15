from ultralytics import YOLO
from paddleocr import PaddleOCR
import cv2

def initialize_yolo(model_path='../../model/yolo/yolov8x-seg.pt'):
    """YOLO 모델 초기화"""
    return YOLO(model_path)

def initialize_ocr(det_model_dir, rec_model_dir, lang='korean', show_log=False):
    """OCR 모델 초기화"""
    return PaddleOCR(
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        use_angle_cls=True,
        lang=lang,
        show_log=show_log
    )

def initialize_webcam(camera_index=0):
    """웹캠 초기화"""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise IOError("웹캠을 열 수 없습니다.")
    
    # 해상도 설정
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # 1920x1080 해상도
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    return cap