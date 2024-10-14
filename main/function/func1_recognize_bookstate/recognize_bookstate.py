from ultralytics import YOLO
import cv2
from paddleocr import PaddleOCR

cv2.namedWindow('image')
timer = 0
before_person_detect_picture = None
after_person_detect_picture = None
orb = cv2.ORB_create()


def func_No_detectPerson(frame, check_person):
    global before_person_detect_picture, after_person_detect_picture
    if timer == 30:
        if check_person == True:
            after_person_detect_picture = frame
            check_person = False
            cal_differ_picture(before_person_detect_picture, after_person_detect_picture)

        else:
            before_person_detect_picture = frame
            
    return before_person_detect_picture, after_person_detect_picture

    
def cal_differ_picture(before_frame, after_frame):
    
    kp1, des1 = orb.detectAndCompute(before_frame, None)
    kp2, des2 = orb.detectAndCompute(after_frame, None)
    
    
    if des1 is None or des2 is None:
        print("디스크립터를 추출하지 못했습니다.")
        return

    if len(des1) < 2 or len(des2) < 2:
        print("디스크립터가 충분하지 않습니다.")
        return
    bf = cv2.BFMatcher(cv2.NORM_HAMMING) 
    matches = bf.knnMatch(des1, des2, k=2) 

    good_matches = []
    for m , n in matches:
        if m.distance < 0.6 * n.distance:
            good_matches.append(m)
            
    NG_kp1 = [kp1[m.queryIdx] for m,n in matches if m not in good_matches]
    NG_kp2 = [kp2[m.queryIdx] for m,n in matches if m not in good_matches]
    
    differ_frame_before = cv2.drawKeypoints(before_frame, NG_kp1, None, color=(0, 0, 255))
    differ_frame_after = cv2.drawKeypoints(after_frame, NG_kp2, None, color=(255, 0, 0))
    
    # differ_frame = cv2.drawMatches(before_frame, kp1, after_frame, kp2, good_matches, None)


   
    if(differ_frame_before is not None):
        # cv2.resizeWindow(winname='differ_frame', width=200, height=200)
        cv2.imshow("differ_frame_before", differ_frame_before)
        cv2.waitKey()
        cv2.imshow("differ_frame_after", differ_frame_after)
        cv2.waitKey()        
        # detect_ocr(differ_frame)

def detect_ocr(frame):
    frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    # cv2.resizeWindow(winname='differ_frame', width=200, height=200)
    cv2.imshow("differ_frame", frame)
    cv2.waitKey()
    ocr_results = ocr_model.ocr(frame, cls = True)
    if ocr_results is None or len(ocr_results) == 0 or ocr_results[0] is None or len(ocr_results[0]) == 0:
        print("OCR failed: No text detected")
        return ""
    text_lines = [line[1][0] for line in sorted(ocr_results[0], key=lambda x: x[0][0][0])]
    detected_text = ' '.join(text_lines)

check_person = False
check_cal = False 



model = YOLO('yolov8s.pt')
ocr_model = PaddleOCR(use_angle_cls=True, lang='korean', rec_model_dir='path/to/korean_server_v2.0_rec', use_gpu=True)

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH,640)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,480)


        
    




ret, frame = capture.read()

before_person_detect_picture = frame
after_person_detect_picture = frame

while frame is not None:
    results = model.predict(frame)
    for result in results:
        person_detections = [d for d in result.boxes.data if int(d[5]) == 0]
        timer+=1
        if person_detections :
            print("person_detect!")
            check_person = True            
            timer = 0
        elif not person_detections:
            before_person_detect_picture , after_person_detect_picture = func_No_detectPerson(frame,check_person)
        
        
        # cv2.resizeWindow(winname='image', width=200, height=200)

        cv2.imshow("image", frame)
        cv2.waitKey(100)
            
        ret, frame = capture.read()
    
    

