from PyQt6.QtCore import Qt, QFileSystemWatcher, QTimer
from PyQt6.QtGui import QIntValidator, QImage, QPixmap
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QLabel, QComboBox, QDialog, QVBoxLayout, QGridLayout, QListWidget, QFileDialog, QInputDialog, QDialogButtonBox, QWidget
from PyQt6 import uic
import sys
import random
import json
import os
import shutil
import cv2
import vlc

#======================================================================
#__     _____ ____  _____ ___    ____  _____ ____ _____ ___ ___  _   _ 
#\ \   / /_ _|  _ \| ____/ _ \  / ___|| ____/ ___|_   _|_ _/ _ \| \ | |
# \ \ / / | || | | |  _|| | | | \___ \|  _|| |     | |  | | | | |  \| |
#  \ V /  | || |_| | |__| |_| |  ___) | |__| |___  | |  | | |_| | |\  |
#   \_/  |___|____/|_____\___/  |____/|_____\____| |_| |___\___/|_| \_|
#======================================================================
class VideoPlayer(QDialog):
    def __init__(self, file_path, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.CustomizeWindowHint
        )
        self.setWindowTitle("Video Player")

        self.file_path = file_path
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.media = self.instance.media_new(self.file_path)
        self.player.set_media(self.media)

        self.video_frame = QWidget(self)
        self.player.set_hwnd(self.video_frame.winId())

        self.stop_button = QPushButton("Dừng xem video", self)
        self.stop_button.clicked.connect(self.stop_video)
        self.stop_button.setEnabled(False)  # Vô hiệu hóa nút dừng ban đầu

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_frame)
        layout.addWidget(self.stop_button)

        self.player.play()
        self.showFullScreen()

        # Timer để kiểm tra thời gian phát video
        self.check_time_timer = QTimer(self)
        self.check_time_timer.timeout.connect(self.check_video_time)
        self.check_time_timer.start(1000)  # Kiểm tra mỗi giây
        
    def check_video_time(self):
        """Kiểm tra thời gian phát video và kích hoạt nút dừng."""
        # Thời gian đã phát (tính bằng mili giây)
        current_time = self.player.get_time()  
        # Thời lượng video (tính bằng mili giây)
        video_duration = self.media.get_duration() 

        if current_time >= video_duration // 2:
            self.stop_button.setEnabled(True)  # Kích hoạt nút dừng
            self.check_time_timer.stop()  # Dừng timer

    def update_video_frame(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimage = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimage))
        else:
            self.timer.stop()

    def update_watch_timer(self):
        """Cập nhật thời gian xem và kích hoạt nút dừng."""
        self.remaining_seconds -= 1
        if self.remaining_seconds < 0:
            self.stop_button.setEnabled(True)  # Kích hoạt nút dừng
            self.watch_timer.stop()

    def get_video_duration(self, file_path):
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps
            cap.release()
            return int(duration)
        else:
            return None

    def stop_video(self):
        self.player.stop()
        self.close()

    def closeEvent(self, event):
        """Hiển thị thông báo khi cố gắng đóng cửa sổ."""
        if not self.stop_button.isEnabled():  # Kiểm tra nút dừng đã được kích hoạt hay chưa
            QMessageBox.warning(self, "Thông báo", "Hãy cố gắng xem hết video em nhé!")
            event.ignore()  # Ngăn chặn việc đóng cửa sổ
        else:
            event.accept()  # Cho phép đóng cửa sổ
            

class Main(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("gui/menu.ui", self)
        self.phone_validator = QIntValidator()
        self.phone_validator.setBottom(0)
        self.phone_validator.setTop(999999999)
        self.HocSinh_btn.clicked.connect(self.Login_hs)
        self.GiaoVien_btn.clicked.connect(self.Login_tc)
        self.Register_btn.clicked.connect(self.regis)
        self.quit_btn.clicked.connect(self.quit)
        
        self.chon_hs_combo = QComboBox()
        self.load_data()

        self.teacher_login = None
        self.student_login = None
        self.register = None
        self.teacher_main = None
        self.student_main = None
        self.renewpass = None
        self.btvn_upload = None
        self.chon_hoc_sinh_dialog = None
        self.nhap_diem_dialog = None
        self.sua_thong_tin_dialog = None
        self.sua_diem_dialog = None
        self.xem_bai_tap_dialog = None
        
        
        # Khởi tạo các widget cho hộp thoại "Nhập điểm" một lần duy nhất
        self.nhap_diem_dialog = None
        self.combo_hk = None
        self.combo_mon = None
        self.tx1 = None
        self.tx2 = None
        self.tx3 = None
        self.tx4 = None
        self.gk = None
        self.hk = None
        self.luu_btn = None
        self.grid_layout = None

        # Khởi tạo các widget cho hộp thoại "Sửa điểm" một lần duy nhất
        self.sua_diem_dialog = None
        self.combo_hk_sua = None
        self.combo_mon_sua = None
        self.tx1_sua = None
        self.tx2_sua = None
        self.tx3_sua = None
        self.tx4_sua = None
        self.gk_sua = None
        self.hk_sua = None
        self.luu_btn_sua = None
        self.grid_layout_sua = None
        
        # Khởi tạo current_teacher_table và current_student_table
        self.current_teacher_table = None
        self.current_student_table = None
        self.current_user = None
        self.load_data()
        
        
        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Lỗi")
        self.msg_box.setIcon(QMessageBox.Icon.Warning)
        self.msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")

        # Khởi tạo QFileSystemWatcher
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.addPath("btvn")  # Theo dõi folder "btvn"
        self.file_watcher.directoryChanged.connect(self.show_new_assignment_notification)

        # Lưu thời gian lần đăng nhập cuối cùng của học sinh
        self.last_login_time = None


    def quit(self):
        window.close()
        
#===================================================================================================     
#      ___           ___           ___           ___           ___             ___           ___
#     /\  \         /\  \         /\  \         /\  \         /\__\           /\  \         /\  \
#     \:\  \       /::\  \       /::\  \       /::\  \       /:/  /          /::\  \       /::\  \
#      \:\  \     /:/\:\  \     /:/\:\  \     /:/\:\  \     /:/__/          /:/\:\  \     /:/\:\  \
#      /::\  \   /::\~\:\  \   /::\~\:\  \   /:/  \:\  \   /::\  \ ___     /::\~\:\  \   /::\~\:\  \
#     /:/\:\__\ /:/\:\ \:\__\ /:/\:\ \:\__\ /:/__/ \:\__\ /:/\:\  /\__\   /:/\:\ \:\__\ /:/\:\ \:\__\
#    /:/  \/__/ \:\~\:\ \/__/ \/__\:\/:/  / \:\  \  \/__/ \/__\:\/:/  /   \:\~\:\ \/__/ \/_|::\/:/  /
#   /:/  /       \:\ \:\__\        \::/  /   \:\  \            \::/  /     \:\ \:\__\      |:|::/  /
#   \/__/         \:\ \/__/        /:/  /     \:\  \           /:/  /       \:\ \/__/      |:|\/__/
#                  \:\__\         /:/  /       \:\__\         /:/  /         \:\__\        |:|  |
#                   \/__/         \/__/         \/__/         \/__/           \/__/         \|__|
#===================================================================================================


    def Login_tc(self):
        if not self.teacher_login:
            self.teacher_login = uic.loadUi("gui/login-teacher.ui")
            self.PhoneTC = self.teacher_login.findChild(QLineEdit, "PhoneTC")
            self.PhoneTC.setValidator(self.phone_validator)
            self.PassTC = self.teacher_login.findChild(QLineEdit, "PassTC")
            self.teacher_login.GiaoVienLogin_btn.clicked.connect(self.check_login)
            self.teacher_login.goback_tc_btn.clicked.connect(self.goback_tc_Clicked)
            self.teacher_login.forgo_pass_tc.clicked.connect(self.renew)

        self.teacher_login.show()
        self.hide()

    def check_login(self):
        Phone = self.PhoneTC.text()
        password = self.PassTC.text()
        
        if not Phone:
            self.msg_box.setText("Vui lòng nhập số điện thoại!")
            self.msg_box.exec()
            return
        if not password:
            self.msg_box.setText("Vui lòng nhập mật khẩu!")
            self.msg_box.exec()
            return
            
        phone_number = self.PhoneTC.text()
        if len(phone_number) != 10 or not phone_number.startswith('0'):
            self.msg_box.setText("Số điện thoại không hợp lệ!")
            self.msg_box.exec()
            return
        
        if Phone == "0987654321" and password == "admin":
            self.close()
            self.GiaoVienClicked()
        else:
            self.msg_box.setText("Số điện thoại hoặc mật khẩu sai")
            self.msg_box.exec()
        
    def GiaoVienClicked(self):
        if not self.teacher_main:
            self.teacher_main = uic.loadUi("gui/main-tc.ui")
            self.teacher_main.logOut_btn_tc.clicked.connect(self.GiaoVienMain_Return)
            
            self.teacher_main.add_btn.clicked.connect(self.add_information)
            self.teacher_main.nhap_diem_mon_btn.clicked.connect(self.show_chon_hoc_sinh_dialog)
            self.teacher_main.update_btn.clicked.connect(self.show_sua_thong_tin_dialog)
            self.teacher_main.delete_btn.clicked.connect(self.delete_information)
            self.teacher_main.search_btn.clicked.connect(self.search)
            self.teacher_main.clear_btn.clicked.connect(self.clear_information)
            self.teacher_main.xem_bai_tap.clicked.connect(self.show_xem_bai_tap_dialog)
            self.teacher_main.btvn_upload_btn.clicked.connect(self.upload_btvn)

            self.table = self.teacher_main.findChild(QTabWidget, "Semester_tab")
            self.tab_widget = self.teacher_main.findChild(QTabWidget, "Semester_tab")
            self.table_HK1 = self.teacher_main.findChild(QTableWidget, "student_Infor_table_HK1")
            self.table_HK2 = self.teacher_main.findChild(QTableWidget, "student_Infor_table_HK2")
            self.table_CN = self.teacher_main.findChild(QTableWidget, "student_Infor_table_CN")
            self.xem_hk1 = self.teacher_main.findChild(QComboBox, "xem_diem_mon_hk1")
            self.xem_hk2 = self.teacher_main.findChild(QComboBox, "xem_diem_mon_hk2")
            self.xem_cn = self.teacher_main.findChild(QComboBox, "xem_diem_mon_cn")
            self.search_bar = self.teacher_main.findChild(QLineEdit, "Search_bar")
            
            self.stt = self.teacher_main.findChild(QLineEdit, "so_thu_tu")    
            self.ho = self.teacher_main.findChild(QLineEdit, "ho")
            self.ten = self.teacher_main.findChild(QLineEdit, "ten")        
            
            
            self.tab_widget.currentChanged.connect(self.on_tab_changed)
            self.on_tab_changed(self.tab_widget.currentIndex())

            self.setup_table(self.table_HK1, "Học kỳ 1")
            self.setup_table(self.table_HK2, "Học kỳ 2")
            self.setup_table(self.table_CN, "Cả năm")
            self.fill_tables()

            self.xem_hk1.currentTextChanged.connect(lambda text: self.show_column(self.table_HK1, text))
            self.xem_hk2.currentTextChanged.connect(lambda text: self.show_column(self.table_HK2, text))
            self.xem_cn.currentTextChanged.connect(lambda text: self.show_column(self.table_CN, text))

        self.teacher_main.show()
        self.teacher_login.hide()

    def on_tab_changed(self, index):
        """Cập nhật self.current_teacher_table dựa trên tab hiện tại của giáo viên."""
        if index == 0:
            self.current_teacher_table = self.table_HK1
        elif index == 1:
            self.current_teacher_table = self.table_HK2
        elif index == 2:
            self.current_teacher_table = self.table_CN

        # Cập nhật lại combobox môn học cho tab hiện tại
        self.update_subject_combobox()
            
    def load_data(self):
        """Load data from JSON file and sort students."""
        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"Danh_sach_hoc_sinh": []}
        except Exception as e:
            print(f"Lỗi khi đọc file diem_database.json: {e}")

        self.sort_students()  # Sort students after loading data

    def save_data(self):
        """Sort students before saving data to JSON file."""
        self.sort_students()
        with open("diem_database.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def sort_students(self):
        """Sort students based on their "Số thứ tự" in ascending order."""
        self.data["Danh_sach_hoc_sinh"].sort(key=lambda student: int(student.get("Số thứ tự", 0)))

    def setup_table(self, table, semester):
        """Thiết lập bảng, bao gồm cả bảng điểm trung bình cả năm."""
        if semester == "Cả năm":
            column_count = 8  # STT, Họ, Tên, GK1, HK1, GK2, HK2, ĐTBCN
            header_labels = ["STT", "Họ", "Tên", "GK1", "HK1", "GK2", "HK2", "ĐTBCN"]
        else:
            column_count = 11
            header_labels = [
                "Số thứ tự",
                "Họ",
                "Tên",
                "TX1",
                "TX2",
                "TX3",
                "TX4",
                "GK",
                "HK",
                "ĐTB",
                "Điểm TB môn cả năm",
            ]

        table.setColumnCount(column_count)
        table.setHorizontalHeaderLabels(header_labels)
        
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 40)
        table.setColumnWidth(5, 40)
        table.setColumnWidth(6, 40)
        table.setColumnWidth(7, 40)
        table.setColumnWidth(8, 40)
        table.setColumnWidth(9, 40)
        table.setColumnWidth(10, 50)

        table.setAlternatingRowColors(True)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        for i in range(table.columnCount()):
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

    def fill_tables(self):
        """Điền dữ liệu từ self.data vào bảng."""
        self.table_HK1.setRowCount(0)
        self.table_HK2.setRowCount(0)
        self.table_CN.setRowCount(0)

        for row, student in enumerate(self.data["Danh_sach_hoc_sinh"]):
            # Thêm thông tin học sinh vào các cột tương ứng
            row_position = self.table_HK1.rowCount()
            self.table_HK1.insertRow(row_position)
            self.table_HK2.insertRow(row_position)
            self.table_CN.insertRow(row_position)

            self.table_HK1.setItem(row, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
            self.table_HK1.setItem(row, 1, QTableWidgetItem(student.get("Họ", "")))
            self.table_HK1.setItem(row, 2, QTableWidgetItem(student.get("Tên", "")))

            self.table_HK2.setItem(row, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
            self.table_HK2.setItem(row, 1, QTableWidgetItem(student.get("Họ", "")))
            self.table_HK2.setItem(row, 2, QTableWidgetItem(student.get("Tên", "")))

            self.table_CN.setItem(row, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
            self.table_CN.setItem(row, 1, QTableWidgetItem(student.get("Họ", "")))
            self.table_CN.setItem(row, 2, QTableWidgetItem(student.get("Tên", "")))

            for i, subject in enumerate(
                [
                    "Toán",
                    "Văn",
                    "Anh",
                    "Khoa học tự nhiên",
                    "Lịch sử - địa lý",
                    "Tin học",
                    "Công nghệ",
                    "Giáo dục công dân",
                ]
            ):
                # Điền điểm cho học kỳ 1 và 2
                for semester_key, table in [
                    ("Học kỳ 1", self.table_HK1),
                    ("Học kỳ 2", self.table_HK2),
                ]:
                    if (
                        semester_key in student.get("Điểm trong năm", {})
                        and subject in student["Điểm trong năm"][semester_key]
                    ):
                        for j, grade_type in enumerate(
                            [
                                "TX1",
                                "TX2",
                                "TX3",
                                "TX4",
                                "GK1" if semester_key == "Học kỳ 1" else "GK2",
                                "HK1" if semester_key == "Học kỳ 1" else "HK2",
                                "ĐTBM",
                            ]
                        ):
                            column_index = 3 + j + i * 7  # 7 cột cho mỗi môn học trong table_HK1 và table_HK2
                            table.setItem(
                                row,
                                column_index,
                                QTableWidgetItem(
                                    str(
                                        student["Điểm trong năm"][semester_key][
                                            subject
                                        ].get(grade_type, "")
                                    )
                                ),
                            )
                # Điền điểm trung bình cả năm
                try:
                    gk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("GK1", "0")
                    gk1 = float(gk1_str) if gk1_str else 0.0
                    hk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("HK1", "0")
                    hk1 = float(hk1_str) if hk1_str else 0.0
                    gk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("GK2", "0")
                    gk2 = float(gk2_str) if gk2_str else 0.0
                    hk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("HK2", "0")
                    hk2 = float(hk2_str) if hk2_str else 0.0

                    dtbm_cn = (gk1 + hk1 + (gk2 + hk2) * 2) / 6

                    self.table_CN.setItem(row, i * 5 + 3, QTableWidgetItem(str(gk1) if gk1 else ""))
                    self.table_CN.setItem(row, i * 5 + 4, QTableWidgetItem(str(hk1) if hk1 else ""))
                    self.table_CN.setItem(row, i * 5 + 5, QTableWidgetItem(str(gk2) if gk2 else ""))
                    self.table_CN.setItem(row, i * 5 + 6, QTableWidgetItem(str(hk2) if hk2 else ""))
                    self.table_CN.setItem(row, i * 5 + 7, QTableWidgetItem(f"{dtbm_cn:.2f}"))
                except KeyError:
                    for col in range(5):
                        self.table_CN.setItem(row, i * 5 + 3 + col, QTableWidgetItem(""))
                                        
    def show_column(self, table, subject):
            """Cập nhật dữ liệu cột dựa trên môn học được chọn."""
            for row in range(table.rowCount()):
                student = self.data["Danh_sach_hoc_sinh"][row]
                for semester_key in ["Học kỳ 1", "Học kỳ 2"]:
                    if semester_key in student.get("Điểm trong năm", {}) and subject in student["Điểm trong năm"][semester_key]:
                        for j, grade_type in enumerate(
                            [
                                "TX1",
                                "TX2",
                                "TX3",
                                "TX4",
                                "GK1" if semester_key == "Học kỳ 1" else "GK2",
                                "HK1" if semester_key == "Học kỳ 1" else "HK2",
                                "ĐTBM",
                            ]
                        ):
                            column_index = 3 + j  # Vị trí cột bắt đầu từ cột 3
                            table.setItem(
                                row,
                                column_index,
                                QTableWidgetItem(
                                    str(student["Điểm trong năm"][semester_key][subject].get(grade_type, ""))
                                ),
                            )

    def search(self):
        text = self.search_bar.text().strip().lower()
        for row in range(self.table_HK1.rowCount()):
            match = False
            for column in range(self.table_HK1.columnCount()):
                item = self.table_HK1.item(row, column)
                if item and text in item.text().strip().lower():
                    match = True
                    break
            self.table_HK1.setRowHidden(row, not match)

        for row in range(self.table_HK2.rowCount()):
            match = False
            for column in range(self.table_HK2.columnCount()):
                item = self.table_HK2.item(row, column)
                if item and text in item.text().strip().lower():
                    match = True
                    break
            self.table_HK2.setRowHidden(row, not match)

        for row in range(self.table_CN.rowCount()):
            match = False
            for column in range(self.table_CN.columnCount()):
                item = self.table_CN.item(row, column)
                if item and text in item.text().strip().lower():
                    match = True
                    break
            self.table_CN.setRowHidden(row, not match)

    def show_chon_hoc_sinh_dialog(self):
        if not self.chon_hoc_sinh_dialog:
            self.chon_hoc_sinh_dialog = QDialog(self)
            self.chon_hoc_sinh_dialog.setWindowTitle("Chọn học sinh")

            layout = QVBoxLayout()
            # Gán giá trị cho thuộc tính chon_hs_combo
            self.chon_hs_combo = QComboBox()
            for student in self.data["Danh_sach_hoc_sinh"]:
                self.chon_hs_combo.addItem(f"{student.get('Họ', '')} {student.get('Tên', '')}")
            layout.addWidget(self.chon_hs_combo)

            chon_btn = QPushButton("Chọn")
            chon_btn.clicked.connect(self.show_nhap_diem_dialog)
            layout.addWidget(chon_btn)

            self.chon_hoc_sinh_dialog.setLayout(layout)
        self.chon_hoc_sinh_dialog.show()

    def show_nhap_diem_dialog(self):
        if not self.nhap_diem_dialog:
            self.nhap_diem_dialog = QDialog(self)
            self.nhap_diem_dialog.setWindowTitle("Nhập điểm")

            layout = QVBoxLayout()
            self.nhap_diem_dialog.setLayout(layout)

            label_hk = QLabel("Chọn học kỳ:")
            self.combo_hk = QComboBox()
            self.combo_hk.addItems(["Học kỳ 1", "Học kỳ 2"])
            self.combo_hk.currentTextChanged.connect(self.update_nhap_diem_dialog)
            layout.addWidget(label_hk)
            layout.addWidget(self.combo_hk)

            self.grid_layout = QGridLayout()
            self.create_nhap_diem_form("Học kỳ 1")
            layout.addLayout(self.grid_layout)

        self.nhap_diem_dialog.show()

    def update_nhap_diem_dialog(self, text):
        self.grid_layout.deleteLater()
        self.grid_layout = QGridLayout()  # Tạo layout mới 
        self.create_nhap_diem_form(text)
        self.nhap_diem_dialog.layout().addLayout(self.grid_layout)    
        
    def create_nhap_diem_form(self, hoc_ki):
        # Xóa layout cũ nếu có
        if self.grid_layout is not None:
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        else:
            self.grid_layout = QGridLayout()

        self.grid_layout.addWidget(QLabel("Môn học:"), 0, 0)
        self.combo_mon = QComboBox()
        self.combo_mon.addItems(
            [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]
        )
        self.grid_layout.addWidget(self.combo_mon, 0, 1)
        self.grid_layout.addWidget(QLabel("TX1:"), 1, 0)
        self.tx1 = QLineEdit()
        self.grid_layout.addWidget(self.tx1, 1, 1)
        self.grid_layout.addWidget(QLabel("TX2:"), 2, 0)
        self.tx2 = QLineEdit()
        self.grid_layout.addWidget(self.tx2, 2, 1)
        self.grid_layout.addWidget(QLabel("TX3:"), 3, 0)
        self.tx3 = QLineEdit()
        self.grid_layout.addWidget(self.tx3, 3, 1)
        self.grid_layout.addWidget(QLabel("TX4:"), 4, 0)
        self.tx4 = QLineEdit()
        self.grid_layout.addWidget(self.tx4, 4, 1)
        self.grid_layout.addWidget(QLabel("GK:"), 5, 0)
        self.gk = QLineEdit()
        self.grid_layout.addWidget(self.gk, 5, 1)
        self.grid_layout.addWidget(QLabel("HK:"), 6, 0)
        self.hk = QLineEdit()
        self.grid_layout.addWidget(self.hk, 6, 1)
        self.luu_btn = QPushButton("Lưu")
        self.luu_btn.clicked.connect(self.nhap_diem_luu)
        self.grid_layout.addWidget(self.luu_btn, 7, 0, 1, 2)
        

    def nhap_diem_luu(self):
        """Lưu điểm đã nhập vào self.data và cập nhật bảng."""
        selected_student_index = self.chon_hs_combo.currentIndex()
        if selected_student_index == -1:
            return

        hoc_ki = self.combo_hk.currentText()
        mon_hoc = self.combo_mon.currentText()
        tx1 = self.tx1.text()
        tx2 = self.tx2.text()
        tx3 = self.tx3.text()
        tx4 = self.tx4.text()
        gk = self.gk.text()
        hk = self.hk.text()

        student = self.data["Danh_sach_hoc_sinh"][selected_student_index]

        # Đảm bảo cấu trúc dữ liệu chính xác
        if "Điểm trong năm" not in student:
            student["Điểm trong năm"] = {}
        if hoc_ki not in student["Điểm trong năm"]:
            student["Điểm trong năm"][hoc_ki] = {}
        if mon_hoc not in student["Điểm trong năm"][hoc_ki]:
            student["Điểm trong năm"][hoc_ki][mon_hoc] = {}

        # Lưu điểm vào cấu trúc dữ liệu
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX1"] = tx1
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX2"] = tx2
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX3"] = tx3
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX4"] = tx4
        student["Điểm trong năm"][hoc_ki][mon_hoc]["GK1" if hoc_ki == "Học kỳ 1" else "GK2"] = gk
        student["Điểm trong năm"][hoc_ki][mon_hoc]["HK1" if hoc_ki == "Học kỳ 1" else "HK2"] = hk

        dtbm = self.calculate_dtbm(tx1, tx2, tx3, tx4, gk, hk)
        if dtbm is not None:
            student["Điểm trong năm"][hoc_ki][mon_hoc]["ĐTBM"] = f"{dtbm:.2f}"

        # Lưu dữ liệu JSON đã cập nhật
        self.save_data()

        self.fill_tables()  # Cập nhật tất cả các bảng
        self.nhap_diem_dialog.close()
        
    def update_diem_trung_binh_ca_nam(self, student_index, subject):
        """Cập nhật cột Điểm TB môn cả năm trong bảng."""
        student = self.data["Danh_sach_hoc_sinh"][student_index]

        try:
            dtbm_hk1 = float(
                student["Điểm trong năm"]["Học kỳ 1"][subject]["ĐTBM"]
            )
            dtbm_hk2 = float(
                student["Điểm trong năm"]["Học kỳ 2"][subject]["ĐTBM"]
            )
            dtbm_cn = (dtbm_hk1 + (dtbm_hk2 * 2)) / 3

            column_index = 4 + [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ].index(subject)

            self.table_CN.setItem(
                student_index, column_index, QTableWidgetItem(f"{dtbm_cn:.2f}")
            )

        except KeyError:
            # Xử lý trường hợp thiếu điểm
            column_index = 4 + [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ].index(subject)
            self.table_CN.setItem(student_index, column_index, QTableWidgetItem(""))
        
    def update_table_after_nhap_diem(self, hoc_ki, row_index, mon_hoc):
        """Cập nhật table sau khi nhập điểm."""
        student = self.data["Danh_sach_hoc_sinh"][row_index]
        if hoc_ki == "Học kỳ 1":
            table = self.table_HK1
        elif hoc_ki == "Học kỳ 2":
            table = self.table_HK2
        else:
            return

        subject_order = [
            "Toán",
            "Văn",
            "Anh",
            "Khoa học tự nhiên",
            "Lịch sử - địa lý",
            "Tin học",
            "Công nghệ",
            "Giáo dục công dân",
        ]
        if mon_hoc in subject_order:
            column_index = 4 + subject_order.index(mon_hoc)

            # Check if semester and subject exist
            if (
                hoc_ki in student["Điểm trong năm"]
                and mon_hoc in student["Điểm trong năm"][hoc_ki]
            ):
                for j, grade_type in enumerate(
                    [
                        "TX1",
                        "TX2",
                        "TX3",
                        "TX4",
                        "GK1" if hoc_ki == "Học kỳ 1" else "GK2",
                        "HK1" if hoc_ki == "Học kỳ 1" else "HK2",
                        "ĐTBM",
                    ]
                ):
                    # Create subject key if it doesn't exist
                    if grade_type not in student["Điểm trong năm"][hoc_ki][mon_hoc]:
                        student["Điểm trong năm"][hoc_ki][mon_hoc][grade_type] = ""
                    
                    table.setItem(
                        row_index,
                        column_index + j,
                        QTableWidgetItem(
                            str(student["Điểm trong năm"][hoc_ki][mon_hoc].get(grade_type, ""))
                        ),
                    )

    def calculate_dtbm(self, tx1, tx2, tx3, tx4, gk, hk):
        try:
            tx1 = float(tx1)
            tx2 = float(tx2)
            tx3 = float(tx3)
            tx4 = float(tx4)
            gk = float(gk)
            hk = float(hk)
            dtbm = ((tx1 + tx2 + tx3 + tx4) + (gk * 2) + (hk * 3)) / 9
            return dtbm
        except ValueError:
            self.msg_box.setText("Vui lòng nhập số cho điểm.")
            self.msg_box.exec()
            return 0

    def show_sua_thong_tin_dialog(self):
        """Hiển thị hộp thoại để sửa thông tin học sinh."""
        current_row = self.current_teacher_table.currentRow()
        self.sua_thong_tin_dialog = QDialog(self)
        self.sua_thong_tin_dialog.setWindowTitle("Thêm thông tin học sinh")
        layout = QGridLayout()

        layout.addWidget(QLabel("Số thứ tự:"), 1, 0)
        self.stt = self.teacher_main.findChild(QLineEdit, "so_thu_tu") # Sử dụng QLineEdit "so_thu_tu" có sẵn
        layout.addWidget(self.stt, 1, 1)

        layout.addWidget(QLabel("Họ:"), 2, 0)
        self.ho = self.teacher_main.findChild(QLineEdit, "ho")  # Sử dụng QLineEdit "ho" có sẵn
        layout.addWidget(self.ho, 2, 1)

        layout.addWidget(QLabel("Tên:"), 3, 0)
        self.ten = self.teacher_main.findChild(QLineEdit, "ten")  # Sử dụng QLineEdit "ten" có sẵn
        layout.addWidget(self.ten, 3, 1)

        luu_btn = QPushButton("Lưu")
        luu_btn.clicked.connect(self.add_information_to_table)
        layout.addWidget(luu_btn, 4, 0, 1, 2)

        self.sua_thong_tin_dialog.setLayout(layout)

    def show_sua_thong_tin_dialog(self):
        """Hiển thị hộp thoại để sửa thông tin học sinh."""
        current_row = self.table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]
            self.sua_thong_tin_dialog = QDialog(self)
            self.sua_thong_tin_dialog.setWindowTitle("Sửa thông tin học sinh")
            layout = QGridLayout()

            layout.addWidget(QLabel("Số thứ tự:"), 0, 0)
            self.stt_edit = QLineEdit(student["Số thứ tự"])  # Use a different name
            layout.addWidget(self.stt_edit, 0, 1)

            layout.addWidget(QLabel("Họ:"), 1, 0)
            self.ho_edit = QLineEdit(student["Họ"])  # Use a different name
            layout.addWidget(self.ho_edit, 1, 1)

            layout.addWidget(QLabel("Tên:"), 2, 0)
            self.ten_edit = QLineEdit(student["Tên"])  # Use a different name
            layout.addWidget(self.ten_edit, 2, 1)

            luu_btn = QPushButton("Lưu")
            luu_btn.clicked.connect(self.update_thong_tin_hoc_sinh)
            layout.addWidget(luu_btn, 3, 0, 1, 2)

            self.sua_thong_tin_dialog.setLayout(layout)
            self.sua_thong_tin_dialog.show()
        else:
            self.msg_box.setText("Vui lòng chọn học sinh để sửa thông tin.")
            self.msg_box.exec()

    def update_thong_tin_hoc_sinh(self):
        """Cập nhật thông tin học sinh từ hộp thoại sửa."""
        current_row = self.current_teacher_table.currentRow() # Sử dụng current_teacher_table
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]
            student["Số thứ tự"] = self.stt_edit.text()  # Update with edited values
            student["Họ"] = self.ho_edit.text()
            student["Tên"] = self.ten_edit.text()

            # Update the table directly
            self.table.setItem(current_row, 0, QTableWidgetItem(student["Số thứ tự"]))
            self.table.setItem(current_row, 1, QTableWidgetItem(student["Họ"]))
            self.table.setItem(current_row, 2, QTableWidgetItem(student["Tên"]))

            self.save_data()
            self.sua_thong_tin_dialog.close()
            
    def show_sua_diem_dialog(self):
        if not self.sua_diem_dialog:
            self.sua_diem_dialog = QDialog(self)
            self.sua_diem_dialog.setWindowTitle("Sửa điểm học sinh")
            layout = QGridLayout()
            self.sua_diem_dialog.setLayout(layout)  

            layout.addWidget(QLabel("Chọn học kỳ:"), 0, 0)
            self.combo_hk_sua = QComboBox()
            self.combo_hk_sua.addItems(["Học kỳ 1", "Học kỳ 2"])
            self.combo_hk_sua.currentTextChanged.connect(self.update_sua_diem_dialog)
            layout.addWidget(self.combo_hk_sua, 0, 1)

            self.grid_layout_sua = QGridLayout()
            self.create_sua_diem_form("Học kỳ 1")
            layout.addLayout(self.grid_layout_sua, 1, 0, 1, 2)

        self.sua_diem_dialog.show()

    def update_sua_diem_dialog(self, text):
        current_row = self.current_teacher_table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]
            self.create_sua_diem_form(text, student)

    def create_sua_diem_form(self, hoc_ki, student=None):  # Thêm tham số student
        # Xóa layout cũ nếu có
        if self.grid_layout_sua is not None:
            while self.grid_layout_sua.count():
                item = self.grid_layout_sua.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        else:
            self.grid_layout_sua = QGridLayout()

        self.grid_layout_sua.addWidget(QLabel("Môn học:"), 0, 0)
        self.combo_mon_sua = QComboBox()
        self.combo_mon_sua.addItems(
            [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]
        )
        self.combo_mon_sua.currentTextChanged.connect(
            lambda text: self.update_sua_diem_form_mon_hoc(text, student)
        )  # Truyền student khi cập nhật môn học
        self.grid_layout_sua.addWidget(self.combo_mon_sua, 0, 1)

        self.update_sua_diem_form_mon_hoc("Toán", student)  # Truyền student khi khởi tạo

    def update_sua_diem_form_mon_hoc(self, mon_hoc, student=None):
        if student is None:
            return

        # Lấy chỉ số dòng hiện tại
        current_row = self.current_teacher_table.currentRow() 
        if current_row == -1:
            return
        
        hoc_ki = self.combo_hk_sua.currentText()

        # Cập nhật giá trị cho các QLineEdit dựa trên môn học được chọn
        self.tx1_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("TX1", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.tx2_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("TX2", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.tx3_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("TX3", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.tx4_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("TX4", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.gk_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("GK1" if hoc_ki == "Học kỳ 1" else "GK2", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.hk_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get("HK1" if hoc_ki == "Học kỳ 1" else "HK2", "")
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        
        self.fill_tables()
        self.save_data()  # Lưu dữ liệu JSON đã cập nhật
        
        

    def update_diem_hoc_sinh(self):
        current_row = self.current_teacher_table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]

        hoc_ki = self.combo_hk_sua.currentText()
        mon_hoc = self.combo_mon_sua.currentText()
        if hoc_ki in student["Điểm trong năm"] and mon_hoc in student["Điểm trong năm"][hoc_ki]:
            # Cập nhật điểm trong self.data
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX1"] = self.tx1_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX2"] = self.tx2_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX3"] = self.tx3_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX4"] = self.tx4_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["GK1" if hoc_ki == "Học kỳ 1" else "GK2"] = self.gk_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["HK1" if hoc_ki == "Học kỳ 1" else "HK2"] = self.hk_sua.text()

            # Tính toán lại điểm trung bình môn
            dtbm = self.calculate_dtbm(self.tx1_sua.text(), self.tx2_sua.text(), self.tx3_sua.text(),
                                       self.tx4_sua.text(), self.gk_sua.text(), self.hk_sua.text())
            if dtbm is not None:
                student["Điểm trong năm"][hoc_ki][mon_hoc]["ĐTBM"] = f"{dtbm:.2f}"
            
            # Cập nhật điểm trung bình cả năm
            self.update_diem_trung_binh_ca_nam(current_row, mon_hoc)

        # Cập nhật lại bảng
        self.fill_tables()
        
        self.save_data()  # Lưu dữ liệu JSON đã cập nhật
        self.sua_diem_dialog.close()
        
    def add_information(self):
        # Kiểm tra xem người dùng đã nhập đủ thông tin hay chưa
        if not self.stt.text() or not self.ho.text() or not self.ten.text():
            self.msg_box.setText("Vui lòng nhập đầy đủ thông tin!")
            self.msg_box.exec()
            return

        # Get the text from the QLineEdit
        stt = self.stt.text()

        # Now validate the stt string 
        if not stt or len(stt) != 5 or not stt.isdigit() or int(stt[2:]) == 0:
            self.msg_box.setText("Số thứ tự không hợp lệ. Vui lòng nhập theo định dạng 'Số lớp - Số thứ tự' (ví dụ: 88041).")
            self.msg_box.exec()
            return

        # Khởi tạo biến new_student với thông tin học sinh mới
        new_student = {
            "Số thứ tự": stt,
            "Họ": self.ho.text(),
            "Tên": self.ten.text(),
            "Điểm trong năm": {
                "Học kỳ 1": {
                    "Toán": {},
                    "Văn": {},
                    "Anh": {},
                    "Khoa học tự nhiên": {},
                    "Lịch sử - địa lý": {},
                    "Tin học": {},
                    "Công nghệ": {},
                    "Giáo dục công dân": {},
                },
                "Học kỳ 2": {
                    "Toán": {},
                    "Văn": {},
                    "Anh": {},
                    "Khoa học tự nhiên": {},
                    "Lịch sử - địa lý": {},
                    "Tin học": {},
                    "Công nghệ": {},
                    "Giáo dục công dân": {},
                },
            },
        }

        # Thêm thông tin điểm trung bình cả năm (khởi tạo là null)
        new_student["Điểm trung bình cả năm"] = {
            "Học kỳ 1": {subject: {"GK1": None, "HK1": None} for subject in [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]},
            "Học kỳ 2": {subject: {"GK2": None, "HK2": None} for subject in [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]}
        }

        self.data["Danh_sach_hoc_sinh"].append(new_student)

        # Cập nhật combobox chọn học sinh
        self.chon_hs_combo.addItem(f"{new_student['Họ']} {new_student['Tên']}")

        # Lưu dữ liệu vào file JSON
        self.save_data()

        # Cập nhật bảng sau khi thêm
        self.fill_tables()

        # Xóa nội dung trong các QLineEdit
        self.stt.clear()
        self.ho.clear()
        self.ten.clear()

    def update_subject_combobox(self):
        """Cập nhật combobox môn học dựa trên tab hiện tại của giáo viên."""
        if self.current_teacher_table is self.table_HK1: # Sử dụng current_teacher_table
            combobox = self.xem_hk1
        elif self.current_teacher_table is self.table_HK2:
            combobox = self.xem_hk2
        elif self.current_teacher_table is self.table_CN:
            combobox = self.xem_cn
        else:
            return

        combobox.clear()
        combobox.addItem("")
        combobox.addItems(
            [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]
        )

    def clear_information(self):
        self.msg_box.setText(
            "Hệ thống đang thông báo đến hiệu trưởng. Đang chờ hiệu trưởng đồng ý hoặc không đồng ý."
        )
        self.msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.msg_box.exec()

        approval = random.choice(["Đồng ý", "Không đồng ý"])

        if approval == "Đồng ý":
            confirm_box = QMessageBox()
            confirm_box.setWindowTitle("Thông báo")
            confirm_box.setIcon(QMessageBox.Icon.Information)
            confirm_box.setText("Hiệu trưởng đã đồng ý. Toàn bộ học sinh sẽ bị xóa.")
            confirm_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")
            confirm_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            
            result = confirm_box.exec()
            if result == QMessageBox.StandardButton.Ok:
                self._clear_all_fields()
        else:
            confirm_box = QMessageBox()
            confirm_box.setWindowTitle("Thông báo")
            confirm_box.setIcon(QMessageBox.Icon.Information)
            confirm_box.setText("Hiệu trưởng không đồng ý.")
            confirm_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")
            confirm_box.exec()

    def _clear_all_fields(self):
        self.data["Danh_sach_hoc_sinh"] = []
        self.fill_tables()

    def delete_information(self):
        current_row = self.current_teacher_table.currentRow() # Sử dụng current_teacher_table
        if current_row != -1:
            # Remove student from data dictionary
            del self.data["Danh_sach_hoc_sinh"][current_row]

            # Update the tables
            self.fill_tables()

            # Save the updated data to JSON file
            self.save_data()

    def GiaoVienMain_Return(self):
        self.teacher_main.hide()
        self.show()

    def goback_tc_Clicked(self):
        self.teacher_login.hide()
        self.show()
        
    def goback_hs_Clicked(self):
        self.student_login.hide()
        self.show()

    def renew(self):
        if not self.renewpass:
            self.renewpass = uic.loadUi("gui/renewpass.ui")
            self.renewpass.renew_btn.clicked.connect(self.renew_Clicked)
            self.renewpass.return_btn.clicked.connect(self.renew_Return)
            self.phone_validator = QIntValidator()
            self.phone_validator.setBottom(0)
            self.phone_validator.setTop(999999999)
            self.renewpass.PhoneRC.setValidator(self.phone_validator)
            self.renewpass.PassRC.setEchoMode(QLineEdit.EchoMode.Password)
            self.renewpass.RePassRC.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.renewpass.show()
        self.hide()

    def renew_Clicked(self):
        Phone = self.renewpass.PhoneRC.text()
        password = self.renewpass.PassRC.text()
        repass = self.renewpass.RePassRC.text()
        
        if not Phone:
            self.msg_box.setText("vui lòng nhập số điện thoại!")
            self.msg_box.exec()
            return
        if not password:
            self.msg_box.setText("vui lòng nhập mật khẩu!")
            self.msg_box.exec()
            return
        if not repass:
            self.msg_box.setText("vui lòng nhập lại mật khẩu!")
            self.msg_box.exec()
            return
        if password != repass:
            self.msg_box.setText("mật khẩu không trùng khớp!")
            self.msg_box.exec()
            return

        self.renewpass.hide()
        self.show()

    def renew_Return(self):
        self.renewpass.hide()
        self.teacher_login.show()
        
    def upload_btvn(self):
        if not self.btvn_upload:
            self.btvn_upload = uic.loadUi("gui/btvn-upload.ui")
            self.btvn_upload.clickTo_Upload.clicked.connect(self.upload_click)
            self.loai_file_combo = QComboBox(self.btvn_upload)  # Thêm combobox chọn loại file
            self.loai_file_combo.addItems(["Bài tập", "Video bài giảng"])
            self.btvn_upload.layout().addWidget(self.loai_file_combo)

        self.btvn_upload.show()
        self.hide()
        
    def upload_click(self):
        options = QFileDialog.Option.DontUseNativeDialog
        loai_file = self.loai_file_combo.currentText()
        if loai_file == "Bài tập":
            file_filter = "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx);;PowerPoint Presentations (*.pptx)"
        elif loai_file == "Video bài giảng":
            file_filter = "Video Files (*.mp4)"
        else:
            file_filter = "All Files (*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn file",
            "",
            file_filter,
            options=options,
        )

        if file_path:
            folder_path = os.path.join("btvn", loai_file)  # Tạo thư mục con theo loại file
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(folder_path, file_name)

            try:
                os.replace(file_path, destination_path)
                self.msg_box.setWindowTitle("Thông báo")
                self.msg_box.setIcon(QMessageBox.Icon.Information)
                self.msg_box.setText("Tải lên thành công!")
                self.msg_box.exec()

                if self.xem_bai_tap_dialog:
                    self.update_btvn_list()

            except Exception as e:
                self.msg_box.setText(f"Lỗi khi tải lên: {e}")
                self.msg_box.exec()

        self.btvn_upload.hide()
        self.teacher_main.show()

        
    def update_btvn_list(self):
        self.btvn_list.clear()
        self.video_list.clear()

        for loai_file in ["Bài tập", "Video bài giảng"]:
            folder_path = os.path.join("btvn", loai_file)
            if os.path.exists(folder_path):
                file_list = os.listdir(folder_path)
                if file_list:
                    for file_name in file_list:
                        if loai_file == "Bài tập":
                            self.btvn_list.addItem(file_name) # Thêm vào list bài tập
                        elif loai_file == "Video bài giảng":
                            self.video_list.addItem(file_name) # Thêm vào list video
                else:
                    if loai_file == "Bài tập":
                        self.btvn_list.addItem("Hiện tại không có bài tập")
                    elif loai_file == "Video bài giảng":
                        self.video_list.addItem("Hiện tại không có video bài giảng")
                
    def delete_btvn(self):
        selected_item = self.btvn_list.currentItem()
        if selected_item and selected_item.text() != "Hiện tại không có bài tập":
            file_name = selected_item.text()
            folder_path = "btvn"
            file_path = os.path.join(folder_path, file_name)

            confirm_box = QMessageBox()
            confirm_box.setWindowTitle("Xác nhận xóa")
            confirm_box.setText(f"Bạn có chắc muốn xóa {file_name}?")
            confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            
            result = confirm_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(file_path)
                    self.update_btvn_list()  # Cập nhật danh sách sau khi xóa
                    self.msg_box.setWindowTitle("Thông báo")
                    self.msg_box.setIcon(QMessageBox.Icon.Information)
                    self.msg_box.setText("Xóa bài tập thành công!")
                    self.msg_box.exec()
                except Exception as e:
                    self.msg_box.setText(f"Lỗi khi xóa: {e}")
                    self.msg_box.exec()

    def rename_btvn(self):
        selected_item = self.btvn_list.currentItem()
        if selected_item and selected_item.text() != "Hiện tại không có bài tập":
            old_file_name = selected_item.text()
            folder_path = "btvn"
            old_file_path = os.path.join(folder_path, old_file_name)

            new_file_name, ok = QInputDialog.getText(
                self, "Đổi tên bài tập", "Nhập tên mới:", text=old_file_name
            )
            if ok and new_file_name:
                new_file_path = os.path.join(folder_path, new_file_name)
                try:
                    os.rename(old_file_path, new_file_path)
                    self.update_btvn_list()  # Cập nhật danh sách sau khi đổi tên
                    self.msg_box.setWindowTitle("Thông báo")
                    self.msg_box.setIcon(QMessageBox.Icon.Information)
                    self.msg_box.setText("Đổi tên bài tập thành công!")
                    self.msg_box.exec()
                except Exception as e:
                    self.msg_box.setText(f"Lỗi khi đổi tên: {e}")
                    self.msg_box.exec()
                
    def download_btvn(self):
        selected_item = self.btvn_list.currentItem()
        if selected_item:
            file_name = selected_item.text()
            folder_path = "btvn"
            file_path = os.path.join(folder_path, file_name)

            options = QFileDialog.Option.DontUseNativeDialog
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Lưu Bài Tập",
                file_name,
                "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx);;PowerPoint Presentations (*.pptx)",
                options=options,
            )

            if save_path:
                try:
                    # Sao chép file từ thư mục "btvn" đến vị trí lưu
                    shutil.copy2(file_path, save_path)  # Sử dụng shutil.copy2()
                    self.msg_box.setWindowTitle("Thông báo")
                    self.msg_box.setIcon(QMessageBox.Icon.Information)
                    self.msg_box.setText("Tải xuống bài tập thành công!")
                    self.msg_box.exec()
                except Exception as e:
                    self.msg_box.setText(f"Lỗi khi tải xuống: {e}")
                    self.msg_box.exec()
        
    def show_xem_bai_tap_dialog(self):
        if not self.xem_bai_tap_dialog:
            self.xem_bai_tap_dialog = QDialog(self)
            self.xem_bai_tap_dialog.setWindowTitle("Xem Bài Tập và Video Bài Giảng")

            layout = QVBoxLayout()

            # Bài tập (dạng văn bản)
            self.btvn_list = QListWidget()
            layout.addWidget(QLabel("Bài tập:"))
            layout.addWidget(self.btvn_list)
            self.btvn_list.itemClicked.connect(self.download_btvn) # Xử lý sự kiện click

            # Các nút "Xóa", "Chỉnh Sửa Tên", "Tải Về" cho bài tập (dạng văn bản)
            delete_btn = QPushButton("Xóa")
            delete_btn.clicked.connect(self.delete_btvn)
            layout.addWidget(delete_btn)
            rename_btn = QPushButton("Chỉnh Sửa Tên")
            rename_btn.clicked.connect(self.rename_btvn)
            layout.addWidget(rename_btn)
            
            download_btn = QPushButton("Tải Về")
            download_btn.clicked.connect(self.download_btvn)
            layout.addWidget(download_btn)


            # Video bài giảng
            self.video_list = QListWidget()
            layout.addWidget(QLabel("Video bài giảng:"))
            layout.addWidget(self.video_list)
            self.video_list.itemDoubleClicked.connect(self.play_video_hs) # Xử lý sự kiện double click

            self.update_btvn_list()
            self.xem_bai_tap_dialog.setLayout(layout)

        self.xem_bai_tap_dialog.show()

    def return_upload(self):
        self.btvn_upload.hide()
        self.teacher_main.show()

    def regis(self):
        if not self.register:
            self.register = uic.loadUi("gui/register.ui")
            self.Phone_reg = self.register.findChild(QLineEdit, "Phone_reg")
            self.Phone_reg.setValidator(self.phone_validator)
            self.pass_reg = self.register.findChild(QLineEdit, "pass_reg")
            self.re_pass_reg = self.register.findChild(QLineEdit, "re_pass_reg")
            self.vai_tro = self.register.findChild(QComboBox, "vai_tro")
            self.vai_tro.addItems(["Giáo viên", "Học sinh"])
            self.register_btn = self.register.findChild(QPushButton, "register_btn")
            self.register_btn.clicked.connect(self.re_register)
            self.goback_reg = self.register.findChild(QPushButton, "goback_reg")
            self.goback_reg.clicked.connect(self.return_register)
            self.pass_reg.setEchoMode(QLineEdit.EchoMode.Password)
            self.re_pass_reg.setEchoMode(QLineEdit.EchoMode.Password)

        self.register.show()
        self.hide()

    def re_register(self):
        phone = self.Phone_reg.text()
        password = self.pass_reg.text()
        repass = self.re_pass_reg.text()
        vai_tro = self.vai_tro.currentText()

        if not all([phone, password, repass]):
            self.msg_box.setText("Vui lòng điền đầy đủ thông tin!")
            self.msg_box.exec()
            return
        if password != repass:
            self.msg_box.setText("Mật khẩu không khớp!")
            self.msg_box.exec()
            return

        # Hiển thị dialog để nhập thêm thông tin
        dialog = QDialog(self)
        dialog.setWindowTitle("Thông tin bổ sung")
        layout = QGridLayout(dialog)

        name_label = QLabel("Tên:")
        name_edit = QLineEdit(dialog)
        layout.addWidget(name_label, 0, 0)
        layout.addWidget(name_edit, 0, 1)

        age_label = QLabel("Tuổi:")
        age_edit = QLineEdit(dialog)
        age_edit.setValidator(QIntValidator())
        layout.addWidget(age_label, 1, 0)
        layout.addWidget(age_edit, 1, 1)

        birthday_label = QLabel("Ngày sinh (dd-mm-yyyy):")
        birthday_edit = QLineEdit(dialog)
        layout.addWidget(birthday_label, 2, 0)
        layout.addWidget(birthday_edit, 2, 1)

        gender_label = QLabel("Giới tính:")
        gender_combo = QComboBox(dialog)
        gender_combo.addItems(["Nam", "Nữ"])
        layout.addWidget(gender_label, 3, 0)
        layout.addWidget(gender_combo, 3, 1)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box, 4, 0, 1, 2)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            ten_tai_khoan = name_edit.text()
            age = age_edit.text()
            birthday = birthday_edit.text()
            gender = gender_combo.currentText()

            if vai_tro == "Giáo viên":
                self.luu_tai_khoan_giao_vien(phone, password, ten_tai_khoan, age, birthday, gender)
                # Lưu thông tin tài khoản mới và chuyển đến giao diện đăng nhập
                self.new_account_info = {"PhoneTC": phone, "PassTC": password}
                self.return_register()  # Ẩn giao diện đăng ký
                self.Login_tc()  # Hiển thị giao diện đăng nhập
                self.PhoneTC.setText(phone)  # Điền số điện thoại
                self.PassTC.setText(password)  # Điền mật khẩu
                self.check_login()  # Mô phỏng thao tác nhấn nút đăng nhập
            elif vai_tro == "Học sinh":
                so_thu_tu = self.random_so_thu_tu()
                self.luu_tai_khoan_hoc_sinh(so_thu_tu, ten_tai_khoan, password, phone, birthday, age, gender)
                # Lưu thông tin tài khoản mới và chuyển đến giao diện đăng nhập
                self.new_account_info = {"id_hs": so_thu_tu, "pass_HS": password}
                self.return_register()  # Ẩn giao diện đăng ký
                self.Login_hs()  # Hiển thị giao diện đăng nhập
                self.student_login.id_hs.setText(str(so_thu_tu))  # Điền ID
                self.student_login.pass_HS.setText(password)  # Điền mật khẩu
                self.check_login_hs()  # Mô phỏng thao tác nhấn nút đăng nhập
            else:
                self.msg_box.setText("Vui lòng chọn vai trò!")
                self.msg_box.exec()
                return

    def luu_tai_khoan_giao_vien(self, phone, password, ten_tai_khoan, age, birthday, gender):
        try:
            with open("tk_tc_data.json", "r", encoding="utf-8") as f:
                tk_tc_data = json.load(f)
        except FileNotFoundError:
            tk_tc_data = {"Danh_sach_tai_khoan_teacher": []}

        new_id = 1
        if tk_tc_data["Danh_sach_tai_khoan_teacher"]:
            new_id = max(int(tk['id_tai_khoan']) for tk in tk_tc_data["Danh_sach_tai_khoan_teacher"]) + 1

        new_teacher = {
            "id_tai_khoan": str(new_id),  # Lưu dưới dạng string
            "ten_tai_khoan": ten_tai_khoan,
            "MK_tai_khoan": password,
            "so_dien_thoai": str(phone),  # Lưu dưới dạng string
            "birthday": birthday,
            "age": str(age),  # Lưu dưới dạng string
            "gender": gender,
        }
        tk_tc_data["Danh_sach_tai_khoan_teacher"].append(new_teacher)

        with open("tk_tc_data.json", "w", encoding="utf-8") as f:
            json.dump(tk_tc_data, f, indent=4, ensure_ascii=False)

        self.msg_box.setText("Đăng ký tài khoản giáo viên thành công!")
        self.msg_box.exec()

    def luu_tai_khoan_hoc_sinh(self, so_thu_tu, ten_tai_khoan, password, phone, birthday, age, gender):
        try:
            with open("tk_hs_data.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
        except FileNotFoundError:
            tk_hs_data = {"Danh_sach_tai_khoan": []}

        # Chuyển đổi so_thu_tu thành int trước khi sử dụng
        so_thu_tu = int(so_thu_tu) 

        new_student = {
            "id_tai_khoan": str(so_thu_tu),  # Lưu dưới dạng string
            "ten_tai_khoan": ten_tai_khoan,
            "MK_tai_khoan": password,
            "so_thu_tu": str(so_thu_tu),  # Lưu dưới dạng string
            "so_dien_thoai": str(phone),  # Lưu dưới dạng string
            "birthday": birthday,
            "age": str(age),  # Lưu dưới dạng string
            "gender": gender,
        }
        tk_hs_data["Danh_sach_tai_khoan"].append(new_student)

        with open("tk_hs_data.json", "w", encoding="utf-8") as f:
            json.dump(tk_hs_data, f, indent=4, ensure_ascii=False)

        self.msg_box.setText("Đăng ký tài khoản học sinh thành công!")
        self.msg_box.exec()

    def random_so_thu_tu(self):
        so_thu_tu = random.randint(88001, 88099)
        try:
            with open("tk_hs_data.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
            while so_thu_tu in [tk['id_tai_khoan'] for tk in tk_hs_data.get("Danh_sach_tai_khoan", [])]:
                so_thu_tu = random.randint(88001, 88099)
        except FileNotFoundError:
            pass
        return so_thu_tu  # Trả về số nguyên
        
    def return_register(self):
        self.register.hide()
        self.show()

#      ___           ___           ___           ___           ___            ___           ___
#     /\  \         /\  \         /\__\         /\  \         /\  \          /\__\         /\  \
#    /::\  \        \:\  \       /:/  /        /::\  \       /::\  \        /::|  |        \:\  \
#   /:/\ \  \        \:\  \     /:/  /        /:/\:\  \     /:/\:\  \      /:|:|  |         \:\  \
#  _\:\~\ \  \       /::\  \   /:/  /  ___   /:/  \:\__\   /::\~\:\  \    /:/|:|  |__       /::\  \
# /\ \:\ \ \__\     /:/\:\__\ /:/__/  /\__\ /:/__/ \:|__| /:/\:\ \:\__\  /:/ |:| /\__\     /:/\:\__\
# \:\ \:\ \/__/    /:/  \/__/ \:\  \ /:/  / \:\  \ /:/  / \:\~\:\ \/__/  \/__|:|/:/  /    /:/  \/__/
#  \:\ \:\__\     /:/  /       \:\  /:/  /   \:\  /:/  /   \:\ \:\__\        |:/:/  /    /:/  /
#   \:\/:/  /     \/__/         \:\/:/  /     \:\/:/  /     \:\ \/__/        |::/  /     \/__/
#    \::/  /                     \::/  /       \::/__/       \:\__\          /:/  /
#     \/__/                       \/__/                       \/__/          \/__/

    def Login_hs(self):
        if not self.student_login:
            self.student_login = uic.loadUi("gui/login-student.ui")
            self.student_login.HocSinhLogin_btn.clicked.connect(self.check_login_hs)
            self.student_login.goback_hs_btn.clicked.connect(self.goback_hs_Clicked)
            self.student_login.id_hs.setValidator(self.phone_validator) # Giả sử ID là số, bạn có thể thay đổi validator nếu cần

        self.student_login.show()
        self.hide()
    
    def check_login_hs(self):
        """Kiểm tra thông tin đăng nhập của học sinh."""
        id_tai_khoan = self.student_login.id_hs.text()
        mat_khau = self.student_login.pass_HS.text()

        try:
            with open("tk_hs_data.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
        except FileNotFoundError:
            self.msg_box.setText("Không tìm thấy file tk_hs_data.json!")
            self.msg_box.exec()
            return

        for tai_khoan in tk_hs_data.get("Danh_sach_tai_khoan", []):
            if (
                str(tai_khoan.get("id_tai_khoan", "")) == id_tai_khoan
                and str(tai_khoan.get("MK_tai_khoan", "")) == mat_khau
            ):
                self.student_login.hide()
                self.current_user = "student"  # Đặt người dùng hiện tại là học sinh
                self.HocSinhClicked(tai_khoan)  # Truyền thông tin tài khoản
                return

        self.msg_box.setText("Sai ID tài khoản hoặc mật khẩu!")
        self.msg_box.exec()
        
    def show_new_assignment_notification(self, path):
        """Hiển thị thông báo khi có bài tập mới cho học sinh."""
        if self.current_user == "student":  # Chỉ hiển thị thông báo cho học sinh
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Nhắc Nhở")
            msg_box.setText("Giáo viên đã giao một bài tập/bài giảng cho bạn, bạn hãy đi xem nhé!")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Ok)
            msg_box.exec()

    def check_new_assignments(self):
        """Kiểm tra bài tập mới và hiển thị thông báo cho học sinh."""
        if self.current_user == "student":  # Chỉ kiểm tra cho học sinh
            folder_path = "btvn"
            if os.path.exists(folder_path):
                file_list = os.listdir(folder_path)
                if file_list:
                    # Lấy thời gian sửa đổi cuối cùng của file mới nhất
                    newest_file_time = max(os.path.getmtime(os.path.join(folder_path, f)) for f in file_list)
                    if self.last_login_time is None or newest_file_time > self.last_login_time:
                        self.show_new_assignment_notification(folder_path)

    def HocSinhClicked(self, tai_khoan):
        """Hiển thị giao diện chính của học sinh."""

        # Luôn khởi tạo các thành phần UI
        self.student_main = uic.loadUi("gui/main-st.ui")
        self.tab_widget_hs = self.student_main.findChild(QTabWidget, "Semester_tab_hs")
        self.table_HK1_hs = self.student_main.findChild(QTableWidget, "student_Infor_table_HK1_hs")
        self.table_HK2_hs = self.student_main.findChild(QTableWidget, "student_Infor_table_HK2_hs")
        self.table_CN_hs = self.student_main.findChild(QTableWidget, "student_Infor_table_CN_hs")
        self.xem_hk1_hs = self.student_main.findChild(QComboBox, "xem_diem_mon_hk1_hs")
        self.xem_hk2_hs = self.student_main.findChild(QComboBox, "xem_diem_mon_hk2_hs")
        self.xem_cn_hs = self.student_main.findChild(QComboBox, "xem_diem_mon_cn_hs_2") 

        self.student_main.ten_hoc_sinh.setText(tai_khoan.get("ten_tai_khoan", ""))
        self.student_main.so_thu_tu_hs.setText(str(tai_khoan.get("so_thu_tu", "")))
        self.student_main.id_tai_khoan.setText(str(tai_khoan.get("id_tai_khoan", "")))
        
        self.setup_table_hs(self.table_HK1_hs, "Học kỳ 1")
        self.setup_table_hs(self.table_HK2_hs, "Học kỳ 2")
        self.setup_table_hs(self.table_CN_hs, "Cả năm")

        self.current_student_table = self.table_HK1_hs
        self.current_student_table = self.table_HK2_hs
        self.current_student_table = self.table_CN_hs
        self.student_main.logOut_btn_tc.clicked.connect(self.HocSinhMain_Return)
        self.student_main.xem_bai_tap_hs.clicked.connect(self.show_xem_bai_tap_dialog_hs)
        
        self.tab_widget_hs.currentChanged.connect(self.on_tab_changed_hs)
        self.on_tab_changed_hs(self.tab_widget_hs.currentIndex()) 

        self.setup_table(self.table_HK1_hs, "Học kỳ 1")
        self.setup_table(self.table_HK2_hs, "Học kỳ 2")
        self.setup_table(self.table_CN_hs, "Cả năm")
        self.fill_tables_hs(tai_khoan)
        self.load_data()
        
        self.check_new_assignments()
        self.last_login_time = os.path.getmtime(__file__)

        self.student_main.show()
        
        self.xem_hk1_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_HK1_hs, text))
        self.xem_hk2_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_HK2_hs, text))
        self.xem_cn_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_CN_hs, text))
        
        # Kiểm tra xem QTabWidget có được tìm thấy hay không
        if self.tab_widget_hs is not None:
            self.tab_widget_hs.currentChanged.connect(self.on_tab_changed_hs)
            self.on_tab_changed_hs(self.tab_widget_hs.currentIndex()) 
        else:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
            
        # Kiểm tra xem các QComboBox có được tìm thấy hay không
        if self.xem_hk1_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
        if self.xem_hk2_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
        if self.xem_cn_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
            
        # Kiểm tra xem các QTableWidget có được tìm thấy hay không
        if self.table_HK1_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
        if self.table_HK2_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
        if self.table_CN_hs is None:
            self.msg_box.setText("Hệ thống đang lỗi, xin vui lòng thử lại sau")
            self.msg_box.exec()
            
        self.student_main.show()
    def setup_table_hs(self, table, semester):
        """Thiết lập bảng cho giao diện học sinh, bao gồm cả bảng điểm trung bình cả năm."""
        if semester == "Cả năm":
            column_count = 8  # STT, Họ, Tên, GK1, HK1, GK2, HK2, ĐTBCN
            header_labels = ["STT", "Họ", "Tên", "GK1", "HK1", "GK2", "HK2", "ĐTBCN"]
        else:
            column_count = 11
            header_labels = [
                "Số thứ tự",
                "Họ",
                "Tên",
                "TX1",
                "TX2",
                "TX3",
                "TX4",
                "GK",
                "HK",
                "ĐTB",
                "Điểm TB môn cả năm",
            ]

        table.setColumnCount(column_count)
        table.setHorizontalHeaderLabels(header_labels)

        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 50)
        table.setColumnWidth(2, 80)
        table.setColumnWidth(3, 80)
        table.setColumnWidth(4, 40)
        table.setColumnWidth(5, 40)
        table.setColumnWidth(6, 40)
        table.setColumnWidth(7, 40)
        table.setColumnWidth(8, 40)
        table.setColumnWidth(9, 40)
        table.setColumnWidth(10, 50)

        table.setAlternatingRowColors(True)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        for i in range(table.columnCount()):
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
            
    def fill_tables_hs(self, tai_khoan):
        """Điền dữ liệu vào bảng điểm của học sinh."""
        self.table_HK1_hs.setRowCount(0)
        self.table_HK2_hs.setRowCount(0)
        self.table_CN_hs.setRowCount(0)

        # Lấy id_tai_khoan từ thông tin tài khoản
        student_id = tai_khoan.get("id_tai_khoan")

        # Tìm học sinh theo id_tai_khoan
        for student in self.data["Danh_sach_hoc_sinh"]:
            if student.get("Số thứ tự") == str(student_id):
                row_position = 0  # Khởi tạo vị trí hàng
                for i, subject in enumerate(
                    [
                        "Toán",
                        "Văn",
                        "Anh",
                        "Khoa học tự nhiên",
                        "Lịch sử - địa lý",
                        "Tin học",
                        "Công nghệ",
                        "Giáo dục công dân",
                    ]
                ):
                    # Điền điểm cho học kỳ 1 và 2
                    for semester_key, table_hs in [
                        ("Học kỳ 1", self.table_HK1_hs),
                        ("Học kỳ 2", self.table_HK2_hs),
                    ]:
                        if (
                            semester_key in student.get("Điểm trong năm", {})
                            and subject in student["Điểm trong năm"][semester_key]
                        ):
                            table_hs.insertRow(row_position) # Thêm dòng mới tại vị trí row_position

                            # Điền thông tin học sinh
                            table_hs.setItem(row_position, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
                            table_hs.setItem(row_position, 1, QTableWidgetItem(student.get("Họ", "")))
                            table_hs.setItem(row_position, 2, QTableWidgetItem(student.get("Tên", "")))

                            # Điền điểm
                            for j, grade_type in enumerate(
                                [
                                    "TX1",
                                    "TX2",
                                    "TX3",
                                    "TX4",
                                    "GK1" if semester_key == "Học kỳ 1" else "GK2",
                                    "HK1" if semester_key == "Học kỳ 1" else "HK2",
                                    "ĐTBM",
                                ]
                            ):
                                column_index = 3 + j * 7
                                table_hs.setItem(
                                    row_position,
                                    column_index,
                                    QTableWidgetItem(
                                        str(
                                            student["Điểm trong năm"][semester_key][
                                                subject
                                            ].get(grade_type, "")
                                        )
                                    ),
                                )
                        row_position += 1  # Tăng vị trí hàng cho môn học tiếp theo

                    # Điền điểm trung bình cả năm
                    try:
                        gk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("GK1", "0")
                        gk1 = float(gk1_str) if gk1_str else 0.0
                        hk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("HK1", "0")
                        hk1 = float(hk1_str) if hk1_str else 0.0
                        gk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("GK2", "0")
                        gk2 = float(gk2_str) if gk2_str else 0.0
                        hk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("HK2", "0")
                        hk2 = float(hk2_str) if hk2_str else 0.0

                        dtbm_cn = (gk1 + hk1 + (gk2 + hk2) * 2) / 6

                        row_position = self.table_CN_hs.rowCount()
                        self.table_CN_hs.insertRow(row_position)

                        # Điền thông tin học sinh
                        self.table_CN_hs.setItem(row_position, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
                        self.table_CN_hs.setItem(row_position, 1, QTableWidgetItem(student.get("Họ", "")))
                        self.table_CN_hs.setItem(row_position, 2, QTableWidgetItem(student.get("Tên", "")))

                        # Điền điểm trung bình cả năm
                        self.table_CN_hs.setItem(row_position, 3, QTableWidgetItem(str(gk1) if gk1 else ""))
                        self.table_CN_hs.setItem(row_position, 4, QTableWidgetItem(str(hk1) if hk1 else ""))
                        self.table_CN_hs.setItem(row_position, 5, QTableWidgetItem(str(gk2) if gk2 else ""))
                        self.table_CN_hs.setItem(row_position, 6, QTableWidgetItem(str(hk2) if hk2 else ""))
                        self.table_CN_hs.setItem(row_position, 7, QTableWidgetItem(f"{dtbm_cn:.2f}"))
                    except KeyError:
                        pass # bỏ qua nếu thiếu key
                break  # Thoát vòng lặp khi đã tìm thấy học sinh           
                        
    def on_tab_changed_hs(self, index):
        """Cập nhật self.current_student_table dựa trên tab hiện tại của học sinh."""
        if index == 0:
            self.current_student_table = self.table_HK1_hs
        elif index == 1:
            self.current_student_table = self.table_HK2_hs
        elif index == 2:
            self.current_student_table = self.table_CN_hs

        # Cập nhật lại combobox môn học cho tab hiện tại
        self.update_subject_combobox_hs()
        
    def show_column_hs(self, table, subject):
        """Cập nhật dữ liệu cột dựa trên môn học được chọn (giao diện học sinh)."""
        student_id = self.student_main.id_tai_khoan.text()  # Lấy ID học sinh
        for student in self.data["Danh_sach_hoc_sinh"]:
            if student.get("Số thứ tự") == student_id:  # Tìm học sinh theo ID
                for semester_key in ["Học kỳ 1", "Học kỳ 2"]:
                    if semester_key in student.get("Điểm trong năm", {}) and subject in student["Điểm trong năm"][semester_key]:
                        for j, grade_type in enumerate(
                            [
                                "TX1",
                                "TX2",
                                "TX3",
                                "TX4",
                                "GK1" if semester_key == "Học kỳ 1" else "GK2",
                                "HK1" if semester_key == "Học kỳ 1" else "HK2",
                                "ĐTBM",
                            ]
                        ):
                            column_index = 3 + j  # Vị trí cột bắt đầu từ cột 3
                            table.setItem(
                                0,  # Luôn là hàng 0 vì chỉ có 1 học sinh
                                column_index,
                                QTableWidgetItem(
                                    str(student["Điểm trong năm"][semester_key][subject].get(grade_type, ""))
                                ),
                            )
                    
    def update_subject_combobox_hs(self):
        """Cập nhật combobox môn học dựa trên tab hiện tại của học sinh."""
        if self.current_student_table is self.table_HK1_hs:
            combobox = self.xem_hk1_hs
        elif self.current_student_table is self.table_HK2_hs:
            combobox = self.xem_hk2_hs
        elif self.current_student_table is self.table_CN_hs:
            # Sửa dòng này để sử dụng object name đúng
            combobox = self.student_main.findChild(QComboBox, "xem_diem_mon_cn_hs_2") 
        else:
            return

        combobox.clear()
        combobox.addItem("")
        combobox.addItems(
            [
                "Toán",
                "Văn",
                "Anh",
                "Khoa học tự nhiên",
                "Lịch sử - địa lý",
                "Tin học",
                "Công nghệ",
                "Giáo dục công dân",
            ]
        )
        
    def fill_tables_hs(self, tai_khoan):
        """Điền dữ liệu vào bảng điểm của học sinh."""
        self.table_HK1_hs.setRowCount(0)
        self.table_HK2_hs.setRowCount(0)
        self.table_CN_hs.setRowCount(0)
        
        # Lấy id_tai_khoan từ thông tin tài khoản
        student_id = tai_khoan.get("id_tai_khoan")

        # Tìm học sinh theo id_tai_khoan
        for student in self.data["Danh_sach_hoc_sinh"]:
            if student.get("Số thứ tự") == str(student_id):
                # Thêm thông tin học sinh vào các cột tương ứng
                row_position = self.table_HK1_hs.rowCount()
                self.table_HK1_hs.insertRow(row_position)
                self.table_HK2_hs.insertRow(row_position)
                self.table_CN_hs.insertRow(row_position)

                self.table_HK1_hs.setItem(0, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
                self.table_HK1_hs.setItem(0, 1, QTableWidgetItem(student.get("Họ", "")))
                self.table_HK1_hs.setItem(0, 2, QTableWidgetItem(student.get("Tên", "")))

                self.table_HK2_hs.setItem(0, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
                self.table_HK2_hs.setItem(0, 1, QTableWidgetItem(student.get("Họ", "")))
                self.table_HK2_hs.setItem(0, 2, QTableWidgetItem(student.get("Tên", "")))

                self.table_CN_hs.setItem(0, 0, QTableWidgetItem(student.get("Số thứ tự", "")))
                self.table_CN_hs.setItem(0, 1, QTableWidgetItem(student.get("Họ", "")))
                self.table_CN_hs.setItem(0, 2, QTableWidgetItem(student.get("Tên", "")))

                for i, subject in enumerate(
                    [
                        "Toán",
                        "Văn",
                        "Anh",
                        "Khoa học tự nhiên",
                        "Lịch sử - địa lý",
                        "Tin học",
                        "Công nghệ",
                        "Giáo dục công dân",
                    ]
                ):
                    for semester_key, table in [
                        ("Học kỳ 1", self.table_HK1_hs),
                        ("Học kỳ 2", self.table_HK2_hs),
                    ]:
                        if (
                            semester_key in student.get("Điểm trong năm", {})
                            and subject in student["Điểm trong năm"][semester_key]
                        ):
                            for j, grade_type in enumerate(
                                [
                                    "TX1",
                                    "TX2",
                                    "TX3",
                                    "TX4",
                                    "GK1" if semester_key == "Học kỳ 1" else "GK2",
                                    "HK1" if semester_key == "Học kỳ 1" else "HK2",
                                    "ĐTBM",
                                ]
                            ):
                                table.setItem(
                                    0,  # Luôn là hàng 0 vì chỉ có 1 học sinh
                                    i + 3 + j,
                                    QTableWidgetItem(
                                        str(
                                            student["Điểm trong năm"][semester_key][
                                                subject
                                            ].get(grade_type, "")
                                        )
                                    ),
                                )

                    try:
                        gk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("GK1", "0")
                        gk1 = float(gk1_str) if gk1_str else 0.0
                        hk1_str = student["Điểm trong năm"]["Học kỳ 1"][subject].get("HK1", "0")
                        hk1 = float(hk1_str) if hk1_str else 0.0
                        gk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("GK2", "0")
                        gk2 = float(gk2_str) if gk2_str else 0.0
                        hk2_str = student["Điểm trong năm"]["Học kỳ 2"][subject].get("HK2", "0")
                        hk2 = float(hk2_str) if hk2_str else 0.0

                        dtbm_cn = (gk1 + hk1 + (gk2 + hk2) * 2) / 6

                        self.table_CN_hs.setItem(0, i * 5 + 3, QTableWidgetItem(str(gk1) if gk1 else ""))
                        self.table_CN_hs.setItem(0, i * 5 + 4, QTableWidgetItem(str(hk1) if hk1 else ""))
                        self.table_CN_hs.setItem(0, i * 5 + 5, QTableWidgetItem(str(gk2) if gk2 else ""))
                        self.table_CN_hs.setItem(0, i * 5 + 6, QTableWidgetItem(str(hk2) if hk2 else ""))
                        self.table_CN_hs.setItem(0, i * 5 + 7, QTableWidgetItem(f"{dtbm_cn:.2f}"))
                    except KeyError:
                        for col in range(5):
                            self.table_CN_hs.setItem(0, i * 5 + 3 + col, QTableWidgetItem(""))
                break  # Đã tìm thấy học sinh, thoát khỏi vòng lặp

    def show_xem_bai_tap_dialog_hs(self):
        if not self.xem_bai_tap_dialog:
            self.xem_bai_tap_dialog = QDialog(self)
            self.xem_bai_tap_dialog.setWindowTitle("Xem Bài Tập và Video Bài Giảng")

            layout = QVBoxLayout()

            self.btvn_list = QListWidget()
            layout.addWidget(QLabel("Bài tập:"))
            layout.addWidget(self.btvn_list)
            download_btn = QPushButton("Tải Về")
            download_btn.clicked.connect(self.download_btvn)
            layout.addWidget(download_btn)

            # Video bài giảng
            self.video_list = QListWidget()
            layout.addWidget(QLabel("Video bài giảng:"))
            layout.addWidget(self.video_list)
            self.video_label = QLabel(self)  # QLabel để hiển thị video
            layout.addWidget(self.video_label)
            self.video_list.itemDoubleClicked.connect(self.play_video_hs)
            self.update_btvn_list()
            self.xem_bai_tap_dialog.setLayout(layout)
            self.xem_bai_tap_dialog.show()

            self.update_btvn_list()
            self.xem_bai_tap_dialog.setLayout(layout)

        self.xem_bai_tap_dialog.show()
        
    def play_video_hs(self, item):
        """Phát video bài giảng trong một cửa sổ riêng biệt."""
        file_name = item.text()
        file_path = os.path.join("btvn", "Video bài giảng", file_name)
        if os.path.exists(file_path):
            # Tạo instance của VideoPlayer và truyền đường dẫn video
            self.video_player = VideoPlayer(file_path, self)
            self.video_player.show()  # Hiển thị cửa sổ video

    def update_video_frame(self):
        """Cập nhật khung hình video trên QLabel."""
        ret, frame = self.cap.read()
        if ret:
            # Chuyển đổi khung hình OpenCV (BGR) sang RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Tạo QImage từ khung hình RGB
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            qimage = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            # Hiển thị QImage trên QLabel
            self.video_label.setPixmap(QPixmap.fromImage(qimage))
        else:
            self.timer.stop()  # Dừng timer khi video kết thúc

    def show_watch_time_dialog(self, file_path):
        """Hiển thị cửa sổ đếm ngược thời gian xem video."""
        video_duration = self.get_video_duration(file_path)
        if video_duration is None:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Thời gian xem video")
        layout = QVBoxLayout()
        time_remaining_label = QLabel(dialog)
        layout.addWidget(time_remaining_label)
        dialog.setLayout(layout)

        self.remaining_seconds = video_duration // 2  # Thời gian xem tối thiểu (1/2 thời lượng)

        def update_timer():
            """Cập nhật đồng hồ đếm ngược."""
            minutes = self.remaining_seconds // 60
            seconds = self.remaining_seconds % 60
            time_remaining_label.setText(f"Thời gian còn lại: {minutes:02}:{seconds:02}")

            self.remaining_seconds -= 1
            if self.remaining_seconds < 0:
                # Đã xem đủ thời gian
                timer.stop()
                dialog.close()
                QMessageBox.information(self, "Thông báo", "Bạn đã xem đủ thời gian!")

        timer = QTimer(self)
        timer.timeout.connect(update_timer)
        timer.start(1000)  # Cập nhật mỗi giây
        update_timer()  # Cập nhật ngay lập tức
        dialog.exec()

    def get_video_duration(self, file_path):
        """Lấy thời lượng video (tính bằng giây)."""
        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            duration = frame_count / fps
            cap.release()
            return int(duration)
        else:
            return None


    def HocSinhMain_Return(self):
        self.student_main.hide()
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())