from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from coming_soon import ComingSoon

class MenuSelectHS(QMainWindow):
    def __init__(self, data, tai_khoan):
        super().__init__()
        uic.loadUi("gui/menu_select_hs.ui", self)
        self.data = data
        self.tai_khoan = tai_khoan
        self.coming_soon = None
        self.ds_diem.clicked.connect(self.open_student_main)

        # Kết nối các nút bấm với hàm show_coming_soon
        self.school_notification.clicked.connect(self.show_coming_soon)
        self.learning_plan.clicked.connect(self.show_coming_soon)
        self.tutor.clicked.connect(self.show_coming_soon)
        self.learning_material_management.clicked.connect(self.show_coming_soon)
        self.join_club.clicked.connect(self.show_coming_soon)
        self.ai_ask.clicked.connect(self.show_coming_soon)
        self.library.clicked.connect(self.show_coming_soon)
        self.ranking.clicked.connect(self.show_coming_soon)
        self.achievement.clicked.connect(self.show_coming_soon)
        self.profile_setting.clicked.connect(self.show_coming_soon)
        self.homework.clicked.connect(self.show_coming_soon)
        self.attendance.clicked.connect(self.show_coming_soon)

    def open_student_main(self):
        from student_main import StudentMain
        self.student_main = StudentMain(self.data, self.tai_khoan)
        self.student_main.show()
        self.close()

    def show_coming_soon(self):
        if not self.coming_soon:
            self.coming_soon = ComingSoon()
        self.coming_soon.show()
        # Tắt màn hình coming_soon sau 5 giây
        QTimer.singleShot(5000, self.coming_soon.close)