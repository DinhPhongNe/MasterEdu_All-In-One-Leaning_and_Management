from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTabWidget, QComboBox, QTableWidget, QTableWidgetItem
from PyQt6 import uic
from student_grades import StudentGrades
from view_assignments import ViewAssignments
from menu_select_hs import MenuSelectHS

class StudentMain(QMainWindow, StudentGrades, ViewAssignments):
    def __init__(self, data, tai_khoan) -> None:
        super().__init__()
        uic.loadUi("gui/main-st.ui", self)
        self.data = data
        self.tai_khoan = tai_khoan
        self.current_user = "student"  # Đặt người dùng hiện tại là học sinh
        self.last_login_time = None # Lưu thời gian đăng nhập cuối cùng

        # Khởi tạo xem_bai_tap_dialog là None
        self.xem_bai_tap_dialog = None
        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Lỗi")
        self.msg_box.setIcon(QMessageBox.Icon.Warning)
        self.msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")

        self.tab_widget_hs = self.findChild(QTabWidget, "Semester_tab_hs")
        self.table_HK1_hs = self.findChild(QTableWidget, "student_Infor_table_HK1_hs")
        self.table_HK2_hs = self.findChild(QTableWidget, "student_Infor_table_HK2_hs")
        self.table_CN_hs = self.findChild(QTableWidget, "student_Infor_table_CN_hs")
        self.xem_hk1_hs = self.findChild(QComboBox, "xem_diem_mon_hk1_hs")
        self.xem_hk2_hs = self.findChild(QComboBox, "xem_diem_mon_hk2_hs")
        self.xem_cn_hs = self.findChild(QComboBox, "xem_diem_mon_cn_hs_2")

        self.ten_hoc_sinh.setText(tai_khoan.get("ten_tai_khoan", ""))
        self.so_thu_tu_hs.setText(str(tai_khoan.get("so_thu_tu", "")))
        self.id_tai_khoan.setText(str(tai_khoan.get("id_tai_khoan", "")))

        self.setup_table(self.table_HK1_hs, "Học kỳ 1")
        self.setup_table(self.table_HK2_hs, "Học kỳ 2")
        self.setup_table(self.table_CN_hs, "Cả năm")

        self.current_student_table = self.table_HK1_hs
        self.current_student_table = self.table_HK2_hs
        self.current_student_table = self.table_CN_hs

        # Sửa lỗi: Loại bỏ self.student_main.
        self.logOut_btn_tc.clicked.connect(self.logout)
        self.xem_bai_tap_hs.clicked.connect(self.show_xem_bai_tap_dialog)
        self.logOut_btn_tc.clicked.connect(self.return_to_menu_hs)

        self.tab_widget_hs.currentChanged.connect(self.on_tab_changed_hs)
        self.on_tab_changed_hs(self.tab_widget_hs.currentIndex())

        self.fill_tables_hs()

        self.xem_hk1_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_HK1_hs, text))
        self.xem_hk2_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_HK2_hs, text))
        self.xem_cn_hs.currentTextChanged.connect(lambda text: self.show_column_hs(self.table_CN_hs, text))

        # Kiểm tra bài tập mới khi đăng nhập
        self.check_new_assignments()
        # Lưu thời gian đăng nhập
        import os
        self.last_login_time = os.path.getmtime(__file__)

        # Kiểm tra xem QTabWidget có được tìm thấy hay không
        if self.tab_widget_hs is None:
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

    def return_to_menu_hs(self):
        self.close()  # Đóng student_main
        self.menu_hs = MenuSelectHS(self.data, self.tai_khoan)  # Tạo lại menu select cho học sinh
        self.menu_hs.show()
        
    def fill_tables_hs(self):
        self.table_HK1_hs.setRowCount(0)
        self.table_HK2_hs.setRowCount(0)
        self.table_CN_hs.setRowCount(0)

        student_id = self.tai_khoan.get("id_tai_khoan")

        for student in self.data["Danh_sach_hoc_sinh"]:
            if student.get("Số thứ tự") == str(student_id):
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

    def on_tab_changed_hs(self, index):
        if index == 0:
            self.current_student_table = self.table_HK1_hs
        elif index == 1:
            self.current_student_table = self.table_HK2_hs
        elif index == 2:
            self.current_student_table = self.table_CN_hs
        self.update_subject_combobox_hs()

    def show_column_hs(self, table, subject):
        student_id = self.id_tai_khoan.text()
        for student in self.data["Danh_sach_hoc_sinh"]:
            if student.get("Số thứ tự") == student_id:
                for semester_key in ["Học kỳ 1", "Học kỳ 2"]:
                    if semester_key in student.get("Điểm trong năm", {}) and subject in student["Điểm trong năm"][
                        semester_key]:
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
                            column_index = 3 + j
                            table.setItem(
                                0,
                                column_index,
                                QTableWidgetItem(
                                    str(student["Điểm trong năm"][semester_key][subject].get(grade_type, ""))
                                ),
                            )

    def update_subject_combobox_hs(self):
        if self.current_student_table is self.table_HK1_hs:
            combobox = self.xem_hk1_hs
        elif self.current_student_table is self.table_HK2_hs:
            combobox = self.xem_hk2_hs
        elif self.current_student_table is self.table_CN_hs:
            combobox = self.xem_cn_hs 
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

    def logout(self):
        self.close()
        # Hiển thị lại giao diện đăng nhập hoặc thực hiện các thao tác đăng xuất khác