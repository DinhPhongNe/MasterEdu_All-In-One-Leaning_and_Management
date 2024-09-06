from PyQt6.QtWidgets import QMainWindow, QTableWidget
from PyQt6 import uic
from PyQt6.QtCore import QTimer
from coming_soon import ComingSoon
from profile_hs import ProfileHS
from document_management import DocumentManagementWindow

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
        self.learning_material_management.clicked.connect(self.open_learning_material_management)
        self.join_club.clicked.connect(self.show_coming_soon)
        self.ai_ask.clicked.connect(self.show_coming_soon)
        self.library.clicked.connect(self.show_coming_soon)
        self.ranking.clicked.connect(self.show_coming_soon)
        self.achievement.clicked.connect(self.show_coming_soon)
        self.profile_setting.clicked.connect(self.open_profile_hs)
        self.homework.clicked.connect(self.show_coming_soon)
        self.timetable.clicked.connect(self.show_coming_soon)
        self.attendance.clicked.connect(self.show_coming_soon)
        self.logout.clicked.connect(self.show_coming_soon)

    def open_student_main(self):
        from student_main import StudentMain
        self.student_main = StudentMain(self.data, self.tai_khoan)
        self.student_main.show()
        
    def open_learning_material_management(self):
        self.document_management = DocumentManagementWindow(self.data, self.tai_khoan)
        self.document_management.show()

    def open_profile_hs(self):
        self.profile_hs = ProfileHS(self.data, self.tai_khoan)

        # Kết nối tín hiệu finished với slot close_menu sau khi ProfileHS được tạo
        self.profile_hs.achievement_monitor.finished.connect(self.close_menu)  

        self.profile_hs.show()
        self.close()

    def close_menu(self):
        self.close()  # Đóng cửa sổ MenuSelectHS sau khi thread watchdog kết thúc
        
    def show_coming_soon(self):
        if not self.coming_soon:
            self.coming_soon = ComingSoon()
        self.coming_soon.show()
        # Tắt màn hình coming_soon sau 5 giây
        QTimer.singleShot(5000, self.coming_soon.close)