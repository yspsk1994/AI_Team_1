import threading
from DB import DB_Function
import queue
import cv2
import pandas as pd
from fuzzywuzzy import fuzz
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR

DET_MODEL_DIR = 'model/PaddleOCR/detection'
REC_MODEL_DIR = 'model/PaddleOCR/my_recognition/v3_ft_word'
EXCEL_PATH = 'data/total_book_list.xlsx'

class BookStatus(DB_Function):
    def __init__(self, db_function,update_data_queue):
        self.update_data_queue = update_data_queue
        self.yolo_model = self.initialize_yolo()
        self.ocr = self.initialize_ocr(DET_MODEL_DIR, REC_MODEL_DIR)
        self.book_list_cache = None  
        self.book_df_cache = None
        self.db_function = db_function
    def update_book_status(self, current_books, previous_books, book_df, excel_path):
        pass

    def extract_text_from_image(self, image):
        result = self.ocr.ocr(image, cls=True)
        extracted_text = ""

        for line in result:
            if isinstance(line, list):
                for sub_line in line:
                    if isinstance(sub_line, list) and len(sub_line) == 2:
                        _, (text, confidence) = sub_line
                        extracted_text += text + "\n"
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
        return model.predict(image, task=task, conf=conf, classes=classes, imgsz=1280)

    def process_boxes_and_masks(self, boxes, masks):
        sorted_indices = sorted(range(len(boxes)), key=lambda i: boxes[i][0])
        sorted_boxes = [boxes[i] for i in sorted_indices]
        sorted_masks = [masks[i] for i in sorted_indices]

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

        return valid_boxes, valid_masks, valid_indices

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

    def initialize_yolo(self, model_path='model/yolo/yolo_trainv2.pt'):
        return YOLO(model_path)

    def initialize_ocr(self, det_model_dir, rec_model_dir, lang='korean', show_log=False):
        return PaddleOCR(
            det_model_dir=det_model_dir,
            rec_model_dir=rec_model_dir,
            use_angle_cls=True,
            lang=lang,
            show_log=show_log
        )

    def load_book_list_from_db(self):
        # DB 연결 및 데이터 가져오기
        connection = self.db_function.connect_to_db()
        if connection is None:
            return [], None

        cursor = connection.cursor()
        sql = "SELECT 제목, 저자, 출판사, 도서상태  FROM bookcase1"
        
        
        cursor.execute(sql)
        results = cursor.fetchall()

        # 데이터프레임 및 리스트로 변환
        df = pd.DataFrame(results, columns=['제목', '저자', '출판사','도서상태'])
        df['combined'] = df['제목'].astype(str) + ' ' + df['저자'].astype(str) + ' ' + df['출판사'].astype(str) + ' ' + df['도서상태'].astype(str)
        
        book_list = df['combined'].tolist()
        cursor.close()
        connection.close()

        return book_list, df
    
    def Do_Process(self, frame):
        try:
            book_list, book_df = self.load_book_list_from_db()

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.predict_with_yolo(self.yolo_model, frame_rgb)

            if results and len(results) > 0 and results[0].boxes is not None and len(results[0].boxes) > 0:
                boxes = results[0].boxes.xyxy.cpu().numpy().astype(int)
                masks = results[0].masks.data.cpu().numpy() if results[0].masks is not None else None

                if masks is not None:
                    valid_boxes, valid_masks, _ = self.process_boxes_and_masks(boxes, masks)
                else:
                    valid_boxes = boxes
                    valid_masks = [None] * len(valid_boxes)

                all_matches = []
                for idx, (box, mask) in enumerate(zip(valid_boxes, valid_masks)):
                    cropped_image = self.crop_image(frame_rgb, mask, box)
                    matches = self.process_cropped_image(cropped_image, book_list)
                    all_matches.append(matches)
                
                highest_books = self.collect_highest_similarity_books(all_matches, book_df)
                current_books = [book['combined'] for book in highest_books]
                self.update_data_queue.put(('UPDATE_BOOK_LIST', highest_books))
                
                print("put update book list .")
            else:
                print("감지된 객체가 없습니다.")

        except Exception as e:
            print(f"오류 발생: {e}")
