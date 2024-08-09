from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QWidget, QLabel, QProgressBar, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6 import uic
import json

class ProfileTC(QMainWindow):
    def __init__(self, data):
        super().__init__()
        uic.loadUi("gui/profile_tc.ui", self)
        self.data = data

        self.achievement_layout = self.findChild(QWidget, "Achievement_layout")
        self.achievement_list = [
            "Học tập chăm chỉ",
            "Khám phá tri thức",
            "Tinh thần tự học",
            "Bậc thầy ghi nhớ",
            "Kế hoạch hoàn hảo",
            "Học hỏi bạn bè",
            "Tinh thần hợp tác",
            "Mọt sách chính hiệu",
            "Tham gia câu lạc bộ",
            "Tinh thần cầu tiến",
            "kĩ năng vô biên",
            "Trì hoãn là gì?",
            "Đốt cháy rào cản ngôn ngữ",
            "Thành thạo tiếng mẹ đẻ",
            "Khỏi cần máy tính",
            "Công dân mẫu mực",
            "Dân văn phòng đây rồi",
            "Không gì làm khó được tôi",
            "Sử địa cân tất",
            "Cao thủ luyện đề",
            "Bậc thầy ghi chú",
            "Quản lý thời gian thông minh",
            "Thách thức bản thân",
            "Máy quét kiến thức",
            "Biên tập viên tài năng",
            "Siêu tập trung",
            "Sáng tạo nội dung",
            "Truyền cảm hứng",
            "Thần đồng công nghệ",
            "Thám hiểm MasterEdu",
            "Thợ săn kiến thức",
            "Siêu trí nhớ",
            "Học tập mọi lúc – mọi nơi",
            "Học sinh xuất sắc của năm",
            "Thần tốc",
            "Cú đêm",
            "Học – học nữa – học mãi",
            "Người tiên phong",
            "Người bạn đồng hành",
            "Cộng tác viên tiềm năng",
            "Ngày đặc biệt",
            "Nhà phát minh tiềm năng",
            "Tín đồ công nghệ",
            "Tester đại tài",
            "Sao hay soi quá à",
            "Thánh nhọ",
            "Ăn gì xui vậy má?",
            "Học sinh toàn diện",
            "Não khỉ",
            "Bớt spam đi nào",
            "The Chosen One",
            "You Are The Best",
            "Chúc mừng năm mới",
            "Lỗi tại anh, tại ổng, tại nó, tại…",
            "Fan cứng của thông báo",
            "Mắc gì nhập sai?",
            "Mạng mạnh đếy",
            "Lời tri ân",
            "Ê mic kìa",
            "Ông hoàng/bà hoàng “bùng” học",
            "Học quá trở lại",
            "Bách khoa toàn thư",
            "Giải mã tuật toán"
        ]
        self.achievement_data = self.load_achievement_data()
        self.create_achievement_widgets()

        self.account_name = self.findChild(QLabel, "account_name")
        self.call_number = self.findChild(QLabel, "call_number")
        self.jobs = self.findChild(QLabel, "jobs")
        self.other_number = self.findChild(QLabel, "jobs_2")  # Chú ý: other_number sử dụng jobs_2 trong file ui
        self.gender = self.findChild(QLabel, "gender")
        self.account_id = self.findChild(QLabel, "account_id")
        self.numbe_av = self.findChild(QLabel, "call_number_2") # Chú ý: numbe_av sử dụng call_number_2 trong file ui
        self.profile_pic = self.findChild(QLabel, "profile_pic")

        self.update_labels()
        self.profile_pic.mousePressEvent = self.change_profile_pic

    def load_achievement_data(self):
        try:
            with open("tk_tc_data.json", "r", encoding="utf-8") as f:
                tk_tc_data = json.load(f)
            for teacher in tk_tc_data["Danh_sach_tai_khoan_teacher"]:
                if teacher.get("so_dien_thoai") == "0987654321":
                    return teacher.get("Thành tựu", {})
        except FileNotFoundError:
            return {}

    def create_achievement_widgets(self):
        layout = self.achievement_layout.layout()
        for i, achievement_name in enumerate(self.achievement_list):
            new_achievement_layout = QWidget()
            new_achievement_layout.setStyleSheet(self.achievement_layout.styleSheet())
            new_layout = QVBoxLayout()
            new_achievement_layout.setLayout(new_layout)

            new_achieviement_pic = QLabel()
            new_achieviement_pic.setPixmap(QPixmap("icons/achievement.png").scaled(
                new_achieviement_pic.width(),
                new_achieviement_pic.height(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))
            new_layout.addWidget(new_achieviement_pic)

            new_ten_thanh_tuu = QLabel()
            new_ten_thanh_tuu.setText(achievement_name)
            new_ten_thanh_tuu.setStyleSheet("font: 600  'Bahnschrift'; background-color: none; color: rgb(129, 201, 255); align-item: center;")
            new_ten_thanh_tuu.setAlignment(Qt.AlignmentFlag.AlignCenter)
            new_layout.addWidget(new_ten_thanh_tuu)

            new_progressBar = QProgressBar()
            new_progressBar.setStyleSheet("""
                #progressBar {
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                    background-color: #E0E0E0;
                }
                #progressBar::chunk {
                    background-color: #2196F3;
                    width: 10px; 
                    margin: 0.5px;
                    textVisible: False;
                }
            """)
            achievement_data = self.achievement_data.get(achievement_name, {})
            if isinstance(achievement_data, dict):
                level_count = sum(achievement_data.values())
                progress = min(level_count * 20, 100)
            else:
                progress = 100 if achievement_data else 0
            new_progressBar.setValue(progress)
            new_progressBar.setTextVisible(False)
            new_progressBar.setOrientation(Qt.Orientation.Horizontal)
            new_progressBar.setTextDirection(QProgressBar.TextDirection.BottomToTop)
            new_layout.addWidget(new_progressBar)

            layout.addWidget(new_achievement_layout)

    def update_labels(self):
        try:
            with open("tk_tc_data.json", "r", encoding="utf-8") as f:
                tk_tc_data = json.load(f)
            for teacher in tk_tc_data["Danh_sach_tai_khoan_teacher"]:
                if teacher.get("so_dien_thoai") == "0987654321":
                    ten_tai_khoan = teacher.get("ten_tai_khoan", "N/A")
                    so_dien_thoai = teacher.get("so_dien_thoai", "N/A")
                    nghe_nghiep = "Giáo viên"
                    gioi_tinh = teacher.get("gender", "N/A")
                    id_tai_khoan = teacher.get("id_tai_khoan", "N/A")
                    break
        except FileNotFoundError:
            ten_tai_khoan = "N/A"
            so_dien_thoai = "N/A"
            nghe_nghiep = "N/A"
            gioi_tinh = "N/A"
            id_tai_khoan = "N/A"

        self.account_name.setText(ten_tai_khoan)
        self.call_number.setText(so_dien_thoai)
        self.jobs.setText(nghe_nghiep)
        self.other_number.setText(so_dien_thoai)  # Sử dụng jobs_2
        self.gender.setText(gioi_tinh)
        self.account_id.setText(str(id_tai_khoan))
        self.numbe_av.setText(str(self.count_achieved_achievements()))  # Sử dụng call_number_2

    def count_achieved_achievements(self):
        count = 0
        for achievement_data in self.achievement_data.values():
            if isinstance(achievement_data, dict):
                count += sum(achievement_data.values())
            elif achievement_data:
                count += 1
        return count

    def change_profile_pic(self, event):
        reply = QMessageBox.question(
            self,
            "Đổi hình nền",
            "Bạn có muốn đổi hình nền không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            options = QFileDialog.Option.DontUseNativeDialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Chọn hình nền",
                "",
                "Image Files (*.png *.jpg *.jpeg)",
                options=options
            )
            if file_path:
                self.profile_pic.setPixmap(QPixmap(file_path).scaled(
                    self.profile_pic.width(),
                    self.profile_pic.height(),
                    Qt.AspectRatioMode.KeepAspectRatio
                ))