import os
import time
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QWidget, QLabel, QProgressBar, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QDialog, QListWidget, QComboBox, QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QUrl, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6 import uic
from PyQt6.QtMultimedia import QSoundEffect
import json
import copy
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from kivy.core.audio import SoundLoader
import threading

file_lock = threading.Lock()
class AchievementNotification(QWidget):
    def __init__(self, parent=None, achievement_name=""):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        self.label = QLabel(f"Thành tựu mới!\n{achievement_name}")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)  # Thời gian hiển thị (milliseconds)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_notification)

    def show_notification(self):
        self.show()
        self.animation.start()
        self.timer.start(3000)  # Hiển thị trong 3 giây (milliseconds)

    def hide_notification(self):
        self.animation.setDirection(QPropertyAnimation.Direction.Backward)
        self.animation.start()
        self.animation.finished.connect(self.hide)
        
class JSONFileHandler(FileSystemEventHandler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def on_modified(self, event):
        if os.path.basename(event.src_path) == "diem_database.json":
            print("Phát tín hiệu achievement_unlocked...")
            self.signal.emit()

class AchievementMonitorThread(QThread):
    achievement_unlocked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.observer = Observer()

    def run(self):
        event_handler = JSONFileHandler(self.achievement_unlocked)
        self.observer.schedule(event_handler, path='.', recursive=False)
        self.observer.start()
        while True:
            time.sleep(1)

    def stop(self):
        self.observer.stop()
        self.wait()
            
class ProfileHS(QMainWindow):
    def __init__(self, data, tai_khoan):
        super().__init__()
        uic.loadUi("gui/profile_hs.ui", self)
        self.data = data
        self.tai_khoan = tai_khoan
        self.old_achievements = copy.deepcopy(self.load_achievement_data())
        self.achievement_monitor = AchievementMonitorThread(self)
        self.achievement_monitor.achievement_unlocked.connect(self.check_for_new_achievements)
        self.achievement_monitor.start()
        self.profile_goback = self.findChild(QPushButton, "profile_goback")
        self.profile_goback.clicked.connect(self.go_back) 
        
        # Khởi tạo QSystemTrayIcon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("gui/icon_pack/12.jpeg"))  # Thay thế "icon.png" bằng đường dẫn đến icon của bạn
        self.tray_icon.setVisible(True)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_for_new_achievements)
        self.timer.start(1000)  # 1000 milliseconds = 1 giây

        self.update_profile()
        self.profile_pic.mousePressEvent = self.change_profile_pic
        # Tạo menu cho tray icon
        self.tray_menu = QMenu()
        self.tray_menu.addAction("Thoát", self.close)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.achievement_mapping = {
            "Study hard": "Học tập chăm chỉ",
            "Knowledge Discovery": "Khám phá tri thức",
            "Self-learning Spirit": "Tinh thần tự học",
            "Remember the Teacher": "Bậc thầy ghi nhớ",
            "Perfect Plan": "Kế hoạch hoàn hảo",
            "Learning from friends": "Học hỏi bạn bè",
            "Spirit of cooperation": "Tinh thần hợp tác",
            "A real book": "Mọt sách chính hiệu",
            "Join the club": "Tham gia câu lạc bộ",
            "Spirit of progress": "Tinh thần cầu tiến",
            "Unlimited skills": "Kỹ năng vô biên",
            "What is procrastination?": "Trì hoãn là gì?",
            "Burning the language barrier": "Đốt cháy rào cản ngôn ngữ",
            "Fluent in mother tongue": "Thành thạo tiếng mẹ đẻ",
            "No need for a computer": "Khỏi cần máy tính",
            "Exemplary Citizen": "Công dân mẫu mực",
            "Here comes the clerk": "Dân văn phòng đây rồi",
            "Nothing can make it difficult for me": "Không gì làm khó được tôi",
            "Geography is balanced": "Sử địa cân tất",
            "Practice test master": "Cao thủ luyện đề",
            "Note-taking master": "Bậc thầy ghi chú",
            "Smart time management": "Quản lý thời gian thông minh",
            "Challenge yourself": "Thách thức bản thân",
            "Knowledge Scan Machine": "Máy quét kiến thức",
            "Talented Editor": "Biên tập viên tài năng",
            "Super Focus": "Siêu tập trung",
            "Content Creation": "Sáng tạo nội dung",
            "Inspiration": "Truyền cảm hứng",
            "Tech Genius": "Thần đồng công nghệ",
            "Explore MasterEdu": "Thám hiểm MasterEdu",
            "Knowledge Hunter": "Thợ săn kiến thức",
            "Super Memory": "Siêu trí nhớ",
            "Learn Anytime - Anywhere": "Học tập mọi lúc - mọi nơi",
            "Excellent student of the year": "Học sinh xuất sắc của năm",
            "The Flash": "Thần tốc",
            "Night Owl": "Cú đêm",
            "Study - Study more - Study forever": "Học - học nữa - học mãi",
            "Pioneer": "Người tiên phong",
            "Companion": "Người bạn đồng hành",
            "Potential Contributor": "Cộng tác viên tiềm năng",
            "Special Day": "Ngày đặc biệt",
            "Potential Inventor": "Nhà phát minh tiềm năng",
            "Technology Believer": "Tín đồ công nghệ",
            "Great Tester": "Tester đại tài",
            "Why so observant?": "Sao hay soi quá à",
            "Lucky": "Thánh nhọ",
            "What did you eat that's so bad?:": "Ăn gì xui vậy má?",
            "Comprehensive student": "Học sinh toàn diện",
            "Brain Freeze": "Não khi",
            "Go away spam": "Bớt spam đi nào",
            "The Chosen One": "The Chosen One",
            "You Are The Best": "You Are The Best",
            "Happy New Year": "Chúc mừng năm mới",
            "It's his fault, his fault, his fault,...": "Lỗi tại anh, tại ổng, tại nó, tại...",
            "Notification enthusiast": "Fan cứng của thông báo",
            "What's wrong with the keyboard?:": "Mắc gì nhập sai?",
            "That network": "Mạng mạnh đấy",
            "Gratitude": "Lời tri ân",
            "Hey, the mic": "Ê mic kìa",
            "King/Queen of skipping class": "Ông hoàng/bà hoàng “bùng” học",
            "Back to overstudying": "Học quá trở lại",
            "Encyclopedia": "Bách khoa toàn thư",
            "Decode the math problem": "Giải mã thuật toán"
        }
        
        self.achievement_widgets = []  # Danh sách chứa (QLabel, QProgressBar) cho mỗi thành tựu
        for i in range(1, 11):
            label = self.findChild(QFrame, f"Achievement_layout_{i}").findChild(QLabel, f"ten_thanh_tuu_{i}")
            progress_bar = self.findChild(QFrame, f"Achievement_layout_{i}").findChild(QProgressBar, f"progressBar_{i}")
            self.achievement_widgets.append((label, progress_bar))
        self.selected_achievements = {}

        self.account_name = self.findChild(QLabel, "account_name")
        self.call_number = self.findChild(QLabel, "call_number")
        self.jobs = self.findChild(QLabel, "jobs")
        self.other_number = self.findChild(QLabel, "other_number")
        self.gender = self.findChild(QLabel, "gender")
        self.account_id = self.findChild(QLabel, "account_id")
        self.numbe_av = self.findChild(QLabel, "numbe_av")
        self.profile_pic = self.findChild(QLabel, "profile_pic")
        self.last_online = self.findChild(QLabel, "last_online")
        self.achievement_setting_btn = self.findChild(QPushButton, "ahievement_setting_btn")
        self.achievement_setting_btn.clicked.connect(self.show_achievement_dialog)

        self.update_profile()
        self.profile_pic.mousePressEvent = self.change_profile_pic
        self.old_achievements = copy.deepcopy(self.load_achievement_data())  # Lưu giá trị cũ của thành tựu
        
        # Ánh xạ tên thành tựu tiếng Anh sang tiếng Việt

    def check_for_new_achievements(self):
        new_achievements = self.load_achievement_data()
        achievement_to_show = None

        for eng_name, vn_name in self.achievement_mapping.items():
            old_achievement = self.old_achievements.get(eng_name)
            new_achievement = new_achievements.get(eng_name)

            if isinstance(old_achievement, dict) and isinstance(new_achievement, dict):
                for level in old_achievement.keys():
                    if not old_achievement.get(level) and new_achievement.get(level):
                        achievement_to_show = vn_name
                        break
            elif not old_achievement and new_achievement:
                achievement_to_show = vn_name

            if achievement_to_show:
                break

        self.old_achievements = copy.deepcopy(new_achievements)
        self.update_achievement_display(new_achievements)

        if achievement_to_show:
            self.show_achievement_notification(achievement_to_show)
            
    def go_back(self):
        from menu_select_hs import MenuSelectHS  # Di chuyển dòng import vào đây
        self.menu_select_hs = MenuSelectHS(self.data, self.tai_khoan)
        self.menu_select_hs.show()
        self.close()
        
    def show_achievement_notification(self, achievement_name):
        # Tạo pop-up thông báo
        notification = AchievementNotification(self, achievement_name)
        notification.show_notification()

        # Phát âm thanh
        sound = QSoundEffect(self)
        sound.setSource(QUrl.fromLocalFile("sound/complete_acv.mp3"))
        sound.play()

    def closeEvent(self, event):
        # Dừng thread theo dõi khi đóng cửa sổ
        self.achievement_monitor.stop()
        super().closeEvent(event)
        
    def update_profile(self):
        # Tìm kiếm thông tin học sinh dựa trên ID
        try:
            for student in self.data["Danh_sach_hoc_sinh"]:
                if student["Thông tin tài khoản"]["id_tai_khoan"] == self.tai_khoan["Thông tin tài khoản"]["id_tai_khoan"]:
                    self.account_name.setText(student["Thông tin tài khoản"]["ten_tai_khoan"])
                    # Chuyển đổi số điện thoại thành chuỗi:
                    self.call_number.setText(str(student["Thông tin tài khoản"]["so_dien_thoai"]))
                    self.jobs.setText("Học sinh")
                    # Chuyển đổi số điện thoại thành chuỗi:
                    self.other_number.setText(str(student["Thông tin tài khoản"]["so_dien_thoai"]))
                    self.gender.setText(student["Thông tin tài khoản"].get("gender", "N/A"))
                    self.account_id.setText(str(student["Thông tin tài khoản"]["id_tai_khoan"]))
                    self.last_online.setText("Chưa cập nhật")
                    self.numbe_av.setText(str(self.count_achieved_achievements(student["Thành tựu"])))
                    self.update_achievement_display(student["Thành tựu"])
                    break
            else:
                # Nếu không tìm thấy học sinh hoặc khóa 'id_tai_khoan' không tồn tại
                self.account_name.setText("N/A")
                self.call_number.setText("N/A")
                self.jobs.setText("N/A")
                self.other_number.setText("N/A")
                self.gender.setText("N/A")
                self.account_id.setText("N/A")
                self.last_online.setText("N/A")
                self.numbe_av.setText("N/A")

            # Kiểm tra thay đổi thành tựu sau khi cập nhật thông tin profile
            self.check_for_new_achievements()
        except Exception as e:
            print(f"Lỗi trong update_profile: {e}")
        
    def count_achieved_achievements(self, achievements):
        count = 0
        for achievement_data in achievements.values():
            if isinstance(achievement_data, dict):
                count += sum(1 for level_achieved in achievement_data.values() if level_achieved)
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

    def show_achievement_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Chọn thành tựu hiển thị")
        dialog.setStyleSheet("background-color: #356a9c; color: white;")
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        # ComboBox để chọn ô
        self.slot_combo_box = QComboBox()
        for i in range(10):
            self.slot_combo_box.addItem(f"Ô {i+1}")
        layout.addWidget(QLabel("Chọn ô hiển thị:"))
        layout.addWidget(self.slot_combo_box)

        # ListWidget để chọn thành tựu (di chuyển ra ngoài vòng lặp)
        self.achievement_list_widget = QListWidget()
        layout.addWidget(QLabel("Chọn thành tựu:"))
        layout.addWidget(self.achievement_list_widget)

        # Kết nối sự kiện thay đổi lựa chọn ô với hàm cập nhật danh sách thành tựu
        self.slot_combo_box.currentIndexChanged.connect(self.update_achievement_list)

        # Hiển thị danh sách thành tựu cho ô đầu tiên mặc định
        self.update_achievement_list(0)

        confirm_button = QPushButton("Xác nhận")
        confirm_button.setStyleSheet("background-color: rgb(129, 201, 255); color: #F8F2EC; border-radius: 10px;")
        confirm_button.clicked.connect(lambda: self.select_achievements(dialog))
        layout.addWidget(confirm_button)

        dialog.exec()

    def update_achievement_list(self, index):
        self.achievement_list_widget.clear()
        for achievement_name in self.achievement_mapping.values():
            self.achievement_list_widget.addItem(achievement_name)

    def select_achievements(self, dialog):
        selected_slot = self.slot_combo_box.currentIndex()
        selected_achievement = self.achievement_list_widget.currentItem().text() if self.achievement_list_widget.currentItem() else None
        self.selected_achievements[selected_slot] = selected_achievement
        self.update_achievement_display(self.load_achievement_data())
        sound = SoundLoader.load("sound/complete_acv.mp3")
        if sound:
            sound.play()

        self.update_achievement_display(self.load_achievement_data())
        dialog.close()

    def load_achievement_data(self):
        with file_lock:
            for student in self.data["Danh_sach_hoc_sinh"]:
                if student["Thông tin tài khoản"]["id_tai_khoan"] == self.tai_khoan["Thông tin tài khoản"]["id_tai_khoan"]:
                    achievements = student.get("Thành tựu", {})
                    # Chuyển đổi giá trị chuỗi "false" sang boolean False
                    for key, value in achievements.items():
                        if isinstance(value, dict):
                            for level, achieved in value.items():
                                if achieved == "false":
                                    achievements[key][level] = False
                        elif value == "false":
                            achievements[key] = False
                    return achievements
            return {}
    
    def update_achievement_display(self, achievements):
        # Hiển thị các thành tựu được chọn (KHÔNG kiểm tra thay đổi file JSON ở đây)
        for i in range(10):
            if i < len(self.achievement_widgets):
                label, progress_bar = self.achievement_widgets[i]
                achievement_name = self.selected_achievements.get(i)
                if achievement_name:
                    if label is not None:
                        label.setText(achievement_name)
                    if progress_bar is not None:
                        for eng_name, vn_name in self.achievement_mapping.items():
                            if vn_name == achievement_name:
                                achievement_data = achievements.get(eng_name, {})
                                if isinstance(achievement_data, dict):
                                    level_count = sum(achievement_data.values())
                                    progress = min(level_count * 20, 100)
                                else:
                                    progress = 100 if achievement_data else 0
                                progress_bar.setValue(progress)
                                break
                else:
                    # Nếu không có thành tựu được chọn cho ô này, xóa nội dung
                    if label is not None:
                        label.clear()
                    if progress_bar is not None:
                        progress_bar.setValue(0)
        # Cập nhật giá trị cũ của thành tựu
        self.old_achievements = copy.deepcopy(achievements)