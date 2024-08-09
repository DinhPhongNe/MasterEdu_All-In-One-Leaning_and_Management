import simpleaudio as sa
from win10toast import ToastNotifier
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

class MainWindow(QWidget):
    # ... (Phần còn lại của code giữ nguyên)

    def show_achievement(self):
        # Hiển thị thông báo toast
        toaster = ToastNotifier()
        toaster.show_toast("Thành tựu mới!", "Bạn đã nhận được thành tựu \"Học tập chăm chỉ\"!", duration=5)

        # Phát âm thanh bằng simpleaudio
        try:
            wave_obj = sa.WaveObject.from_wave_file("sound/complete_acv.mp3")
            play_obj = wave_obj.play()
            play_obj.wait_done()  # Chờ cho âm thanh phát xong
        except Exception as e:
            print(f"Lỗi phát âm thanh: {e}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()