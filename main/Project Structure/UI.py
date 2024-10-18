from PyQt6 import QtCore, QtGui, QtWidgets
import cv2
import threading
import queue

class Ui_MainWindow(QtWidgets.QMainWindow):
    def __init__(self, mt_ui_thread):
        super().__init__()
        self.mt_ui_thread = mt_ui_thread
        self.cam1_queue = self.mt_ui_thread.cam1_queue
        self.cam2_queue = self.mt_ui_thread.cam2_queue
        self.data_queue = self.mt_ui_thread.data_queue
        self.setupUi(self)
        self.start_threads()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1871, 1092)
        MainWindow.setStyleSheet("QMainWindow {\n"
                                 "    background-image: url(\"./Background.jpg\");\n"
                                 "    background-repeat: no-repeat;\n"
                                 "    background-position: center;\n"
                                 "}")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(parent=self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 0, 271, 101))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("./Logo.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")

        self.Title = QtWidgets.QLabel(parent=self.centralwidget)
        self.Title.setGeometry(QtCore.QRect(270, 0, 1281, 101))
        self.Title.setSizeIncrement(QtCore.QSize(1, 0))
        self.Title.setStyleSheet("QMainWindow {\n"
                                 "    background-image: url(\"Background.jpg\");\n"
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

        # 테이블 위젯 설정
        self.View_Book_List_1 = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.View_Book_List_1.setGeometry(QtCore.QRect(360, 170, 631, 781))
        self.View_Book_List_1.setRowCount(30)
        self.View_Book_List_1.setColumnCount(4)
        self.View_Book_List_1.setHorizontalHeaderLabels(["책 제목", "저자", "출판사", "책의 상태"])
        self.View_Book_List_1.setObjectName("View_Book_List_1")

        self.View_Book_List_2 = QtWidgets.QTableWidget(parent=self.centralwidget)
        self.View_Book_List_2.setGeometry(QtCore.QRect(1010, 170, 631, 781))
        self.View_Book_List_2.setRowCount(30)
        self.View_Book_List_2.setColumnCount(4)
        self.View_Book_List_2.setHorizontalHeaderLabels(["책 제목", "저자", "출판사", "책의 상태"])
        self.View_Book_List_2.setObjectName("View_Book_List_2")

        self.Misplacement = QtWidgets.QLabel(parent=self.centralwidget)
        self.Misplacement.setGeometry(QtCore.QRect(1660, 400, 171, 91))
        self.Misplacement.setStyleSheet("border: 2px solid black;\n"
                                        "border-radius: 10px;")
        self.Misplacement.setObjectName("Misplacement")

        self.Normal = QtWidgets.QLabel(parent=self.centralwidget)
        self.Normal.setGeometry(QtCore.QRect(1660, 270, 171, 91))
        self.Normal.setStyleSheet("border: 2px solid black;\n"
                                  "border-radius: 10px;")
        self.Normal.setObjectName("Normal")

        self.Borrowed = QtWidgets.QLabel(parent=self.centralwidget)
        self.Borrowed.setGeometry(QtCore.QRect(1660, 150, 171, 91))
        self.Borrowed.setStyleSheet("border: 2px solid black;\n"
                                    "border-radius: 10px;")
        self.Borrowed.setObjectName("Borrowed")

        self.Cam_1 = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_1.setGeometry(QtCore.QRect(10, 190, 331, 171))
        self.Cam_1.setStyleSheet("border: 3px solid black;")
        self.Cam_1.setObjectName("Cam_1")

        self.Cam_2 = QtWidgets.QLabel(parent=self.centralwidget)
        self.Cam_2.setGeometry(QtCore.QRect(10, 490, 331, 171))
        self.Cam_2.setStyleSheet("border: 3px solid black;")
        self.Cam_2.setObjectName("Cam_2")

        self.Suggestions = QtWidgets.QLabel(parent=self.centralwidget)
        self.Suggestions.setGeometry(QtCore.QRect(1650, 700, 230, 341)) 
        self.Suggestions.setPixmap(QtGui.QPixmap("./Suggestions2.png"))
        self.Suggestions.setScaledContents(True)
        self.Suggestions.setObjectName("Suggestions")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "스마트 도서 관리 시스템"))
        self.Title.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:48pt;\">스마트 도서 관리 시스템</span></p></body></html>"))
        self.Misplacement.setText(_translate("MainWindow", "Misplacement"))
        self.Normal.setText(_translate("MainWindow", "Normal"))
        self.Borrowed.setText(_translate("MainWindow", "Borrowed"))
        self.Cam_1.setText(_translate("MainWindow", "카메라 1"))
        self.Cam_2.setText(_translate("MainWindow", "카메라 2"))

    def start_threads(self):
        self.cam1_thread = threading.Thread(target=self.update_cam_1_from_queue)
        self.cam2_thread = threading.Thread(target=self.update_cam_2_from_queue)
        self.data_thread = threading.Thread(target=self.update_book_list_from_data_queue)
        self.cam1_thread.start()
        self.cam2_thread.start()
        self.data_thread.start()

    def update_book_list_from_data_queue(self):
        while True:
            if not self.data_queue.empty():
                message_type, data = self.data_queue.get()
                if message_type == "UPDATE_BOOK_LIST_1":
                    self.update_book_list_1(data)
                elif message_type == "UPDATE_BOOK_LIST_2":
                    self.update_book_list_2(data)

    def update_book_list_1(self, highest_books):
        self.View_Book_List_1.clearContents()
        for row, book in enumerate(highest_books):
            self.View_Book_List_1.setItem(row, 0, QtWidgets.QTableWidgetItem(book['title']))
            self.View_Book_List_1.setItem(row, 1, QtWidgets.QTableWidgetItem(book['author']))
            self.View_Book_List_1.setItem(row, 2, QtWidgets.QTableWidgetItem(book['publisher']))
            self.View_Book_List_1.setItem(row, 3, QtWidgets.QTableWidgetItem(book['status']))

    def update_book_list_2(self, highest_books):
        self.View_Book_List_2.clearContents()
        for row, book in enumerate(highest_books):
            self.View_Book_List_2.setItem(row, 0, QtWidgets.QTableWidgetItem(book['title']))
            self.View_Book_List_2.setItem(row, 1, QtWidgets.QTableWidgetItem(book['author']))
            self.View_Book_List_2.setItem(row, 2, QtWidgets.QTableWidgetItem(book['publisher']))
            self.View_Book_List_2.setItem(row, 3, QtWidgets.QTableWidgetItem(book['status']))

    def update_cam_1_from_queue(self):
        while True:
            if not self.cam1_queue.empty():
                frame = self.cam1_queue.get()
                QtCore.QMetaObject.invokeMethod(
                    self, "update_cam_1", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(object, frame)
                )

    def update_cam_2_from_queue(self):
        while True:
            if not self.cam2_queue.empty():
                frame = self.cam2_queue.get()
                QtCore.QMetaObject.invokeMethod(
                    self, "update_cam_2", QtCore.Qt.ConnectionType.QueuedConnection, QtCore.Q_ARG(object, frame)
                )

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
        frame = cv2.resize(frame, (self.Cam_2.width(), self.Cam_2.height()))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, c = frame.shape
        qImg = QtGui.QImage(frame.data, w, h, w * c, QtGui.QImage.Format.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.Cam_2.setPixmap(pixmap)

class Widget_Login(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("로그인")
        self.setFixedSize(300, 150)

        # 아이디와 비밀번호 입력 필드 및 버튼 생성
        self.layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("아이디와 비밀번호를 입력하세요")
        self.layout.addWidget(self.label)

        self.id_input = QtWidgets.QLineEdit(self)
        self.id_input.setPlaceholderText("아이디")
        self.layout.addWidget(self.id_input)

        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setPlaceholderText("비밀번호")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setStyleSheet("color: red")
        self.layout.addWidget(self.error_label)

        self.login_btn = QtWidgets.QPushButton("로그인", self)
        self.layout.addWidget(self.login_btn)

    def ChekcIsCorrect(self):
        # 간단한 아이디/비밀번호 검증
        user_id = self.id_input.text()
        password = self.password_input.text()
        if user_id == "admin" and password == "1234":
            return True
        else:
            self.error_label.setText("아이디나 비밀번호를 다시 입력 해 주세요")
            return False
