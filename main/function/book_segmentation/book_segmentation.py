from ultralytics import YOLO
import cv2
import numpy as np
import os
import matplotlib.pyplot as plt


##############################################모델 구성#####################################################

# 1. YOLOv8x-seg 모델 불러오기
model = YOLO('./yolo_model/yolov8x-seg.pt')

# 2. 이미지를 읽어오기
image_path = './book.jpg'  # 책 이미지 경로를 설정해주세요.
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# 3. YOLOv8을 이용해 세그멘테이션 예측
results = model.predict(image_rgb, task='segment', conf=0.5)

# 4. 마스크 결과 저장 폴더 생성 및 크롭된 결과 이미지 저장 폴더 생성
output_folder = "masks"
os.makedirs(output_folder, exist_ok=True)

cropped_folder = "cropped_images"
os.makedirs(cropped_folder, exist_ok=True)


###############################################예외처리#####################################################

# 경계 상자 정보를 가져와 포함된 상자 제외
boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)  # 경계 상자 좌표
masks = results[0].masks.data.cpu().numpy()  # 마스크 데이터

# 포함 관계를 확인하여 제외할 인덱스 리스트
exclude_idxs = []

# 각 경계 상자에 대해 포함 관계 확인
for i in range(len(boxes)):
    x_min_i, y_min_i, x_max_i, y_max_i = boxes[i]
    
    for j in range(len(boxes)):
        if i == j:  # 자기 자신과 비교하지 않음
            continue
        
        x_min_j, y_min_j, x_max_j, y_max_j = boxes[j]
        
        # j의 경계 상자가 i의 경계 상자에 완전히 포함되는지 확인
        if (x_min_i <= x_min_j and y_min_i <= y_min_j and
            x_max_i >= x_max_j and y_max_i >= y_max_j):
            # j 상자는 i 상자 안에 완전히 포함됨
            exclude_idxs.append(j)

# 제외할 인덱스 리스트 구성
exclude_idxs = list(set(exclude_idxs))


###############################################세그멘테이션에 따라 마스크 생성 및 저장#####################################################

# 5. 각 객체에 대해 마스크를 저장
for idx, result in enumerate(results[0].masks.data):
    # 제외 인덱스는 스킵
    if idx in exclude_idxs:
        continue  # 포함된 마스크는 건너뜀
    
    # 마스크를 불러와서 numpy 배열로 변환
    mask = result.cpu().numpy()

    # 마스크를 0과 255로 변환 (OpenCV로 저장하기 위해 0과 1을 0과 255로 변환)
    mask_image = (mask * 255).astype(np.uint8)

    # 마스크 이미지를 저장
    mask_filename = os.path.join(output_folder, f'mask_{idx}.png')
    cv2.imwrite(mask_filename, mask_image)

    print(f"마스크 {idx}가 {mask_filename}에 저장되었습니다.")
    

###############################################마스크 이미지에 따라 이미지 크롭#####################################################

# 7. 각 객체에 대해 마스크를 사용하여 크롭 이미지 저장
for idx, result in enumerate(results[0].masks.data):
    if idx in exclude_idxs:
        continue  # 포함된 마스크는 건너뜀
    
    # 마스크를 numpy 배열로 변환
    mask = result.cpu().numpy()

    # 마스크를 1과 0으로 변환하고, uint8 타입으로 변환
    mask = (mask * 255).astype(np.uint8)

    # 마스크의 크기가 이미지 크기와 일치하는지 확인
    mask_resized = cv2.resize(mask, (image_rgb.shape[1], image_rgb.shape[0]))

    # 마스크를 원본 이미지와 곱해 객체 영역만 추출
    cropped_image = cv2.bitwise_and(image_rgb, image_rgb, mask=mask_resized)

    # 객체의 경계 박스를 추출
    x_min, y_min, x_max, y_max = results[0].boxes.xyxy[idx].cpu().numpy().astype(int)

    # 경계 박스를 이용해 객체 크롭 (이미지의 해당 부분 자르기)
    cropped_image = cropped_image[y_min:y_max, x_min:x_max]

    # 크롭된 이미지를 저장
    cropped_filename = os.path.join(cropped_folder, f'cropped_{idx}.png')
    cv2.imwrite(cropped_filename, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))

    print(f"크롭된 이미지 {idx}가 {cropped_filename}에 저장되었습니다.")
    

###############################################결과 확인 및 화면 저장#####################################################
    
# 8. 결과 시각화 (첫 번째 결과만 시각화)
plt.figure(figsize=(10,10))

# 세그멘테이션 마스크를 포함한 이미지를 불러오기
segmented_image = results[0].plot()

plt.imshow(segmented_image)
plt.axis('off')
plt.show()

# 9. 세그멘테이션 마스크 저장
cv2.imwrite("segmented_book.jpg", segmented_image)

########################################################################################################################
