from ultralytics import YOLO
import cv2
import numpy as np
import os
from paddleocr import PaddleOCR
import pandas as pd
from fuzzywuzzy import fuzz
import time

## 초기화 함수들

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

## 이미지 처리 함수들

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

## OCR 및 매칭 함수들

def extract_text_from_image(ocr, image_path):
    """이미지에서 텍스트 추출"""
    result = ocr.ocr(image_path, cls=True)
    extracted_text = ""

    for line in result:
        if isinstance(line, list):
            for sub_line in line:
                if isinstance(sub_line, list) and len(sub_line) == 2:
                    _, (text, confidence) = sub_line
                    extracted_text += text + "\n"
    return extracted_text.strip()

def process_cropped_image(ocr, cropped_filename, book_list):
    """크롭된 이미지에서 텍스트 추출 후 도서 목록과 매칭"""
    extracted_text = extract_text_from_image(ocr, cropped_filename)
    
    if not extracted_text:
        return []

    full_text = ' '.join(extracted_text.split())
    matches = sorted(
        [(book, fuzz.partial_ratio(full_text, book)) for book in book_list],
        key=lambda x: x[1], reverse=True
    )
    
    return matches

def load_book_list(excel_path):
    """엑셀 파일에서 도서 목록 로드"""
    df = pd.read_excel(excel_path)
    df['combined'] = df['제목'].astype(str) + ' ' + df['저자'].astype(str) + ' ' + df['출판사'].astype(str)
    return df['combined'].tolist(), df

def collect_highest_similarity_books(all_matches, book_df):
    """각 매칭 결과에서 가장 높은 유사도를 가진 도서 정보 수집"""
    highest_books = []
    for matches in all_matches:
        if matches:
            book, _ = matches[0]
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty:
                highest_books.append(book_info.iloc[0])
    return highest_books

def save_books_to_excel(books_info, excel_path='current_book_list.xlsx'):
    """도서 정보를 엑셀 파일로 저장"""
    df = pd.DataFrame(books_info)
    df.drop(columns=['combined'], inplace=True, errors='ignore')
    df.to_excel(excel_path, index=False)

## 순서 관련 함수들

def find_lis(current_order, correct_order):
    """현재 순서에서 최장 증가 부분 수열(LIS)를 찾는 함수"""
    pos_map = {book: i for i, book in enumerate(correct_order)}
    transformed_order = [pos_map.get(book, -1) for book in current_order if book in pos_map]

    lis = []
    predecessors = [-1] * len(transformed_order)
    indices = []

    for i, value in enumerate(transformed_order):
        if value == -1:
            continue
        if not lis or value > lis[-1]:
            predecessors[i] = indices[-1] if indices else -1
            lis.append(value)
            indices.append(i)
        else:
            left, right = 0, len(lis) - 1
            while left < right:
                mid = (left + right) // 2
                if lis[mid] < value:
                    left = mid + 1
                else:
                    right = mid
            lis[left] = value
            indices[left] = i
            predecessors[i] = indices[left - 1] if left > 0 else -1

    lis_books = []
    k = indices[-1] if indices else -1
    while k >= 0:
        lis_books.append(current_order[k])
        k = predecessors[k]

    return lis_books[::-1]

def find_books_to_move(current_order, lis_books):
    """현재 순서에서 이동해야 할 책을 찾는 함수"""
    lis_set = set(lis_books)
    return [book for book in current_order if book not in lis_set]

## 상태 업데이트 함수

def update_book_status(current_books, previous_books, book_df, excel_path):
    """책 상태 업데이트 및 엑셀 파일 저장"""
    updated = False

    # 사라진 책 처리: '읽는중'으로 변경
    for book in previous_books:
        if book not in current_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] not in ['대출중', '오배치']:
                book_df.loc[book_df['combined'] == book, '도서상태'] = '읽는중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '읽는중'으로 변경되었습니다.")
                updated = True

    # 새로 나타난 책 처리: '배치중'으로 변경
    for book in current_books:
        if book not in previous_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] in ['읽는중']:
                book_df.loc[book_df['combined'] == book, '도서상태'] = '배치중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '배치중'으로 변경되었습니다.")
                updated = True

    # 오배치된 책 처리
    correct_order = book_df['combined'].tolist()
    current_order = [book for book in current_books if book in correct_order]

    lis_books = find_lis(current_order, correct_order)
    books_to_move = find_books_to_move(current_order, lis_books)

    for combined in books_to_move:
        book_info = book_df[book_df['combined'] == combined]
        if not book_info.empty and book_info['도서상태'].iloc[0] not in ['대출중', '오배치']:
            book_df.loc[book_df['combined'] == combined, '도서상태'] = '오배치'
            print(f"'{book_info['제목'].iloc[0]}' 상태가 '오배치'로 변경되었습니다.")
            updated = True

    # 오배치 상태였던 책이 제대로 배치된 경우 '배치중'으로 변경
    for book in current_books:
        if book in previous_books and book not in books_to_move:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] == '오배치':
                book_df.loc[book_df['combined'] == book, '도서상태'] = '배치중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '배치중'으로 변경되었습니다.")
                updated = True

    if updated:
        # 'combined' 열 제거 후 엑셀 파일 저장
        save_df = book_df.drop(columns=['combined'])
        save_df.to_excel(excel_path, index=False)
        print(f"'{excel_path}'에 업데이트된 도서 목록이 저장되었습니다.")
        print(f"오배치된 책의 수: {len(books_to_move)}")

    return book_df

## 메인 함수

def main():
    CROPPED_FOLDER = "cropped_images"
    DET_MODEL_DIR = '../../model/PaddleOCR/model/detection'
    REC_MODEL_DIR = '../../model/PaddleOCR/model/my_recognition/v3_ft_word'
    EXCEL_PATH = 'total_book_list.xlsx'
    PROCESS_INTERVAL = 5  # 5초 간격으로 처리

    try:
        yolo_model = initialize_yolo()
        ocr = initialize_ocr(DET_MODEL_DIR, REC_MODEL_DIR)
        os.makedirs(CROPPED_FOLDER, exist_ok=True)

        book_list, book_df = load_book_list(EXCEL_PATH)
        cap = initialize_webcam()

        last_process_time = time.time()
        previous_books = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            current_time = time.time()

            cv2.namedWindow('Library CAM', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Library CAM', 640, 480)
            cv2.imshow('Library CAM', frame)

            if current_time - last_process_time >= PROCESS_INTERVAL:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = predict_with_yolo(yolo_model, frame_rgb)

                if len(results[0].boxes) == 0:
                    last_process_time = current_time
                    continue

                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                masks = results[0].masks.data.cpu().numpy()

                exclude_idxs = get_exclude_indices(boxes)
                sorted_indices = sorted(range(len(boxes)), key=lambda i: boxes[i][0])

                all_matches = []
                for idx, sorted_idx in enumerate(sorted_indices):
                    if sorted_idx in exclude_idxs:
                        continue

                    mask = masks[sorted_idx]
                    box = boxes[sorted_idx]
                    cropped_filename = crop_and_save_image(frame_rgb, mask, box, idx, CROPPED_FOLDER)
                    matches = process_cropped_image(ocr, cropped_filename, book_list)
                    all_matches.append(matches)

                highest_books = collect_highest_similarity_books(all_matches, book_df)
                
                current_books = [book['combined'] for book in highest_books]
                
                book_df = update_book_status(current_books, previous_books, book_df, EXCEL_PATH)
                
                previous_books = current_books

                save_books_to_excel(highest_books, 'current_book_list.xlsx')

                last_process_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()