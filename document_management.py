import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QTableWidgetItem, QListWidget, QMainWindow, QTableWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import uic
import PyPDF2 
from PIL import Image 
import time
from coming_soon import ComingSoon

class DocumentManagementWindow(QMainWindow):  # Tạo class DocumentManagementWindow
    def __init__(self, data, tai_khoan):  # Thêm data và tai_khoan
        super().__init__()
        uic.loadUi("gui/leaning_material.ui", self)
        self.data = data
        self.tai_khoan = tai_khoan
        self.document_dialog = None

        self.table_tai_lieu = self.findChild(QTableWidget, "tableWidget")
        self.xem_favor_tai_lieu = self.findChild(QPushButton, "xem_favor_tai_lieu")
        self.upload_tai_lieu = self.findChild(QPushButton, "upload_tai_lieu")
        self.coming_soon = None

        #self.setup_document_table()
        self.load_documents()

        self.xem_favor_tai_lieu.clicked.connect(self.show_favorite_documents)
        self.upload_tai_lieu.clicked.connect(self.show_coming_soon)
        
        
        self.table_tai_lieu.setColumnCount(8)
        self.table_tai_lieu.setHorizontalHeaderLabels(
            ["Người đăng", "Mã tài liệu", "Tài liệu môn", "Ngày đăng", "Ghi chú", "Đọc", "Thêm vào yêu thích", "Đường dẫn"]
        )
        self.table_tai_lieu.setColumnHidden(7, True)  # Ẩn cột "Đường dẫn"

        self.table_tai_lieu.setColumnWidth(0, 150)  # Điều chỉnh độ rộng cột cho phù hợp
        self.table_tai_lieu.setColumnWidth(1, 100)
        self.table_tai_lieu.setColumnWidth(2, 150)
        self.table_tai_lieu.setColumnWidth(3, 100)
        self.table_tai_lieu.setColumnWidth(4, 200)
        self.table_tai_lieu.setColumnWidth(5, 50)
        self.table_tai_lieu.setColumnWidth(6, 150)

        self.table_tai_lieu.setAlternatingRowColors(True)
        self.table_tai_lieu.setSelectionMode(self.table_tai_lieu.SelectionMode.SingleSelection)

        for i in range(self.table_tai_lieu.columnCount()):
            self.table_tai_lieu.horizontalHeaderItem(i).setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table_tai_lieu.cellClicked.connect(self.handle_cell_click)

        self.display_documents() 

    def load_documents(self):
        try:
            with open("documents.json", "r", encoding="utf-8") as f:
                self.documents = json.load(f)
        except FileNotFoundError:
            self.documents = []
        self.display_documents()

    def display_documents(self):
        self.table_tai_lieu.setRowCount(0)
        for document in self.documents:
            row_position = self.table_tai_lieu.rowCount()
            self.table_tai_lieu.insertRow(row_position)

            self.table_tai_lieu.setItem(row_position, 0, QTableWidgetItem(document["nguoi_dang"]))
            self.table_tai_lieu.setItem(row_position, 1, QTableWidgetItem(document["ma_tai_lieu"]))
            self.table_tai_lieu.setItem(row_position, 2, QTableWidgetItem(document["tai_lieu_mon"]))
            self.table_tai_lieu.setItem(row_position, 3, QTableWidgetItem(document["ngay_dang"]))
            self.table_tai_lieu.setItem(row_position, 4, QTableWidgetItem(document["ghi_chu"]))
            self.table_tai_lieu.setItem(row_position, 5, QTableWidgetItem(""))  # Cột "Đọc" để trống
            self.table_tai_lieu.setItem(row_position, 6, QTableWidgetItem(""))  # Cột "Yêu thích" để trống
            self.table_tai_lieu.setItem(row_position, 7, QTableWidgetItem(document["duong_dan"]))  # Cột "Đường dẫn"

    def handle_cell_click(self, row, column):
        if column == 5:  # Cột "Đọc"
            self.open_document(row)
        elif column == 6:  # Cột "Yêu thích"
            self.toggle_favorite(row)

    def open_document(self, row):
        document_path = self.table_tai_lieu.item(row, 7).text()
        try:
            # Mở tài liệu PDF
            if document_path.lower().endswith(".pdf"):
                pdf_reader = PyPDF2.PdfReader(document_path)
                # Hiển thị trang đầu tiên của PDF
                page = pdf_reader.pages[0]
                xObject = page['/Resources']['/XObject'].get_object()

                for obj in xObject:
                    if xObject[obj]['/Subtype'] == '/Image':
                        size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                        data = xObject[obj].get_data()
                        if xObject[obj]['/ColorSpace'] == '/DeviceRGB':
                            mode = "RGB"
                        else:
                            mode = "P"

                        img = Image.frombytes(mode, size, data)
                        img.show()
            else:
                # Xử lý các loại tài liệu khác ở đây (ví dụ: mở bằng ứng dụng mặc định)
                os.startfile(document_path)
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể mở tài liệu: {e}")

    def toggle_favorite(self, row):
        ma_tai_lieu = self.table_tai_lieu.item(row, 1).text()
        for i, document in enumerate(self.documents):
            if document["ma_tai_lieu"] == ma_tai_lieu:
                # Đánh dấu "X" vào cột "Yêu thích"
                if "yeu_thich" not in document:
                    document["yeu_thich"] = False
                document["yeu_thich"] = not document["yeu_thich"]
                self.table_tai_lieu.setItem(row, 6, QTableWidgetItem("X" if document["yeu_thich"] else ""))

                # Lưu thay đổi vào file documents.json
                self.save_documents()
                break

    def show_favorite_documents(self):
        favorite_docs = [doc for doc in self.documents if doc.get("yeu_thich")]
        if favorite_docs:
            # Hiển thị danh sách tài liệu yêu thích
            dialog = QDialog(self)
            dialog.setWindowTitle("Tài liệu yêu thích")
            layout = QVBoxLayout()
            list_widget = QListWidget()
            for doc in favorite_docs:
                list_widget.addItem(f"{doc['tai_lieu_mon']} - {doc['ma_tai_lieu']} ({doc['nguoi_dang']})")
            layout.addWidget(list_widget)
            dialog.setLayout(layout)
            dialog.exec()
        else:
            QMessageBox.information(self, "Thông báo", "Bạn chưa có tài liệu yêu thích nào.")

    def upload_document(self):
        if not self.document_dialog:
            self.document_dialog = uic.loadUi("gui/upload_document.ui")
            self.document_dialog.choose_file_btn.clicked.connect(self.choose_file)
            self.document_dialog.upload_btn.clicked.connect(self.process_upload)

        self.document_dialog.show()

    def choose_file(self):
        options = QFileDialog.Option.DontUseNativeDialog
        file_filter = "All Files (*);;PDF Files (*.pdf);;Word Documents (*.docx);;PowerPoint Presentations (*.pptx)"
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn file", "", file_filter, options=options)
        if file_path:
            self.document_dialog.file_path_label.setText(file_path)

    def process_upload(self):
        file_path = self.document_dialog.file_path_label.text()
        if not file_path:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn file!")
            return

        mon_hoc = self.document_dialog.mon_hoc_combo.currentText()
        ghi_chu = self.document_dialog.ghi_chu_text.text()

        # Lưu trữ thông tin tài liệu
        new_document = {
            "nguoi_dang": self.tai_khoan["Thông tin tài khoản"]["ten_tai_khoan"] if hasattr(self, "tai_khoan") else "Admin",
            "ma_tai_lieu": self.generate_document_id(),
            "tai_lieu_mon": mon_hoc,
            "ngay_dang": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ghi_chu": ghi_chu,
            "duong_dan": file_path,
            "yeu_thich": [],
        }
        self.documents.append(new_document)
        self.save_documents()
        self.load_documents()

        self.document_dialog.close()
        QMessageBox.information(self, "Thông báo", "Tải lên tài liệu thành công!")

    def generate_document_id(self):
        # Tạo mã tài liệu duy nhất
        return str(int(time.time()))

    def save_documents(self):
        with open("documents.json", "w", encoding="utf-8") as f:
            json.dump(self.documents, f, indent=4, ensure_ascii=False)
            
    def show_coming_soon(self):
        if not self.coming_soon:
            self.coming_soon = ComingSoon()
        self.coming_soon.show()
        # Tắt màn hình coming_soon sau 5 giây
        QTimer.singleShot(5000, self.coming_soon.close)