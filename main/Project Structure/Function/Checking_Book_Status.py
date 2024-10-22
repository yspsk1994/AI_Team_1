import threading
from DB import DB_Function
import queue
import cv2
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np
import paddle
from ultralytics import YOLO
from paddleocr import PaddleOCR
import gc
import traceback

# 모델 경로 설정
DET_MODEL_DIR = 'model/PaddleOCR/detection'
REC_MODEL_DIR = 'model/PaddleOCR/my_recognition/v3_ft_word'
EXCEL_PATH = 'data/total_book_list.xlsx'
paddle.disable_signal_handler()


class BookStatus(DB_Function):
    def __init__(self, db_function, update_data_queue):
        self.update_data_queue = update_data_queue
        self.yolo_model = self.initialize_yolo()
        self.ocr = self.initialize_ocr(DET_MODEL_DIR, REC_MODEL_DIR)
        self.book_list_cache = None  
        self.book_df_cache = None
        self.db_function = db_function
        
    def find_lis(self,current_order, correct_order):
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

    def find_books_to_move(self,current_order, lis_books):
        """현재 순서에서 이동해야 할 책을 찾는 함수"""
        lis_set = set(lis_books)
        return [book for book in current_order if book not in lis_set]
    def update_book_status(self,current_books, book_df, excel_path):
        """현재 책 상태만을 기반으로 책 상태 업데이트 및 엑셀 파일 저장"""
        updated = False
        
        # 오배치된 책 처리
        correct_order = book_df['combined'].tolist()
        current_order = [book for book in current_books if book in correct_order]

        lis_books = self.find_lis(current_order, correct_order)
        books_to_move = self.find_books_to_move(current_order, lis_books)

        # 현재 책 목록에 있는 책을 '배치중'으로 변경
        for book in current_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] != '대출중' and book_info['도서상태'].iloc[0] != '배치중':
                book_df.loc[book_df['combined'] == book, '도서상태'] = '배치중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '배치중'으로 변경되었습니다.")
                updated = True
        
        for combined in books_to_move:
            book_info = book_df[book_df['combined'] == combined]
            if not book_info.empty and book_info['도서상태'].iloc[0] != '대출중' and book_info['도서상태'].iloc[0] != '오배치':
                book_df.loc[book_df['combined'] == combined, '도서상태'] = '오배치'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '오배치'로 변경되었습니다.")
                updated = True

        # 현재 책 목록에 없는 책은 '읽는중'으로 변경
        missing_books = set(book_df['combined']) - set(current_books)
        for book in missing_books:
            book_info = book_df[book_df['combined'] == book]
            if not book_info.empty and book_info['도서상태'].iloc[0] != '대출중' and book_info['도서상태'].iloc[0] != '읽는중':
                book_df.loc[book_df['combined'] == book, '도서상태'] = '읽는중'
                print(f"'{book_info['제목'].iloc[0]}' 상태가 '읽는중'으로 변경되었습니다.")
                updated = True

        if updated:
            # 'combined' 열 제거 후 엑셀 파일 저장
            save_df = book_df.drop(columns=['combined'])
            save_df.to_excel(excel_path, index=False)
            print(f"'{excel_path}'에 업데이트된 도서 목록이 저장되었습니다.")
            print(f"오배치된 책의 수: {len(books_to_move)}")
            print(f"읽는중인 책의 수: {len(missing_books)}")

        return book_df

    def extract_text_from_image(self, image):
        extracted_text = ""  # 초기값 설정
        try:
            result = self.ocr.ocr(image, cls=True)
        except Exception as e:
            print(f"OCR 처리 중 오류 발생: {e}")
            traceback.print_exc()  # 스택 트레이스 출력
            return extracted_text  # 빈 문자열 반환
        
        for line in result:
            if isinstance(line, list):
                for sub_line in line:
                    if isinstance(sub_line, list) and len(sub_line) == 2:
                        _, (text, confidence) = sub_line
                        extracted_text += text + "\n"
        
        del result
        gc.collect()
        return extracted_text.strip()

    def process_cropped_image(self, cropped_image, book_list):
        extracted_text = self.extract_text_from_image(cropped_image)
        if not extracted_text:
            return []

        full_text = ' '.join(extracted_text.split())
        matches = sorted(
            [(book, fuzz.partial_ratio(full_text, book)) for book in book_list],
            key=lambda x: x[1], reverse=True
        )
        return matches

    def load_book_list(self, excel_path):
        if self.book_list_cache is not None and self.book_df_cache is not None:
            return self.book_list_cache, self.book_df_cache

        df = pd.read_excel(excel_path)
        df['combined'] = df['제목'].astype(str) + ' ' + df['저자'].astype(str) + ' ' + df['출판사'].astype(str)
        self.book_list_cache = df['combined'].tolist()
        self.book_df_cache = df
        return self.book_list_cache, self.book_df_cache

    def collect_highest_similarity_books(self, all_matches, book_df):
        highest_books = []
        for matches in all_matches:
            if matches:
                book, _ = matches[0]
                book_info = book_df[book_df['combined'] == book]
                if not book_info.empty:
                    highest_books.append(book_info.iloc[0])
        return highest_books

    def predict_with_yolo(self, model, image, task='segment', conf=0.5, classes=[0]):
        try:
            return model.predict(image, task=task, conf=conf, classes=classes, imgsz=1280)
        except Exception as e:
            print(f"YOLO 예측 중 오류 발생: {e}")
            traceback.print_exc()
            return None
    
    def calculate_iou(self,box1, box2):
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
   
    def remove_overlap(self,masks, boxes):
        """면적 큰 마스크에서 겹치는 영역 제거"""
        n = len(boxes)
        for i in range(n):
            for j in range(i+1, n):
                if self.calculate_iou(boxes[i], boxes[j]) > 0.5:
                    if self.box_area(boxes[i]) > self.box_area(boxes[j]):
                        larger, smaller = i, j
                    else:
                        larger, smaller = j, i
                    
                    overlap = self.get_overlap_area(boxes[larger], boxes[smaller])
                    if overlap > 0:
                        x_min = max(boxes[larger][0], boxes[smaller][0])
                        y_min = max(boxes[larger][1], boxes[smaller][1])
                        x_max = min(boxes[larger][2], boxes[smaller][2])
                        y_max = min(boxes[larger][3], boxes[smaller][3])
                        
                        masks[larger][y_min:y_max, x_min:x_max] = 0
        
        return masks
    
    def sort_boxes_and_masks(self,boxes, masks):
        sorted_indices = sorted(range(len(boxes)), key=lambda i: boxes[i][0])
        sorted_boxes = [boxes[i] for i in sorted_indices]
        sorted_masks = [masks[i] for i in sorted_indices]
        return sorted_boxes, sorted_masks, sorted_indices    

    def contains(self,box1, box2):
        return (box1[0] <= box2[0] and box1[1] <= box2[1] and
                box1[2] >= box2[2] and box1[3] >= box2[3])
        
    def process_boxes_and_masks(self, boxes, masks):
        sorted_boxes, sorted_masks, sorted_indices = self.sort_boxes_and_masks(boxes, masks)
        
        exclude_idxs = set()
        for i, box_i in enumerate(sorted_boxes):
            if i in exclude_idxs:
                continue
            for j, box_j in enumerate(sorted_boxes):
                if i == j or j in exclude_idxs:
                    continue
                if self.contains(box_i, box_j):
                    exclude_idxs.add(j)
        
        valid_indices = [i for i in range(len(sorted_boxes)) if i not in exclude_idxs]
        valid_boxes = [sorted_boxes[i] for i in valid_indices]
        valid_masks = [sorted_masks[i] for i in valid_indices]
        
        updated_masks = self.remove_overlap(valid_masks, valid_boxes)
        
        original_indices = [sorted_indices[i] for i in valid_indices]
        
        return valid_boxes, updated_masks, original_indices

    def contains(self, box1, box2):
        return (box1[0] <= box2[0] and box1[1] <= box2[1] and
                box1[2] >= box2[2] and box1[3] >= box2[3])

    def crop_image(self, image, mask, box):
        mask = (mask * 255).astype(np.uint8)
        mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))
        cropped_image = cv2.bitwise_and(image, image, mask=mask_resized)

        x_min, y_min, x_max, y_max = box
        cropped_image = cropped_image[y_min:y_max, x_min:x_max]

        gray = cv2.cvtColor(cropped_image, cv2.COLOR_RGB2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            new_mask = np.zeros(gray.shape, np.uint8)
            cv2.drawContours(new_mask, [largest_contour], 0, 255, -1)
            result = cv2.bitwise_and(cropped_image, cropped_image, mask=new_mask)
        else:
            result = cropped_image

        return result

    def initialize_yolo(self, model_path='model/yolo/yolo_trainv2.pt',imgsz=1280):
        return YOLO(model_path)

    def initialize_ocr(self, det_model_dir, rec_model_dir, lang='korean', show_log=False):
        return PaddleOCR(
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
            use_angle_cls=True,
            lang=lang,
            gpu = True,
            show_log=show_log
        )

    def load_book_list_from_db(self):
        connection = self.db_function.connect_to_db()
        if connection is None:
            return [], None

        cursor = connection.cursor()
        sql = "SELECT 제목, 저자, 출판사, 도서상태 FROM bookcase1"
        cursor.execute(sql)
        results = cursor.fetchall()

        df = pd.DataFrame(results, columns=['제목', '저자', '출판사', '도서상태'])
        df['combined'] = df['제목'].astype(str) + ' ' + df['저자'].astype(str) + ' ' + df['출판사'].astype(str) + ' ' + df['도서상태'].astype(str)
        
        book_list = df['combined'].tolist()
        cursor.close()
        connection.close()

        return book_list, df

    def Do_Process(self, frame):
        try:
            book_list, book_df = self.load_book_list_from_db()
            previous_books = []
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = self.predict_with_yolo(self.yolo_model, frame_rgb)

            if results and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                masks = results[0].masks.data.cpu().numpy() if results[0].masks is not None else None

                if masks is not None:
                    valid_boxes, valid_masks, valid_indices = self.process_boxes_and_masks(boxes, masks)
                else:
                    valid_boxes, valid_indices = boxes, list(range(len(boxes)))
                    valid_masks = [None] * len(valid_boxes)

                all_matches = []
                for idx, (box, mask) in enumerate(zip(valid_boxes, valid_masks)):
                    cropped_image = self.crop_image(frame_rgb, mask, box)
                    matches = self.process_cropped_image(cropped_image, book_list)
                    all_matches.append(matches)

                # 가장 유사한 책 정보 수집
                highest_books = self.collect_highest_similarity_books(all_matches, book_df)
                # current_books = [book['combined'] for book in highest_books]
                # book_df = self.update_book_status(current_books, book_df, EXCEL_PATH)
                self.update_data_queue.put(('UPDATE_BOOK_LIST', highest_books))
                # self.save_books_to_excel(highest_books, 'data/current_book_list.xlsx')
                print("put update book list.")
            else:
                print("감지된 객체가 없습니다.")

        except Exception as e:
            print(f"오류 발생: {e}")
            traceback.print_exc()
