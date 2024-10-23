from ultralytics import YOLO

model = YOLO('yolov8x-seg.pt') 


data_path = '/home/taejoon/workspace/team_project/learning_bookspline/Book_spine_2.v7i.yolov8/data.yaml'

model.train(
    data=data_path,
    epochs=300,     
    imgsz=640,
    batch=4, 
    name='book_detection_yolov8_optimized',
    lr0=0.003,
    lrf=0.001,  
    momentum=0.8,  
    weight_decay=0.0004  
)


trained_model_path = 'runs/detect/book_detection_yolov8/weights/best.pt'





# from ultralytics import YOLO

# # 1. 기존 학습된 모델 불러오기 (best.pt 사용)
# model = YOLO('runs/detect/book_detection_yolov8/weights/best.pt')

# # 2. 새로운 데이터셋에 대한 추가 학습
# new_data_path = '/path_to_new_dataset/data.yaml'  # 새로운 데이터셋의 data.yaml 경로
# model.train(data=new_data_path, epochs=300, imgsz=640, batch=16, name='book_detection_finetune')

##







# #아래 실행 
# from ultralytics import YOLO

# # YOLO 모델 불러오기
# model = YOLO('/home/taejoon/workspace/team_project/learning_bookspline/runs/detect/book_detection_yolov8_optimized9/weights/best.pt')

# # 데이터 경로 설정
# data_path = '/home/taejoon/workspace/team_project/learning_bookspline/BookDetection.v5i.yolov8/data.yaml'

# model.train(
#     data=data_path,
#     epochs=300,     
#     imgsz=640,
#     batch=4, 
#     name='book_detection_yolov8_optimized',
#     lr0=0.003,
#     lrf=0.001,  
#     momentum=0.8,  
#     weight_decay=0.0004  
# )


# # 학습된 모델 경로
# trained_model_path = 'runs/detect/book_detection_yolov8_optimized/weights/best.pt'
