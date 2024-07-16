from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

class StudentGrades:
    def setup_table(self, table, semester):
        if semester == "Cả năm":
            column_count = 8 
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
        table.setSelectionMode(table.SelectionMode.SingleSelection)

        for i in range(table.columnCount()):
            table.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            
    def show_column(self, table, subject):
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
                        column_index = 3 + j
                        table.setItem(
                            row,
                            column_index,
                            QTableWidgetItem(
                                str(student["Điểm trong năm"][semester_key][subject].get(grade_type, ""))
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