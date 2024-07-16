from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QWidget
import vlc
from PyQt6.QtWidgets import QMessageBox

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
        self.stop_button.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.video_frame)
        layout.addWidget(self.stop_button)

        self.player.play()
        self.showFullScreen()

        self.check_time_timer = QTimer(self)
        self.check_time_timer.timeout.connect(self.check_video_time)
        self.check_time_timer.start(1000)

    def check_video_time(self):
        current_time = self.player.get_time()
        video_duration = self.media.get_duration()

        if current_time >= video_duration // 2:
            self.stop_button.setEnabled(True)
            self.check_time_timer.stop()

    def stop_video(self):
        self.player.stop()
        self.close()

    def closeEvent(self, event):
        if not self.stop_button.isEnabled():
            QMessageBox.warning(
                self, "Thông báo", "Hãy cố gắng xem hết video em nhé!"
            )
            event.ignore()
        else:
            event.accept()