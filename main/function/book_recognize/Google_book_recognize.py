from ultralytics import YOLO
import cv2
import numpy as np
import os
import requests
import re
import xmltodict
from paddleocr import PaddleOCR
import io
from google.cloud import vision

def initialize_yolo():
    return YOLO('yolov8x-seg.pt')

def initialize_ocr(det_model_dir, rec_model_dir, lang='korean'):
    return PaddleOCR(
        det_model_dir=det_model_dir,
        rec_model_dir=rec_model_dir,
        use_angle_cls=True,
        lang=lang
    )

def load_image(image_path):
    image = cv2.imread(image_path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def predict_with_yolo(model, image):
    return model.predict(image, task='segment', conf=0.5)

def get_exclude_indices(boxes):
    exclude_idxs = []
    for i in range(len(boxes)):
        x_min_i, y_min_i, x_max_i, y_max_i = boxes[i]
        for j in range(len(boxes)):
            if i == j:
                continue
            x_min_j, y_min_j, x_max_j, y_max_j = boxes[j]
            if (x_min_i <= x_min_j and y_min_i <= y_min_j and
                x_max_i >= x_max_j and y_max_i >= y_max_j):
                exclude_idxs.append(j)
    return list(set(exclude_idxs))

# def crop_and_save_image(image, mask, box, idx, output_folder):
#     mask = (mask * 255).astype(np.uint8)
#     mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
#     cropped_image = cv2.bitwise_and(image, image, mask=mask_resized)

#     x_min, y_min, x_max, y_max = box
#     cropped_image = cropped_image[y_min:y_max, x_min:x_max]

#     cropped_filename = os.path.join(output_folder, f'cropped_{idx}.png')
#     cv2.imwrite(cropped_filename, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
#     print(f"크롭된 이미지 {idx}가 {cropped_filename}에 저장되었습니다.")
#     return cropped_filename

def crop_and_save_image(image, mask, box, save_idx, output_folder):
    mask = (mask * 255).astype(np.uint8)
    mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
    cropped_image = cv2.bitwise_and(image, image, mask=mask_resized)

    x_min, y_min, x_max, y_max = box
    cropped_image = cropped_image[y_min:y_max, x_min:x_max]

    cropped_filename = os.path.join(output_folder, f'cropped_{save_idx}.png')
    cv2.imwrite(cropped_filename, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
    print(f"크롭된 이미지 {save_idx}가 {cropped_filename}에 저장되었습니다.")
    return cropped_filename

# # paddleocr를 통해 이미지에서 텍스트 추출
# def extract_text_from_image(ocr, image_path):
#     result = ocr.ocr(image_path, cls=True)
#     extracted_text = ""

#     for idx, line in enumerate(result):
#         if isinstance(line, list) and len(line) > 0:
#             for sub_line in line:
#                 if isinstance(sub_line, list) and len(sub_line) == 2:
#                     _, (text, confidence) = sub_line
#                     print(f"인식된 텍스트: {text} (신뢰도: {confidence:.2f})")
#                     extracted_text += text + "\n"
#         else:
#             print(f"Unexpected structure in line {idx}")
    
#     return extracted_text.strip()

# Google Vision API를 통해 이미지에서 텍스트 추출
def extract_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description.strip()
    else:
        return None


# def search_book_on_aladin(query, ttb_key):
#     url = "http://www.aladin.co.kr/ttb/api/ItemSearch.aspx"
#     params = {
#         "TTBKey": ttb_key,
#         "Query": query,
#         "QueryType": "Keyword",
#         "MaxResults": 10,
#         "start": 1,
#         "SearchTarget": "Book",
#         "output": "xml",
#         "Version": "20131101"
#     }
    
#     response = requests.get(url, params=params)
    
#     if response.status_code == 200:
#         result = xmltodict.parse(response.content)
#         items = result['object'].get('item', [])
#         if isinstance(items, dict):
#             items = [items]
#         return items if items else None
#     else:
#         print(f"Error: {response.status_code}")
#         return None

# def calculate_relevance_score(book_title, search_term):
#     if search_term.lower() in book_title.lower():
#         return len(search_term)
#     return 0

# def find_best_book_match(extracted_text, ttb_key):
#     lines = extracted_text.splitlines()
#     best_book = None
#     best_score = 0
    
#     for line in lines:
#         if not line:
#             continue
#         print(f"검색 중: {line}")
#         book_info = search_book_on_aladin(line.strip(), ttb_key)
        
#         if book_info:
#             for book in book_info:
#                 score = calculate_relevance_score(book.get('title', ''), line)
#                 if score > best_score:
#                     best_score = score
#                     best_book = book
    
#     return best_book

# def print_book_info(book):
#     if book:
#         print("\n가장 일치하는 도서 정보:")
#         print(f"제목: {book.get('title', '정보 없음')}")
#         print(f"저자: {book.get('author', '정보 없음')}")
#         print(f"출판사: {book.get('publisher', '정보 없음')}")
#         print(f"출판일: {book.get('pubDate', '정보 없음')}")
#         print(f"링크: {book.get('link', '정보 없음')}")
#     else:
#         print("알라딘 API에서 적합한 도서를 찾지 못했습니다.")

# def process_cropped_image(ocr, cropped_filename, ttb_key):
#     extracted_text = extract_text_from_image(ocr, cropped_filename)
    
#     if extracted_text:
#         extracted_text = re.sub(r'[^-!~\w\s]', '\n', extracted_text)
#         print(f"\n추출된 텍스트: {extracted_text}")   
        
#         # best_book = find_best_book_match(extracted_text, ttb_key)
#         # print_book_info(best_book)
#     else:
#         print("이미지에서 텍스트를 감지하지 못했습니다.")

# #Paddle OCR
# def process_cropped_image(ocr, cropped_filename, ttb_key):
#     extracted_text = extract_text_from_image(ocr, cropped_filename)
    
#     with open('recognized_text.txt', 'a', encoding='utf-8') as f:
#         if extracted_text:
#             # 텍스트를 쉼표로 구분하여 저장
#             extracted_text = re.sub(r'[^-!,~\w\s]', '\n', extracted_text)
#             recognized_lines = extracted_text.splitlines()
#             for line in recognized_lines:
#                 if line.strip():  # 빈 줄이 아닌 경우
#                     f.write(line.strip() + ', ')  # 쉼표로 구분하여 작성
#             f.write('\n')  # 다른 책은 줄바꿈으로 구분
#         else:
#             f.write('\n')  # 감지되지 않으면 빈 줄 추가
#             print("이미지에서 텍스트를 감지하지 못했습니다.")

#Google Vision
def process_cropped_image(image_path):
    extracted_text = extract_text_from_image(image_path)

    with open('recognized_text.txt', 'a', encoding='utf-8') as f:
        if extracted_text:
            # 텍스트를 쉼표로 구분하여 저장
            extracted_text = re.sub(r'[^-!,~\w\s]', '\n', extracted_text)
            recognized_lines = extracted_text.splitlines()
            for line in recognized_lines:
                if line.strip():  # 빈 줄이 아닌 경우
                    f.write(line.strip() + ', ')  # 쉼표로 구분하여 작성
            f.write('\n')  # 다른 책은 줄바꿈으로 구분
        else:
            f.write('\n')  # 감지되지 않으면 빈 줄 추가
            print("이미지에서 텍스트를 감지하지 못했습니다.")


def calculate_iou(box1, box2):
    x_min1, y_min1, x_max1, y_max1 = box1
    x_min2, y_min2, x_max2, y_max2 = box2

    # 교차 영역 계산
    inter_x_min = max(x_min1, x_min2)
    inter_y_min = max(y_min1, y_min2)
    inter_x_max = min(x_max1, x_max2)
    inter_y_max = min(y_max1, y_max2)

    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

    # 각 박스의 영역 계산
    area1 = (x_max1 - x_min1) * (y_max1 - y_min1)
    area2 = (x_max2 - x_min2) * (y_max2 - y_min2)

    # IoU 계산
    iou = inter_area / float(area1 + area2 - inter_area)
    return iou

def get_exclude_indices_based_on_iou(boxes):
    exclude_idxs = set()
    for i in range(len(boxes)):
        if i in exclude_idxs:
            continue
        for j in range(i + 1, len(boxes)):
            if j in exclude_idxs:
                continue
            iou = calculate_iou(boxes[i], boxes[j])
            if iou > 0.5:
                # 큰 박스 선택
                area_i = (boxes[i][2] - boxes[i][0]) * (boxes[i][3] - boxes[i][1])
                area_j = (boxes[j][2] - boxes[j][0]) * (boxes[j][3] - boxes[j][1])
                if area_i > area_j:
                    exclude_idxs.add(j)
                else:
                    exclude_idxs.add(i)
                    break
    return list(exclude_idxs)

def main():
    # 설정
    IMAGE_PATH = 'book.jpg'
    CROPPED_FOLDER = "cropped_images"
    DET_MODEL_DIR = '../ocr_model/detection'
    REC_MODEL_DIR = '../ocr_model/my_recognition/v3_ft_word'
    TTB_KEY = "ttbradon992330001"

    # 초기화
    yolo_model = initialize_yolo()
    ocr = initialize_ocr(DET_MODEL_DIR, REC_MODEL_DIR)
    os.makedirs(CROPPED_FOLDER, exist_ok=True)

    # 이미지 로드 및 YOLO 예측
    image = load_image(IMAGE_PATH)
    results = predict_with_yolo(yolo_model, image)

    # 경계 상자 정보 가져오기
    boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
    masks = results[0].masks.data.cpu().numpy()

    # 포함 관계 및 IoU 기반 제외 인덱스 확인
    exclude_idxs_by_containment = get_exclude_indices(boxes)
    exclude_idxs_by_iou = get_exclude_indices_based_on_iou(boxes)
    
    exclude_idxs = set(exclude_idxs_by_containment).union(exclude_idxs_by_iou)

    # 경계 상자를 x_min 값을 기준으로 정렬
    sorted_indices = sorted(range(len(boxes)), key=lambda i: boxes[i][0])

    # 각 객체에 대해 처리 (왼쪽에서 오른쪽으로)
    save_idx = 0
    for idx in sorted_indices:
        if idx in exclude_idxs:
            continue

        mask = masks[idx]
        box = boxes[idx]
        cropped_filename = crop_and_save_image(image, mask, box, save_idx, CROPPED_FOLDER)
        #process_cropped_image(ocr, cropped_filename, TTB_KEY)
        process_cropped_image(cropped_filename)
        save_idx += 1

if __name__ == "__main__":
    main()
