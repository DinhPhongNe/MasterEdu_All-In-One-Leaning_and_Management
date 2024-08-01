from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from coming_soon import ComingSoon

class MenuSelectTC(QMainWindow):
    def __init__(self, data):
        super().__init__()
        uic.loadUi("gui/menu_select_tc.ui", self)
        self.data = data
        self.coming_soon = None
        self.ds_nhap_diem.clicked.connect(self.open_teacher_main)

        # Kết nối các nút bấm với hàm show_coming_soon
        self.school_notification.clicked.connect(self.show_coming_soon)
        self.learning_plan.clicked.connect(self.show_coming_soon)
        self.tutor.clicked.connect(self.show_coming_soon)
        self.learning_material_management.clicked.connect(self.show_coming_soon)
        self.join_club.clicked.connect(self.show_coming_soon)
        self.ai_ask.clicked.connect(self.show_coming_soon)
        self.library.clicked.connect(self.show_coming_soon)
        self.profile_setting.clicked.connect(self.show_coming_soon)
        

    def open_teacher_main(self):
        from teacher_main import TeacherMain
        self.teacher_main = TeacherMain(self.data)
        self.teacher_main.show()
        self.close()

    def show_coming_soon(self):
        if not self.coming_soon:
            self.coming_soon = ComingSoon()
        self.coming_soon.show()
        # Tắt màn hình coming_soon sau 5 giây
        QTimer.singleShot(5000, self.coming_soon.close)