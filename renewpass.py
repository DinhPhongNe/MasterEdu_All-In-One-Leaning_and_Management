from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QLineEdit
from PyQt6 import uic

class RenewPass(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/renewpass.ui", self)
        self.renew_btn.clicked.connect(self.renew_clicked)
        self.return_btn.clicked.connect(self.return_clicked)
        self.phone_validator = QIntValidator()
        self.phone_validator.setBottom(0)
        self.phone_validator.setTop(999999999)
        self.PhoneRC.setValidator(self.phone_validator)
        self.PassRC.setEchoMode(QLineEdit.EchoMode.Password)
        self.RePassRC.setEchoMode(QLineEdit.EchoMode.Password)

        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Lỗi")
        self.msg_box.setIcon(QMessageBox.Icon.Warning)
        self.msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")

    def renew_clicked(self):
        phone = self.PhoneRC.text()
        password = self.PassRC.text()
        repass = self.RePassRC.text()

        if not phone:
            self.msg_box.setText("Vui lòng nhập số điện thoại!")
            self.msg_box.exec()
            return
        if not password:
            self.msg_box.setText("Vui lòng nhập mật khẩu!")
            self.msg_box.exec()
            return
        if not repass:
            self.msg_box.setText("Vui lòng nhập lại mật khẩu!")
            self.msg_box.exec()
            return
        if password != repass:
            self.msg_box.setText("Mật khẩu không trùng khớp!")
            self.msg_box.exec()
            return

        self.hide()
        # Thực hiện logic đổi mật khẩu tại đây

    def return_clicked(self):
        self.hide()
        # Hiển thị lại giao diện đăng nhập giáo viên