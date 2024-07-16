from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox, QInputDialog, QFileDialog
import os
import shutil

class ViewAssignments:
    def show_xem_bai_tap_dialog(self):
        if not self.xem_bai_tap_dialog:
            self.xem_bai_tap_dialog = QDialog(self)
            self.xem_bai_tap_dialog.setWindowTitle("Xem Bài Tập và Video Bài Giảng")

            layout = QVBoxLayout()
            self.btvn_list = QListWidget()
            layout.addWidget(QLabel("Bài tập:"))
            layout.addWidget(self.btvn_list)
            self.btvn_list.itemClicked.connect(self.download_btvn)
            delete_btn = QPushButton("Xóa")
            delete_btn.clicked.connect(self.delete_btvn)
            layout.addWidget(delete_btn)
            rename_btn = QPushButton("Chỉnh Sửa Tên")
            rename_btn.clicked.connect(self.rename_btvn)
            layout.addWidget(rename_btn)
            download_btn = QPushButton("Tải Về")
            download_btn.clicked.connect(self.download_btvn)
            layout.addWidget(download_btn)

            self.video_list = QListWidget()
            layout.addWidget(QLabel("Video bài giảng:"))
            layout.addWidget(self.video_list)
            self.video_list.itemDoubleClicked.connect(self.play_video)
            self.update_btvn_list()
            self.xem_bai_tap_dialog.setLayout(layout)
        self.xem_bai_tap_dialog.show()

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
                            self.btvn_list.addItem(file_name)
                        elif loai_file == "Video bài giảng":
                            self.video_list.addItem(file_name)
                else:
                    if loai_file == "Bài tập":
                        self.btvn_list.addItem("Hiện tại không có bài tập")
                    elif loai_file == "Video bài giảng":
                        self.video_list.addItem("Hiện tại không có video bài giảng")

    def delete_btvn(self):
        selected_item = self.btvn_list.currentItem()
        if selected_item and selected_item.text() != "Hiện tại không có bài tập":
            file_name = selected_item.text()
            folder_path = "btvn/Bài tập"  # Đường dẫn đến thư mục "Bài tập"
            file_path = os.path.join(folder_path, file_name)

            confirm_box = QMessageBox()
            confirm_box.setWindowTitle("Xác nhận xóa")
            confirm_box.setText(f"Bạn có chắc muốn xóa {file_name}?")
            confirm_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            result = confirm_box.exec()
            if result == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(file_path)
                    self.update_btvn_list()
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
            folder_path = "btvn/Bài tập"
            old_file_path = os.path.join(folder_path, old_file_name)

            new_file_name, ok = QInputDialog.getText(
                self, "Đổi tên bài tập", "Nhập tên mới:", text=old_file_name
            )
            if ok and new_file_name:
                new_file_path = os.path.join(folder_path, new_file_name)
                try:
                    os.rename(old_file_path, new_file_path)
                    self.update_btvn_list()
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
            folder_path = "btvn/Bài tập"  # Đường dẫn đến thư mục "Bài tập"
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
                    shutil.copy2(file_path, save_path)
                    self.msg_box.setWindowTitle("Thông báo")
                    self.msg_box.setIcon(QMessageBox.Icon.Information)
                    self.msg_box.setText("Tải xuống bài tập thành công!")
                    self.msg_box.exec()
                except Exception as e:
                    self.msg_box.setText(f"Lỗi khi tải xuống: {e}")
                    self.msg_box.exec()

    def play_video(self, item):
        file_name = item.text()
        file_path = os.path.join("btvn/Video bài giảng", file_name)
        if os.path.exists(file_path):
            from video_player import VideoPlayer  # Import tại đây
            self.video_player = VideoPlayer(file_path, self)
            self.video_player.show()
            
    def show_new_assignment_notification(self, path):
        if hasattr(self, 'current_user') and self.current_user == "student":
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Nhắc Nhở")
            msg_box.setText("Giáo viên đã giao một bài tập/bài giảng cho bạn, bạn hãy đi xem nhé!")
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Close | QMessageBox.StandardButton.Ok)
            msg_box.exec()

    def check_new_assignments(self):
        if hasattr(self, 'current_user') and self.current_user == "student":
            folder_path = "btvn"
            if os.path.exists(folder_path):
                file_list = os.listdir(folder_path)
                if file_list:
                    newest_file_time = max(os.path.getmtime(os.path.join(folder_path, f)) for f in file_list)
                    if getattr(self, 'last_login_time', None) is None or newest_file_time > self.last_login_time:
                        self.show_new_assignment_notification(folder_path)