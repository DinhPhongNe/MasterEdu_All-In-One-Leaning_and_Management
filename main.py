from PyQt6.QtWidgets import QApplication
import sys
from login_register import LoginRegister

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginRegister()
    window.show()
    sys.exit(app.exec())