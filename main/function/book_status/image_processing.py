import cv2
import numpy as np
import os

def load_image(image_path):
    """이미지 로드 및 RGB 변환"""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"이미지를 찾을 수 없습니다: {image_path}")
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def predict_with_yolo(model, image, task='segment', conf=0.5, classes=[0]):
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

def get_overlap_area(box1, box2):
    """두 박스의 겹치는 영역 계산"""
    x_min = max(box1[0], box2[0])
    y_min = max(box1[1], box2[1])
    x_max = min(box1[2], box2[2])
    y_max = min(box1[3], box2[3])
    
    if x_min < x_max and y_min < y_max:
        return (x_max - x_min) * (y_max - y_min)
    return 0

def remove_overlap(masks, boxes):
    """면적 큰 마스크에서 겹치는 영역 제거"""
    n = len(boxes)
    for i in range(n):
        for j in range(i+1, n):
            if calculate_iou(boxes[i], boxes[j]) > 0.5:
                if box_area(boxes[i]) > box_area(boxes[j]):
                    larger, smaller = i, j
                else:
                    larger, smaller = j, i
                
                overlap = get_overlap_area(boxes[larger], boxes[smaller])
                if overlap > 0:
                    x_min = max(boxes[larger][0], boxes[smaller][0])
                    y_min = max(boxes[larger][1], boxes[smaller][1])
                    x_max = min(boxes[larger][2], boxes[smaller][2])
                    y_max = min(boxes[larger][3], boxes[smaller][3])
                    
                    masks[larger][y_min:y_max, x_min:x_max] = 0
    
    return masks
                    
def sort_boxes_and_masks(boxes, masks):
    """박스를 왼쪽에서 오른쪽 순으로 정렬하고 동일하게 마스크도 정렬한다."""
    sorted_indices = sorted(range(len(boxes)), key=lambda i: boxes[i][0])  # 박스의 왼쪽 x 좌표로 정렬
    sorted_boxes = [boxes[i] for i in sorted_indices]
    sorted_masks = [masks[i] for i in sorted_indices]
    return sorted_boxes, sorted_masks, sorted_indices

def process_boxes_and_masks(boxes, masks):
    """박스와 마스크 처리"""
    # 박스와 마스크를 왼쪽에서 오른쪽으로 정렬
    sorted_boxes, sorted_masks, sorted_indices = sort_boxes_and_masks(boxes, masks)
    
    exclude_idxs = set()
    for i, box_i in enumerate(sorted_boxes):
        if i in exclude_idxs:
            continue
        for j, box_j in enumerate(sorted_boxes):
            if i == j or j in exclude_idxs:
                continue
            if contains(box_i, box_j):
                exclude_idxs.add(j)
    
    valid_indices = [i for i in range(len(sorted_boxes)) if i not in exclude_idxs]
    valid_boxes = [sorted_boxes[i] for i in valid_indices]
    valid_masks = [sorted_masks[i] for i in valid_indices]
    
    updated_masks = remove_overlap(valid_masks, valid_boxes)
    
    # 원래 인덱스로 변환
    original_indices = [sorted_indices[i] for i in valid_indices]
    
    return valid_boxes, updated_masks, original_indices

def crop_and_save_image(image, mask, box, idx, output_folder):
    """마스크를 이용해 이미지 크롭 및 저장, 가장 큰 윤곽선만 남김"""
    mask = (mask * 255).astype(np.uint8)
    mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
    cropped_image = cv2.bitwise_and(image, image, mask=mask_resized)

    x_min, y_min, x_max, y_max = box
    cropped_image = cropped_image[y_min:y_max, x_min:x_max]

    # 그레이스케일로 변환
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2GRAY)

    # 이진화
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # 윤곽선 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 가장 큰 윤곽선 선택
        largest_contour = max(contours, key=cv2.contourArea)

        # 새로운 마스크 생성
        new_mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(new_mask, [largest_contour], 0, 255, -1)

        # 새로운 마스크 적용
        result = cv2.bitwise_and(cropped_image, cropped_image, mask=new_mask)
    else:
        # 윤곽선이 없는 경우 원본 이미지 사용
        result = cropped_image

    cropped_filename = os.path.join(output_folder, f'cropped_{idx:03d}.png')
    cv2.imwrite(cropped_filename, cv2.cvtColor(result, cv2.COLOR_RGB2BGR))
    
    return cropped_filename