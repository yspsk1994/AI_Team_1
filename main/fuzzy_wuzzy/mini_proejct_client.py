import cv2
import requests
import numpy as np

# 모바일 장치의 카메라 사용 (DroidCam 또는 다른 소스 사용)
cap = cv2.VideoCapture(0)  # DroidCam은 0으로 설정 가능

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 프레임을 JPEG로 인코딩하여 서버로 전송
    _, img_encoded = cv2.imencode('.jpg', frame)
    response = requests.post('http://192.168.0.7:5000/process_frame', data=img_encoded.tobytes())

    # 서버에서 처리된 이미지를 받아서 다시 디코딩
    nparr = np.frombuffer(response.content, np.uint8)
    processed_frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # 처리된 프레임을 모바일 장치 화면에 표시
    cv2.imshow('Processed Frame', processed_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
