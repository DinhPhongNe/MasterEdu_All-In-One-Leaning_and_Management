from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTabWidget, QComboBox, QLineEdit, QTableWidget, QDialog, QVBoxLayout, QPushButton, QLabel, QGridLayout, QTableWidgetItem
from PyQt6 import uic
import json
from student_grades import StudentGrades
from view_assignments import ViewAssignments
from assignment_upload import AssignmentUpload

class TeacherMain(QMainWindow, StudentGrades, ViewAssignments, AssignmentUpload):
    def __init__(self, data) -> None:
        super().__init__()
        uic.loadUi("gui/main-tc.ui", self)
        self.data = data
        self.current_teacher_table = None

        # Khởi tạo xem_bai_tap_dialog là None
        self.xem_bai_tap_dialog = None

        self.logOut_btn_tc.clicked.connect(self.logout)

        self.add_btn.clicked.connect(self.add_information)
        self.nhap_diem_mon_btn.clicked.connect(self.show_chon_hoc_sinh_dialog)
        self.update_btn.clicked.connect(self.show_sua_thong_tin_dialog)
        self.delete_btn.clicked.connect(self.delete_information)
        self.search_btn.clicked.connect(self.search)
        self.clear_btn.clicked.connect(self.clear_information)
        self.xem_bai_tap.clicked.connect(self.show_xem_bai_tap_dialog)
        self.btvn_upload_btn.clicked.connect(self.upload_btvn)

        self.table = self.findChild(QTabWidget, "Semester_tab")
        self.tab_widget = self.findChild(QTabWidget, "Semester_tab")
        self.table_HK1 = self.findChild(QTableWidget, "student_Infor_table_HK1")
        self.table_HK2 = self.findChild(QTableWidget, "student_Infor_table_HK2")
        self.table_CN = self.findChild(QTableWidget, "student_Infor_table_CN")
        self.xem_hk1 = self.findChild(QComboBox, "xem_diem_mon_hk1")
        self.xem_hk2 = self.findChild(QComboBox, "xem_diem_mon_hk2")
        self.xem_cn = self.findChild(QComboBox, "xem_diem_mon_cn")
        self.search_bar = self.findChild(QLineEdit, "Search_bar")

        self.stt = self.findChild(QLineEdit, "so_thu_tu")
        self.ho = self.findChild(QLineEdit, "ho")
        self.ten = self.findChild(QLineEdit, "ten")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(self.tab_widget.currentIndex())

        self.setup_table(self.table_HK1, "Học kỳ 1")
        self.setup_table(self.table_HK2, "Học kỳ 2")
        self.setup_table(self.table_CN, "Cả năm")
        self.fill_tables()

        self.xem_hk1.currentTextChanged.connect(lambda text: self.show_column(self.table_HK1, text))
        self.xem_hk2.currentTextChanged.connect(lambda text: self.show_column(self.table_HK2, text))
        self.xem_cn.currentTextChanged.connect(lambda text: self.show_column(self.table_CN, text))

        self.chon_hs_combo = QComboBox()
        self.load_data()

        self.chon_hoc_sinh_dialog = None
        self.nhap_diem_dialog = None
        self.sua_thong_tin_dialog = None
        self.sua_diem_dialog = None

        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Lỗi")
        self.msg_box.setIcon(QMessageBox.Icon.Warning)
        self.msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")

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

    def logout(self):
        self.hide()
        # Hiển thị lại giao diện đăng nhập hoặc thực hiện các thao tác đăng xuất khác

    def on_tab_changed(self, index):
        if index == 0:
            self.current_teacher_table = self.table_HK1
        elif index == 1:
            self.current_teacher_table = self.table_HK2
        elif index == 2:
            self.current_teacher_table = self.table_CN
        self.update_subject_combobox()

    def load_data(self):
        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"Danh_sach_hoc_sinh": []}
        except Exception as e:
            print(f"Lỗi khi đọc file diem_database.json: {e}")
        self.sort_students()

    def save_data(self):
        self.sort_students()
        with open("diem_database.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def sort_students(self):
        self.data["Danh_sach_hoc_sinh"].sort(key=lambda student: int(student.get("Số thứ tự", 0)))

    def fill_tables(self):
        self.table_HK1.setRowCount(0)
        self.table_HK2.setRowCount(0)
        self.table_CN.setRowCount(0)

        for row, student in enumerate(self.data["Danh_sach_hoc_sinh"]):
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
                            column_index = 3 + j + i * 7 
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
        self.grid_layout = QGridLayout()
        self.create_nhap_diem_form(text)
        self.nhap_diem_dialog.layout().addLayout(self.grid_layout)

    def create_nhap_diem_form(self, hoc_ki):
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

        if "Điểm trong năm" not in student:
            student["Điểm trong năm"] = {}
        if hoc_ki not in student["Điểm trong năm"]:
            student["Điểm trong năm"][hoc_ki] = {}
        if mon_hoc not in student["Điểm trong năm"][hoc_ki]:
            student["Điểm trong năm"][hoc_ki][mon_hoc] = {}

        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX1"] = tx1
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX2"] = tx2
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX3"] = tx3
        student["Điểm trong năm"][hoc_ki][mon_hoc]["TX4"] = tx4
        student["Điểm trong năm"][hoc_ki][mon_hoc][
            "GK1" if hoc_ki == "Học kỳ 1" else "GK2"
        ] = gk
        student["Điểm trong năm"][hoc_ki][mon_hoc][
            "HK1" if hoc_ki == "Học kỳ 1" else "HK2"
        ] = hk

        dtbm = self.calculate_dtbm(tx1, tx2, tx3, tx4, gk, hk)
        if dtbm is not None:
            student["Điểm trong năm"][hoc_ki][mon_hoc]["ĐTBM"] = f"{dtbm:.2f}"

        self.save_data()

        self.fill_tables()
        self.nhap_diem_dialog.close()

    def update_diem_trung_binh_ca_nam(self, student_index, subject):
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
                    if grade_type not in student["Điểm trong năm"][hoc_ki][mon_hoc]:
                        student["Điểm trong năm"][hoc_ki][mon_hoc][grade_type] = ""

                    table.setItem(
                        row_index,
                        column_index + j,
                        QTableWidgetItem(
                            str(student["Điểm trong năm"][hoc_ki][mon_hoc].get(grade_type, ""))
                        ),
                    )

    def show_sua_thong_tin_dialog(self):
        current_row = self.table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]
            self.sua_thong_tin_dialog = QDialog(self)
            self.sua_thong_tin_dialog.setWindowTitle("Sửa thông tin học sinh")
            layout = QGridLayout()

            layout.addWidget(QLabel("Số thứ tự:"), 0, 0)
            self.stt_edit = QLineEdit(student["Số thứ tự"])
            layout.addWidget(self.stt_edit, 0, 1)

            layout.addWidget(QLabel("Họ:"), 1, 0)
            self.ho_edit = QLineEdit(student["Họ"])
            layout.addWidget(self.ho_edit, 1, 1)

            layout.addWidget(QLabel("Tên:"), 2, 0)
            self.ten_edit = QLineEdit(student["Tên"])
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
        current_row = self.current_teacher_table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]
            student["Số thứ tự"] = self.stt_edit.text()
            student["Họ"] = self.ho_edit.text()
            student["Tên"] = self.ten_edit.text()

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
            self.combo_hk_sua.currentTextChanged.connect(
                self.update_sua_diem_dialog
            )
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

    def create_sua_diem_form(self, hoc_ki, student=None):
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
        )
        self.grid_layout_sua.addWidget(self.combo_mon_sua, 0, 1)

        self.tx1_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("TX1:"), 1, 0)
        self.grid_layout_sua.addWidget(self.tx1_sua, 1, 1)
        self.tx2_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("TX2:"), 2, 0)
        self.grid_layout_sua.addWidget(self.tx2_sua, 2, 1)
        self.tx3_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("TX3:"), 3, 0)
        self.grid_layout_sua.addWidget(self.tx3_sua, 3, 1)
        self.tx4_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("TX4:"), 4, 0)
        self.grid_layout_sua.addWidget(self.tx4_sua, 4, 1)
        self.gk_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("GK:"), 5, 0)
        self.grid_layout_sua.addWidget(self.gk_sua, 5, 1)
        self.hk_sua = QLineEdit()
        self.grid_layout_sua.addWidget(QLabel("HK:"), 6, 0)
        self.grid_layout_sua.addWidget(self.hk_sua, 6, 1)
        self.luu_btn_sua = QPushButton("Lưu")
        self.luu_btn_sua.clicked.connect(self.update_diem_hoc_sinh)
        self.grid_layout_sua.addWidget(self.luu_btn_sua, 7, 0, 1, 2)

        self.update_sua_diem_form_mon_hoc("Toán", student)

    def update_sua_diem_form_mon_hoc(self, mon_hoc, student=None):
        if student is None:
            return

        current_row = self.current_teacher_table.currentRow()
        if current_row == -1:
            return

        hoc_ki = self.combo_hk_sua.currentText()

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
            student["Điểm trong năm"][hoc_ki][mon_hoc].get(
                "GK1" if hoc_ki == "Học kỳ 1" else "GK2", ""
            )
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )
        self.hk_sua.setText(
            student["Điểm trong năm"][hoc_ki][mon_hoc].get(
                "HK1" if hoc_ki == "Học kỳ 1" else "HK2", ""
            )
            if hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
            else ""
        )

        self.fill_tables()
        self.save_data()

    def update_diem_hoc_sinh(self):
        current_row = self.current_teacher_table.currentRow()
        if current_row != -1:
            student = self.data["Danh_sach_hoc_sinh"][current_row]

        hoc_ki = self.combo_hk_sua.currentText()
        mon_hoc = self.combo_mon_sua.currentText()
        if (
            hoc_ki in student["Điểm trong năm"]
            and mon_hoc in student["Điểm trong năm"][hoc_ki]
        ):
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX1"] = self.tx1_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX2"] = self.tx2_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX3"] = self.tx3_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc]["TX4"] = self.tx4_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc][
                "GK1" if hoc_ki == "Học kỳ 1" else "GK2"
            ] = self.gk_sua.text()
            student["Điểm trong năm"][hoc_ki][mon_hoc][
                "HK1" if hoc_ki == "Học kỳ 1" else "HK2"
            ] = self.hk_sua.text()

            dtbm = self.calculate_dtbm(
                self.tx1_sua.text(),
                self.tx2_sua.text(),
                self.tx3_sua.text(),
                self.tx4_sua.text(),
                self.gk_sua.text(),
                self.hk_sua.text(),
            )
            if dtbm is not None:
                student["Điểm trong năm"][hoc_ki][mon_hoc]["ĐTBM"] = f"{dtbm:.2f}"

            self.update_diem_trung_binh_ca_nam(current_row, mon_hoc)

        self.fill_tables()

        self.save_data()
        self.sua_diem_dialog.close()

    def add_information(self):
        if not self.stt.text() or not self.ho.text() or not self.ten.text():
            self.msg_box.setText("Vui lòng nhập đầy đủ thông tin!")
            self.msg_box.exec()
            return

        stt = self.stt.text()

        if not stt or len(stt) != 5 or not stt.isdigit() or int(stt[2:]) == 0:
            self.msg_box.setText(
                "Số thứ tự không hợp lệ. Vui lòng nhập theo định dạng 'Số lớp - Số thứ tự' (ví dụ: 88041)."
            )
            self.msg_box.exec()
            return

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

        new_student["Điểm trung bình cả năm"] = {
            "Học kỳ 1": {
                subject: {"GK1": None, "HK1": None}
                for subject in [
                    "Toán",
                    "Văn",
                    "Anh",
                    "Khoa học tự nhiên",
                    "Lịch sử - địa lý",
                    "Tin học",
                    "Công nghệ",
                    "Giáo dục công dân",
                ]
            },
            "Học kỳ 2": {
                subject: {"GK2": None, "HK2": None}
                for subject in [
                    "Toán",
                    "Văn",
                    "Anh",
                    "Khoa học tự nhiên",
                    "Lịch sử - địa lý",
                    "Tin học",
                    "Công nghệ",
                    "Giáo dục công dân",
                ]
            },
        }

        self.data["Danh_sach_hoc_sinh"].append(new_student)
        self.chon_hs_combo.addItem(f"{new_student['Họ']} {new_student['Tên']}")
        self.save_data()
        self.fill_tables()
        self.stt.clear()
        self.ho.clear()
        self.ten.clear()

    def update_subject_combobox(self):
        if self.current_teacher_table is self.table_HK1:
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

        import random
        approval = random.choice(["Đồng ý", "Không đồng ý"])

        if approval == "Đồng ý":
            confirm_box = QMessageBox()
            confirm_box.setWindowTitle("Thông báo")
            confirm_box.setIcon(QMessageBox.Icon.Information)
            confirm_box.setText("Hiệu trưởng đã đồng ý. Toàn bộ học sinh sẽ bị xóa.")
            confirm_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")
            confirm_box.setStandardButtons(
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            )

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
        current_row = self.current_teacher_table.currentRow()
        if current_row != -1:
            del self.data["Danh_sach_hoc_sinh"][current_row]
            self.fill_tables()
            self.save_data()