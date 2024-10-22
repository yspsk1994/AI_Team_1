from PyQt6 import QtCore, QtGui, QtWidgets
import cv2
import threading
import queue
import pandas as pd
from Function.DB import DB_Function
import os

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.clicked.emit()

class Cam_1_Thread(QtCore.QThread):
    update_frame = QtCore.pyqtSignal(object)

    def __init__(self, cam1_queue):
        super().__init__()
        self.cam1_queue = cam1_queue
        self.running = True
    
    def run(self):
        while self.running:
            try:
                frame = self.cam1_queue.get(timeout=0.01) 
                self.update_frame.emit(frame)
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
        self.wait()

class Cam_2_Thread(QtCore.QThread):
    update_frame = QtCore.pyqtSignal(object) 
    
    def __init__(self, cam2_queue):
        super().__init__()
        self.cam2_queue = cam2_queue
        self.running = True

    def run(self):
        while self.running:
            try:
                frame = self.cam2_queue.get(timeout=0.01)  
                self.update_frame.emit(frame)
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
        self.wait()

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mt_ui_thread):
        super().__init__()
        self.mt_ui_thread = mt_ui_thread
        self.cam1_queue = self.mt_ui_thread.cam1_queue
        self.cam2_queue = self.mt_ui_thread.cam2_queue
        self.db_function = DB_Function()
        self.image = QtGui.QPixmap("./Suggestions.png")
        
        self.update_data_queue_1 = self.mt_ui_thread.update_data_queue_1        
        self.update_data_queue_2 = self.mt_ui_thread.update_data_queue_2
        
        self.setupUi(self)
        self.start_threads()
        self.start_time_update() 
        self.setFocus()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1871, 1092)
        MainWindow.setStyleSheet("QMainWindow {\n"
                         "    background-color: #ECE9E2;\n"
                         "}")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 271, 101))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("./Logo.png"))
        self.label.setStyleSheet("background-color: transparent;")
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.Title = QtWidgets.QLabel(parent=self.centralwidget)
        self.Title.setGeometry(QtCore.QRect(270, 0, 1281, 101))
        self.Title.setSizeIncrement(QtCore.QSize(1, 0))
        self.Title.setStyleSheet("QMainWindow {\n"
                                 "    background-image: url(\"Title.png\");\n"
                                 "    background-repeat: no-repeat;\n"
                                 "    background-position: center;\n"
                                 "    background-size: cover;\n"
                                 "}")
        self.Title.setObjectName("Title")

        self.Time = QtWidgets.QDateTimeEdit(parent=self.centralwidget)
        self.Time.setGeometry(QtCore.QRect(1630, 30, 221, 41))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.Time.setFont(font)
        self.Time.setStyleSheet("QDateTimeEdit::up-button {\n"
                                "    width: 0;\n"
                                "    height: 0;\n"
                                "}\n"
                                "QDateTimeEdit::down-button {\n"
                                "    width: 0;\n"
                                "    height: 0;\n"
                                "}\n"
                                "QDateTimeEdit {\n"
                                "    background-color: transparent;\n"
                                "    border: none;\n"
                                "}")
        self.Time.setDisplayFormat("yyyy/MM/dd hh:mm:ss")
        self.Time.setObjectName("Time")
        self.Time.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        
        self.h_line = QtWidgets.QFrame(parent=self.centralwidget)
        self.h_line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.h_line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.h_line.setLineWidth(3)
        self.h_line.setGeometry(0,102,1871,10)
   
        self.h_line.raise_()
        self.View_Book_List_1_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.View_Book_List_1_label.setText("책장 1")
        self.View_Book_List_1_label.setGeometry(1041, 130, 100, 40)
        self.View_Book_List_1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.View_Book_List_1_label.setFont(font)           
        self.View_Book_List_1 = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.View_Book_List_1.setGeometry(QtCore.QRect(550, 170, 1092, 420))
        self.View_Book_List_1.setRowCount(30)
        self.View_Book_List_1.setColumnCount(4)
        self.View_Book_List_1.setHorizontalHeaderLabels(["책 제목", "저자", "출판사", "도서 상태"])
        self.View_Book_List_1.setObjectName("View_Book_List_1")
        self.View_Book_List_1.setColumnWidth(0, 582)
        self.View_Book_List_1.setColumnWidth(1, 200)
        self.View_Book_List_1.setColumnWidth(2, 150)
        self.View_Book_List_1.setColumnWidth(3, 130)
    
        self.View_Book_List_2_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.View_Book_List_2_label.setText("책장 2")
        self.View_Book_List_2_label.setGeometry(1041, 600, 100, 40)
        self.View_Book_List_2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.View_Book_List_2_label.setFont(font)     

        self.View_Book_List_2 = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.View_Book_List_2.setGeometry(QtCore.QRect(550, 640, 1092, 420))
        self.View_Book_List_2.setRowCount(30)
        self.View_Book_List_2.setColumnCount(4)
        self.View_Book_List_2.setHorizontalHeaderLabels(["책 제목", "저자", "출판사", "도서 상태"])
        self.View_Book_List_2.setObjectName("View_Book_List_2")
        self.View_Book_List_2.setColumnWidth(0, 582)
        self.View_Book_List_2.setColumnWidth(1, 200)
        self.View_Book_List_2.setColumnWidth(2, 150)
        self.View_Book_List_2.setColumnWidth(3, 130)

        # 공통 스타일 정의
        common_style = """
            border: 2px solid rgb(58, 134, 255);
            border-radius: 10px;
            background-color: white;
            color: rgb(58, 134, 255);
            font-size: 16px;
            font-weight: bold;
        """

        # 레이블 스타일 설정
        label_style = common_style + """
            padding: 10px;
        """

        # 버튼 스타일 설정
        button_style = common_style + """
            QPushButton:hover {
                background-color: rgb(230, 240, 255);
            }
            QPushButton:pressed {
                background-color: rgb(200, 220, 255);
                border-width: 3px;
            }
        """
        # Misplacement 레이블
        self.Misplacement = QtWidgets.QLabel(parent=self.centralwidget)
        self.Misplacement.setGeometry(QtCore.QRect(1660, 400, 205, 109))
        self.Misplacement.setStyleSheet(label_style)
        self.Misplacement.setObjectName("Misplaced")
        self.Misplacement.setText("오배열")
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.Misplacement.setFont(font)
        self.Misplacement.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Normal 레이블
        self.Normal = QtWidgets.QLabel(parent=self.centralwidget)
        self.Normal.setGeometry(QtCore.QRect(1660, 260, 205, 109))
        self.Normal.setStyleSheet(label_style)
        self.Normal.setObjectName("Normal")
        self.Normal.setText("정상")
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.Normal.setFont(font)
        self.Normal.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Borrowed 레이블
        self.Borrowed = QtWidgets.QLabel(parent=self.centralwidget)
        self.Borrowed.setGeometry(QtCore.QRect(1660, 120, 205, 109))
        self.Borrowed.setStyleSheet(label_style)
        self.Borrowed.setObjectName("Borrowed")
        self.Borrowed.setText("대출")
        font = QtGui.QFont()
        font.setPointSize(25)
        font.setBold(True)
        self.Borrowed.setFont(font)
        self.Borrowed.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # 신간 도서 등록 버튼
        self.button = QtWidgets.QPushButton("신간 도서 등록", parent=self.centralwidget)
        self.button.setGeometry(1660, 540, 205, 91)
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        self.button.setFont(font)
        self.button.clicked.connect(self.on_button_click)
        self.button.setStyleSheet(button_style)

        self.Cam_1_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_1_label.setText("Camera 1")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.Cam_1_label.setFont(font)
        self.Cam_1_label.setGeometry(10,120,100,100)
        self.Cam_1_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)     
        
        self.Cam_1 = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_1.setGeometry(QtCore.QRect(10, 190, 525, 315))
        self.Cam_1.setStyleSheet("border: 3px solid black;")
        self.Cam_1.setObjectName("Cam_1")

        self.Cam_2_label = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_2_label.setText("Camera 2")
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.Cam_2_label.setFont(font)
        self.Cam_2_label.setGeometry(10,600,100,100)
        self.Cam_2_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)     
        
        self.Cam_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_2.setGeometry(QtCore.QRect(10, 670, 525, 315))
        self.Cam_2.setStyleSheet("border: 3px solid black;")
        self.Cam_2.setObjectName("Cam_2")
        
        self.Suggestions = ClickableLabel(parent=self.centralwidget)
        self.Suggestions.setGeometry(QtCore.QRect(1660, 640, 205, 386))
        self.Suggestions.setPixmap(QtGui.QPixmap("./Suggestions2.png"))
        self.Suggestions.setScaledContents(True)
        self.Suggestions.setObjectName("Suggestions")

        self.Suggestions.clicked.connect(self.on_button_click_suggestion)
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "스마트 도서 관리 시스템"))
        self.Title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:48pt; font-weight: bold;\">스마트 도서 관리 시스템</span></p></body></html>"))
        self.Misplacement.setText(_translate("MainWindow", "Misplacement"))
        self.Normal.setText(_translate("MainWindow", "Normal"))
        self.Borrowed.setText(_translate("MainWindow", "Borrowed"))
        self.Cam_1.setText(_translate("MainWindow", "카메라 1"))
        self.Cam_2.setText(_translate("MainWindow", "카메라 2"))

    def start_threads(self):
        self.cam1_thread = Cam_1_Thread(self.cam1_queue)
        self.cam1_thread.update_frame.connect(self.update_cam_1)
        self.cam1_thread.start()

        self.cam2_thread = Cam_2_Thread(self.cam2_queue)
        self.cam2_thread.update_frame.connect(self.update_cam_2)
        self.cam2_thread.start()
    
    def on_button_click(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx *.xls)")
        
        if file_path:
            self.db_function.bookStatus2db_xls(file_path)
            
    def on_button_click_suggestion(self):
        self.show_dialog()
 
    def set_item_color(self, item):
        status = item.text() 
        if status == "대출중":
            item.setBackground(QtGui.QColor("blue"))  
            item.setForeground(QtGui.QColor("white"))  
        elif status == "오배치":
            item.setBackground(QtGui.QColor("red")) 
            item.setForeground(QtGui.QColor("white"))  

    def show_suggestions_by_date(self):
        suggestion_list = self.db_function.suggestions_by_date()

        # suggestion_list의 내용을 QTextEdit에 추가
        for date, num in suggestion_list:
            suggestions_text = "\n".join(f"{date} : {num} 개" for date, num in suggestion_list)
            self.Suggestions.setText(suggestions_text)

    @QtCore.pyqtSlot(object) 
    def update_book_list_1(self, highest_books):
        self.View_Book_List_1.clearContents()
        for row, book in enumerate(highest_books):
            try:
                title_item = QtWidgets.QTableWidgetItem(str(book['제목']))
                author_item = QtWidgets.QTableWidgetItem(str(book['저자']))
                publisher_item = QtWidgets.QTableWidgetItem(str(book['출판사']))
                status_item = QtWidgets.QTableWidgetItem(str(book['도서상태']))

                self.set_item_color(status_item)

                self.View_Book_List_1.setItem(row, 0, title_item)
                self.View_Book_List_1.setItem(row, 1, author_item)
                self.View_Book_List_1.setItem(row, 2, publisher_item)
                self.View_Book_List_1.setItem(row, 3, status_item)
                    
                print("ui_1 책 리스트 업데이트 성공!")
                self.update_total_counts()

            except KeyError as e:
                print(f"키 오류 발생: {e}, book 데이터: {book}")
            except TypeError as e:
                print(f"타입 오류 발생: {e}, book 데이터: {book}")

    @QtCore.pyqtSlot(object) 
    def update_book_list_2(self, highest_books):
        self.View_Book_List_2.clearContents()
        for row, book in enumerate(highest_books):
            try:
                title_item = QtWidgets.QTableWidgetItem(str(book['제목']))
                author_item = QtWidgets.QTableWidgetItem(str(book['저자']))
                publisher_item = QtWidgets.QTableWidgetItem(str(book['출판사']))
                status_item = QtWidgets.QTableWidgetItem(str(book['도서상태']))

                self.set_item_color(status_item)

                self.View_Book_List_2.setItem(row, 0, title_item)
                self.View_Book_List_2.setItem(row, 1, author_item)
                self.View_Book_List_2.setItem(row, 2, publisher_item)
                self.View_Book_List_2.setItem(row, 3, status_item)
                print("ui_2 책 리스트 업데이트 성공!")
                self.update_total_counts()

            except KeyError as e:
                print(f"키 오류 발생: {e}, book 데이터: {book}")
            except TypeError as e:
                print(f"타입 오류 발생: {e}, book 데이터: {book}")

    def update_total_counts(self):
        highest_books_1 = self.get_highest_books_from_view(self.View_Book_List_1)
        highest_books_2 = self.get_highest_books_from_view(self.View_Book_List_2)

        highest_books_1 = highest_books_1 or []
        highest_books_2 = highest_books_2 or []
        
        misplaced_count = sum(1 for book in highest_books_1 + highest_books_2 if book['도서상태'] == "오배치")
        normal_count = sum(1 for book in highest_books_1 + highest_books_2 if book['도서상태'] == "배치중")
        borrowed_count = sum(1 for book in highest_books_1 + highest_books_2 if book['도서상태'] == "대출중")

        self.update_book_status(misplaced_count, normal_count, borrowed_count)

    def get_highest_books_from_view(self, table_widget):
        highest_books = []
        for row in range(table_widget.rowCount()):
            title_item = table_widget.item(row, 0)
            author_item = table_widget.item(row, 1)
            publisher_item = table_widget.item(row, 2)
            status_item = table_widget.item(row, 3)

            if title_item and author_item and publisher_item and status_item:
                highest_books.append({
                    '제목': title_item.text(),
                    '저자': author_item.text(),
                    '출판사': publisher_item.text(),
                    '도서상태': status_item.text()
                })
        return highest_books
    def update_cam_1_from_queue(self):
        while True:
            try:
                frame = self.cam1_queue.get(timeout=0.01)
                QtCore.QMetaObject.invokeMethod(
                    self, "update_cam_1", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(object, frame)
                )
            except queue.Empty:
                pass

    def update_cam_2_from_queue(self):
        while True:
            try:
                frame = self.cam2_queue.get(timeout=0.01)
                QtCore.QMetaObject.invokeMethod(
                    self, "update_cam_2", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(object, frame)
                )
            except queue.Empty:
                pass

    @QtCore.pyqtSlot(object)
    def update_cam_1(self, frame):
        try:
            frame = cv2.resize(frame, (self.Cam_1.width(), self.Cam_1.height()))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.Cam_1.setPixmap(pixmap)
        except Exception as e:
            print(f"Error updating frame on Cam_1: {e}")

    @QtCore.pyqtSlot(object)
    def update_cam_2(self, frame):
        try:
            frame = cv2.resize(frame, (self.Cam_2.width(), self.Cam_2.height()))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, c = frame.shape
            qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.Cam_2.setPixmap(pixmap)
        except Exception as e:
            print(f"Error updating frame on Cam_2: {e}")

    def closeEvent(self, event):
        self.cam1_thread.stop()
        self.cam2_thread.stop()
        
        super().closeEvent(event)
        
    @QtCore.pyqtSlot(int, int, int) 
    def update_book_status(self, misplaced_count, normal_count, borrowed_count):
        self.Misplacement.setText(f"오배치 : {misplaced_count}개")
        self.Misplacement.setStyleSheet("color: red;")

        self.Normal.setText(f"배치중 : {normal_count}개")
        self.Normal.setStyleSheet("color: black;")

        self.Borrowed.setText(f"대출중 : {borrowed_count}개")
        self.Borrowed.setStyleSheet("color: blue;")

    def start_time_update(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(5000) 

    def update_time(self):
        current_time = QtCore.QDateTime.currentDateTime()
        self.Time.setDateTime(current_time)

    def show_dialog(self):
        results = self.db_function.show_suggestions_list()
        dialog = QtWidgets.QDialog(self)
        
        dialog.setWindowTitle("건의사항")
        dialog.setGeometry(500, 500, 800, 1000)

        layout = QtWidgets.QVBoxLayout()
        dialog.setLayout(layout)
        
        label = QtWidgets.QLabel("건의사항 목록:")
        layout.addWidget(label)

        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        for row_num, row in enumerate(results, start=1):
            text_edit.append(f"{row[2]}  :  {row[1]}")

        layout.addWidget(text_edit)

        dialog.exec()

class Widget_Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("스마트 도서 관리 시스템 로그인")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #ECE9E2;
            }
            QLabel {
                color: #333333;
                font-size: 14pt;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #4CAF50;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)

        logo = QtWidgets.QLabel()
        logo.setPixmap(QtGui.QPixmap("./Logo2.png").scaled(120, 120, QtCore.Qt.AspectRatioMode.KeepAspectRatio))
        logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        layout.addWidget(QtWidgets.QLabel("아이디와 비밀번호를 입력하세요"))

        self.id_input = QtWidgets.QLineEdit(self)
        self.id_input.setPlaceholderText("아이디")
        layout.addWidget(self.id_input)

        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("비밀번호")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red")
        layout.addWidget(self.error_label)

        self.login_btn = QtWidgets.QPushButton("로그인", self)
        layout.addWidget(self.login_btn)

    def CheckIsCorrect(self):
        user_id = self.id_input.text()
        password = self.password_input.text()
        if user_id == "admin" and password == "1234":
            return True
        else:
            self.error_label.setText("아이디나 비밀번호를 다시 입력해 주세요")
            return False