from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import uic

class SplashScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/ui_Form_progress.ui", self)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

        # Cập nhật labelSubName sau mỗi khoảng thời gian
        QTimer.singleShot(1000, lambda: self.labelSubName.setText("<strong>LOADING</strong><font style='color:white'> EXPLOITS</font>"))
        QTimer.singleShot(1500, lambda: self.labelSubName.setText("<strong>LOADING</strong><font style='color:white'> DATABASE</font>"))
        QTimer.singleShot(3000, lambda: self.labelSubName.setText("<strong>LOADING</strong><font style='color:white'> USER INTERFACE</font>"))

    def update_progress(self):
        current_value = self.progressBar.value()
        if current_value < 100:
            self.progressBar.setValue(current_value + 1)
        else:
            self.timer.stop()
            self.close()

    def finish(self, window):
        self.timer.timeout.connect(lambda: window.show())
        self.close()  # Đóng splash screen sau khi hiển thị cửa sổ chính