import cv2
from ultralytics import YOLO
import numpy as np
import time
from deep_sort_realtime.deepsort_tracker import DeepSort
import os

model = YOLO("yolov8l-seg.pt")
tracker = DeepSort(max_age=50, n_init=1, nn_budget=100)

previous_segmentations = []
after_person_segmentations = []
person_detected = False
start_time_before = None
start_time_after = None
used_track_ids = set()
previous_frame = None
after_frame = None
interval_before_person = 5
interval_after_person = 5
last_captured_time = 0

def iou(mask1, mask2):
    intersection = np.bitwise_and(mask1, mask2).sum()
    union = np.bitwise_or(mask1, mask2).sum()
    return intersection / union if union != 0 else 0

def is_side_view_enhanced(box):
    x1, y1, x2, y2 = box
    width = x2 - x1
    height = y2 - y1
    aspect_ratio = height / width
    area = width * height
    return 1.5 < aspect_ratio < 8.0 and area < 50000

def detect_person(frame):
    results = model(frame)
    for r in results:
        for box in r.boxes.data:
            class_id = int(box[5].item())
            if class_id == 0:
                return True
    return False

def track_books_with_segmentation(frame, check_confirmation=False, save_path="runs/segment/predict", before_person=True):
    results = model(frame)
    img_height, img_width = frame.shape[:2]
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    masks = [r.masks.data for r in results if r.masks is not None]
    boxes = [box for r in results for box in r.boxes.data]
    detections = []
    for box in boxes:
        x1, y1, x2, y2 = box[:4]
        if x1 < 1 and y1 < 1 and x2 < 1 and y2 < 1:
            x1, x2 = x1 * img_width, x2 * img_width
            y1, y2 = y1 * img_height, y2 * img_height
        
        confidence = float(box[4].item())
        class_id = int(box[5].item())
        if class_id == 73 and confidence > 0.5 and is_side_view_enhanced((x1, y1, x2, y2)):
            detections.append(([int(x1), int(y1), int(x2), int(y2)], confidence, 'book'))

    tracks = tracker.update_tracks(detections, frame=frame)
    segmentations = []
    track_id_to_mask = {}

    for track in tracks:
        track_id = track.track_id
        if not check_confirmation or (track.is_confirmed() and track.time_since_update == 0):
            for mask in masks:
                for single_mask in mask:
                    segmentation_img = (single_mask.squeeze().cpu().numpy() > 0.5).astype(np.uint8)
                    is_duplicate = False
                    for prev_track_id, prev_mask in track_id_to_mask.items():
                        if iou(segmentation_img, prev_mask) > 0.9:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        masked_frame = cv2.bitwise_and(frame, frame, mask=segmentation_img)
                        if before_person:
                            mask_save_path = os.path.join(save_path, f"before_person_masked_frame_{track_id}.png")
                        else:
                            mask_save_path = os.path.join(save_path, f"after_person_masked_frame_{track_id}.png")

                        cv2.imwrite(mask_save_path, masked_frame)
                        track_id_to_mask[track_id] = segmentation_img
                        break
                        
    segmentations = [(track_id, mask) for track_id, mask in track_id_to_mask.items()]
    return segmentations

def compare_segmentations(before_segs, after_segs, save_path="runs/segment/predict"):
    removed_segmentations = []
    after_ids = {seg[0] for seg in after_segs}
    for before_seg in before_segs:
        track_id, seg_img = before_seg
        if track_id not in after_ids:
            mask_save_path = os.path.join(save_path, f"disappeared_object_{track_id}.png")
            cv2.imwrite(mask_save_path, seg_img.astype('uint8') * 255)
            removed_segmentations.append(before_seg)
    return removed_segmentations

cap = cv2.VideoCapture(1)
w = 1280
h = 720
cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    current_time = time.time()

    if person_detected:
        interval = interval_after_person
    else:
        interval = interval_before_person
    
    if current_time - last_captured_time >= interval:
        is_person_detected = detect_person(frame)
    
        if not person_detected and not is_person_detected:
            start_time_before = time.time()
            previous_frame = frame.copy()
            segs = track_books_with_segmentation(previous_frame, before_person=True)
            previous_segmentations = segs
            print(f"Saved {len(segs)} new segmentations before person appeared")

        elif is_person_detected and not person_detected:
            person_detected = True
            start_time_before = None
            start_time_after = None
            print("Person detected")    

        elif not is_person_detected and person_detected:
            if start_time_after is None:
                start_time_after = time.time()

            if time.time() - start_time_after >= interval_after_person:
                after_frame = frame.copy()
                segs = track_books_with_segmentation(after_frame, before_person=False)
                after_person_segmentations = segs
                
                removed_segmentations = compare_segmentations(previous_segmentations, after_person_segmentations)
                if removed_segmentations:
                    for track_id, removed_seg in removed_segmentations:
                        cv2.imshow(f"Removed Object ID {track_id}", removed_seg.astype('uint8') * 255)
                        cv2.waitKey(100)
                        print(f"사라진 객체 ID {track_id}가 감지되었습니다.")
                
                person_detected = False
                previous_segmentations = after_person_segmentations.copy()
                after_person_segmentations.clear()
                start_time_after = None
                print("Object status reset")
                
        last_captured_time = current_time

    cv2.imshow('main frame', frame)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
