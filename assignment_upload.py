from PyQt6.QtWidgets import QFileDialog, QMessageBox, QComboBox
from PyQt6 import uic
import os

class AssignmentUpload:
    def upload_btvn(self):
        # Khởi tạo btvn_upload là None nếu chưa được khởi tạo
        if not hasattr(self, 'btvn_upload'):
            self.btvn_upload = None
        
        if not self.btvn_upload:
            self.btvn_upload = uic.loadUi("gui/btvn-upload.ui")
            self.btvn_upload.clickTo_Upload.clicked.connect(self.upload_click)
            self.loai_file_combo = QComboBox(self.btvn_upload)
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
            self, "Chọn file", "", file_filter, options=options
        )

        if file_path:
            folder_path = os.path.join("btvn", loai_file)
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

                if hasattr(self, "xem_bai_tap_dialog") and self.xem_bai_tap_dialog:
                    self.update_btvn_list()

            except Exception as e:
                self.msg_box.setText(f"Lỗi khi tải lên: {e}")
                self.msg_box.exec()

        self.btvn_upload.hide()
        self.show()