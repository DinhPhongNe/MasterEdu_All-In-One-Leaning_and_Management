from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
import pyaudio
import wave
from PyQt6.QtCore import QTimer

class AchievementToastApp(App):
    def build(self):
        return Label()

    def show_toast(self, achievement_name):
        # Sử dụng QTimer để trì hoãn việc tạo popup
        QTimer.singleShot(0, lambda: self._show_popup(achievement_name))

    def _show_popup(self, achievement_name):
        # Tạo và hiển thị popup
        content = Label(text=f"Bạn đã nhận được thành tựu:\n{achievement_name}")
        popup = Popup(title="Thành tựu mới!", content=content, size_hint=(None, None), size=(400, 200))
        popup.open()

        # Phát âm thanh
        try:
            wf = wave.open("sound/complete_acv.mp3", 'rb')
            p = pyaudio.PyAudio()

            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Lỗi phát âm thanh: {e}")

# Tạo một instance duy nhất của ứng dụng
achievement_app = AchievementToastApp()