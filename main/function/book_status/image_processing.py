import cv2
import numpy as np
import os

def load_image(image_path):
    """이미지 로드 및 RGB 변환"""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def predict_with_yolo(model, image, task='segment', conf=0.5, classes=[73]):
    """YOLO 모델을 사용하여 예측 수행"""
    return model.predict(image, task=task, conf=conf, classes=classes, imgsz=1280)

def calculate_iou(box1, box2):
    """두 박스 간의 IoU 계산"""
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2

    inter_x_min = max(x_min1, x_min2)
    inter_y_min = max(y_min1, y_min2)
    inter_x_max = min(x_max1, x_max2)
    inter_y_max = min(y_max1, y_max2)

    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
    area2 = (x_max2 - x_min2) * (y_max2 - y_min2)

    return inter_area / float(area1 + area2 - inter_area)

def contains(box1, box2):
    """box1이 box2를 포함하는지 확인"""
    return (box1[0] <= box2[0] and box1[1] <= box2[1] and
            box1[2] >= box2[2] and box1[3] >= box2[3])

def box_area(box):
    """박스의 면적 계산"""
    return (box[2] - box[0]) * (box[3] - box[1])

def get_exclude_indices(boxes):
    """겹치는 박스 중 제외할 인덱스 결정"""
    exclude_idxs = set()
    for i, box_i in enumerate(boxes):
        if i in exclude_idxs:
            continue
        for j, box_j in enumerate(boxes):
            if i == j or j in exclude_idxs:
                continue
            if contains(box_i, box_j):
                exclude_idxs.add(j)
            elif calculate_iou(box_i, box_j) > 0.5:
                if box_area(box_i) > box_area(box_j):
                    exclude_idxs.add(j)
                else:
                    exclude_idxs.add(i)
                    break
    return list(exclude_idxs)

def crop_and_save_image(image, mask, box, idx, output_folder):
    """마스크를 이용해 이미지 크롭 및 저장"""
    mask = (mask * 255).astype(np.uint8)
    mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
    cropped_image = cv2.bitwise_and(image, image, mask=mask_resized)

    x_min, y_min, x_max, y_max = box
    cropped_image = cropped_image[y_min:y_max, x_min:x_max]

    cropped_filename = os.path.join(output_folder, f'cropped_{idx:03d}.png')
    cv2.imwrite(cropped_filename, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
    return cropped_filename