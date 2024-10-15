import os
import cv2
import time
import shutil
from initialization import initialize_yolo, initialize_ocr, initialize_webcam
from image_processing import predict_with_yolo, get_exclude_indices, crop_and_save_image
from book_matching import process_cropped_image, load_book_list, collect_highest_similarity_books, save_books_to_excel
from state_update import update_book_status

def main():
    CROPPED_FOLDER = "cropped_images"
    DET_MODEL_DIR = 'model/PaddleOCR/detection'
    REC_MODEL_DIR = 'model/PaddleOCR/my_recognition/v3_ft_word'
    EXCEL_PATH = 'data/total_book_list.xlsx'
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
                if os.path.exists(CROPPED_FOLDER):
                    shutil.rmtree(CROPPED_FOLDER)
                os.makedirs(CROPPED_FOLDER, exist_ok=True)
                
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
                    # 제외할 인덱스는 건너뜁니다.
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

                save_books_to_excel(highest_books, 'data/current_book_list.xlsx')

                last_process_time = current_time

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()