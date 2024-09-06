from PyQt6.QtWidgets import QApplication
import sys
from login_register import LoginRegister
from splash_screen import SplashScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Hiển thị splash screen
    splash = SplashScreen()
    splash.show()

    # Khởi tạo LoginRegister sau khi splash screen kết thúc
    window = LoginRegister()
    splash.finish(window)  

    sys.exit(app.exec())