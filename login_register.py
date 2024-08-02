from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QPushButton, QComboBox, QLineEdit
from PyQt6 import uic
import json
from student_main import StudentMain
from teacher_main import TeacherMain
from renewpass import RenewPass

class LoginRegister(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("gui/menu.ui", self)
        self.phone_validator = QIntValidator()
        self.phone_validator.setBottom(0)
        self.phone_validator.setTop(999999999)
        self.HocSinh_btn.clicked.connect(self.login_hs)
        self.GiaoVien_btn.clicked.connect(self.login_tc)
        self.Register_btn.clicked.connect(self.register_user)
        self.quit_btn.clicked.connect(self.quit)

        self.teacher_login = None
        self.student_login = None
        self.register = None
        self.teacher_main = None
        self.student_main = None
        self.renewpass = None

        self.load_data()

        self.msg_box = QMessageBox()
        self.msg_box.setWindowTitle("Lỗi")
        self.msg_box.setIcon(QMessageBox.Icon.Warning)
        self.msg_box.setStyleSheet("background-color: #F8F2EC; color: #356a9c")

    def quit(self):
        window.close()

    def login_tc(self):
        if not self.teacher_login:
            self.teacher_login = uic.loadUi("gui/login-teacher.ui")
            self.PhoneTC = self.teacher_login.findChild(QLineEdit, "PhoneTC")
            self.PhoneTC.setValidator(self.phone_validator)
            self.PassTC = self.teacher_login.findChild(QLineEdit, "PassTC")
            self.teacher_login.GiaoVienLogin_btn.clicked.connect(self.check_login_tc)
            self.teacher_login.goback_tc_btn.clicked.connect(self.goback_tc)
            self.teacher_login.forgo_pass_tc.clicked.connect(self.renew_password)

        self.teacher_login.show()
        self.hide()

    def check_login_tc(self):
        phone = self.PhoneTC.text()
        password = self.PassTC.text()

        if not phone:
            self.msg_box.setText("Vui lòng nhập số điện thoại!")
            self.msg_box.exec()
            return
        if not password:
            self.msg_box.setText("Vui lòng nhập mật khẩu!")
            self.msg_box.exec()
            return

        phone_number = self.PhoneTC.text()
        if len(phone_number) != 10 or not phone_number.startswith('0'):
            self.msg_box.setText("Số điện thoại không hợp lệ!")
            self.msg_box.exec()
            return

        if phone == "0987654321" and password == "admin":
            self.teacher_login.close()
            self.open_teacher_select_menu()
        else:
            self.msg_box.setText("Số điện thoại hoặc mật khẩu sai")
            self.msg_box.exec()

    def open_teacher_select_menu(self):
        from menu_select_tc import MenuSelectTC
        self.teacher_select_menu = MenuSelectTC(self.data)
        self.teacher_select_menu.show()
            
    def open_teacher_main(self):
        self.teacher_main = TeacherMain(self.data)
        self.teacher_main.show()
        self.teacher_login.hide()

    def goback_tc(self):
        self.teacher_login.hide()
        self.show()

    def goback_hs(self):
        self.student_login.hide()
        self.show()

    def renew_password(self):
        if not self.renewpass:
            self.renewpass = RenewPass()
        self.renewpass.show()
        self.hide()

    def register_user(self):
        if not self.register:
            self.register = uic.loadUi("gui/register.ui")
            self.Phone_reg = self.register.findChild(QLineEdit, "Phone_reg")
            self.Phone_reg.setValidator(self.phone_validator)
            self.pass_reg = self.register.findChild(QLineEdit, "pass_reg")
            self.re_pass_reg = self.register.findChild(QLineEdit, "re_pass_reg")
            self.vai_tro = self.register.findChild(QComboBox, "vai_tro")
            self.vai_tro.addItems(["Giáo viên", "Học sinh"])
            self.register_btn = self.register.findChild(QPushButton, "register_btn")
            self.register_btn.clicked.connect(self.process_registration)
            self.goback_reg = self.register.findChild(QPushButton, "goback_reg")
            self.goback_reg.clicked.connect(self.return_to_main)
            self.pass_reg.setEchoMode(QLineEdit.EchoMode.Password)
            self.re_pass_reg.setEchoMode(QLineEdit.EchoMode.Password)

        self.register.show()
        self.hide()

    def process_registration(self):
        phone = self.Phone_reg.text()
        password = self.pass_reg.text()
        repass = self.re_pass_reg.text()
        vai_tro = self.vai_tro.currentText()

        if not all([phone, password, repass]):
            self.msg_box.setText("Vui lòng điền đầy đủ thông tin!")
            self.msg_box.exec()
            return
        if password != repass:
            self.msg_box.setText("Mật khẩu không khớp!")
            self.msg_box.exec()
            return

        if vai_tro == "Giáo viên":
            self.register_teacher(phone, password)
        elif vai_tro == "Học sinh":
            self.register_student(phone, password)
        else:
            self.msg_box.setText("Vui lòng chọn vai trò!")
            self.msg_box.exec()
            return

    def register_teacher(self, phone, password):
        try:
            with open("tk_tc_data.json", "r", encoding="utf-8") as f:
                tk_tc_data = json.load(f)
        except FileNotFoundError:
            tk_tc_data = {"Danh_sach_tai_khoan_teacher": []}

        new_id = 1
        if tk_tc_data["Danh_sach_tai_khoan_teacher"]:
            new_id = max(int(tk['id_tai_khoan']) for tk in tk_tc_data["Danh_sach_tai_khoan_teacher"]) + 1

        new_teacher = {
            "id_tai_khoan": str(new_id),
            "ten_tai_khoan": "",
            "MK_tai_khoan": password,
            "so_dien_thoai": str(phone),
            "birthday": "",
            "age": "",
            "gender": "",
        }
        tk_tc_data["Danh_sach_tai_khoan_teacher"].append(new_teacher)

        with open("tk_tc_data.json", "w", encoding="utf-8") as f:
            json.dump(tk_tc_data, f, indent=4, ensure_ascii=False)

        self.msg_box.setText("Đăng ký tài khoản giáo viên thành công!")
        self.msg_box.exec()
        self.return_to_main()

    def register_student(self, phone, password):
        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
        except FileNotFoundError:
            tk_hs_data = {"Danh_sach_hoc_sinh": []}

        # Tạo cấu trúc "Thông tin tài khoản" và "Thành tựu"
        new_student = {
            "None": 0,
            "Số thứ tự": "", # Sẽ được điền sau
            "Họ": "", # Sẽ được điền sau
            "Tên": "", # Sẽ được điền sau
            "Thông tin tài khoản": {
                "id_tai_khoan": self.generate_random_student_id(),
                "grade": None, # Sẽ được điền sau
                "class_name": None, # Sẽ được điền sau
                "ten_tai_khoan": "", # Sẽ được điền sau
                "MK_tai_khoan": password,
                "so_thu_tu": None, # Sẽ được điền sau
                "so_dien_thoai": str(phone),
                "birthday": "", # Sẽ được điền sau
                "age": None # Sẽ được điền sau
            },
            "Thành tựu": {
                "Study hard": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Knowledge Discovery": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Self-learning Spirit": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Remember the Teacher": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Perfect Plan": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Learning from friends": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Spirit of cooperation": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "A real book": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Join the club": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Spirit of progress": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Unlimited skills": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "What is procrastination?": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Burning the language barrier": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Fluent in mother tongue": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "No need for a computer": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Exemplary Citizen": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Here comes the clerk": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Nothing can make it difficult for me": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Geography is balanced": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Practice test master": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Note-taking master": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Smart time management": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Challenge yourself": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Knowledge Scan Machine": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Talented Editor": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Super Focus": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Content Creation": False,
                "Inspiration": False,
                "Tech Genius": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False
                },
                "Explore MasterEdu": False,
                "Knowledge Hunter": False,
                "Super Memory": False,
                "Learn Anytime - Anywhere": False,
                "Excellent student of the year": False,
                "The Flash": {
                    "level_1": False,
                    "level_2": False,
                    "level_3": False,
                    "level_4": False,
                    "level_5": False
                },
                "Night Owl": False,
                "Study - Study more - Study forever": False,
                "Pioneer": False,
                "Companion": False,
                "Potential Contributor": False,
                "Special Day": False,
                "Potential Inventor": False,
                "Technology Believer": False,
                "Great Tester": False,
                "Why so observant?": False,
                "Lucky": False,
                "What did you eat that's so bad?:": False,
                "Comprehensive student": False,
                "Brain Freeze": False,
                "Go away spam": False,
                "The Chosen One": False,
                "You Are The Best": False,
                "Happy New Year": False,
                "It's his fault, his fault, his fault,...": False,
                "Notification enthusiast": False,
                "What's wrong with the keyboard?:": False,
                "That network": False,
                "Gratitude": False,
                "Hey, the mic": False,
                "King/Queen of skipping class": False,
                "Back to overstudying": False,
                "Encyclopedia": False,
                "Decode the math problem": False
            },
            "Điểm trong năm": {
                "Học kỳ 1": {},
                "Học kỳ 2": {}
            },
            "Điểm trung bình cả năm": {
                "Học kỳ 1": {},
                "Học kỳ 2": {}
            }
        }

        tk_hs_data["Danh_sach_hoc_sinh"].append(new_student)

        with open("diem_database.json", "w", encoding="utf-8") as f:
            json.dump(tk_hs_data, f, indent=4, ensure_ascii=False)

        self.msg_box.setText("Đăng ký tài khoản học sinh thành công!")
        self.msg_box.exec()
        self.return_to_main()

    def generate_random_student_id(self):
        import random
        so_thu_tu = random.randint(88001, 88099)
        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
            while so_thu_tu in [int(tk['id_tai_khoan']) for tk in tk_hs_data.get("Danh_sach_hoc_sinh", [])]:
                so_thu_tu = random.randint(88001, 88099)
        except FileNotFoundError:
            pass
        return so_thu_tu

    def return_to_main(self):
        self.register.hide()
        self.show()

    def login_hs(self):
        if not self.student_login:
            self.student_login = uic.loadUi("gui/login-student.ui")
            self.student_login.HocSinhLogin_btn.clicked.connect(self.check_login_hs)
            self.student_login.goback_hs_btn.clicked.connect(self.goback_hs)
            self.student_login.id_hs.setValidator(self.phone_validator)

        self.student_login.show()
        self.hide()

    def check_login_hs(self):
        id_tai_khoan = self.student_login.id_hs.text()
        mat_khau = self.student_login.pass_HS.text()

        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                tk_hs_data = json.load(f)
        except FileNotFoundError:
            self.msg_box.setText("Không tìm thấy file diem_database.json")
            self.msg_box.exec()
            return

        # Duyệt qua danh sách học sinh và kiểm tra thông tin tài khoản
        for hoc_sinh in tk_hs_data.get("Danh_sach_hoc_sinh", []):
            thong_tin_tai_khoan = hoc_sinh.get("Thông tin tài khoản", {})
            if (
                str(thong_tin_tai_khoan.get("id_tai_khoan", "")) == id_tai_khoan
                and str(thong_tin_tai_khoan.get("MK_tai_khoan", "")) == mat_khau
            ):
                self.student_login.close()
                self.open_student_select_menu(hoc_sinh)
                return

        self.msg_box.setText("Sai ID tài khoản hoặc mật khẩu!")
        self.msg_box.exec()

    def open_student_select_menu(self, tai_khoan):
        from menu_select_hs import MenuSelectHS
        self.student_select_menu = MenuSelectHS(self.data, tai_khoan)
        self.student_select_menu.show()
        
    def open_student_main(self, tai_khoan):
        self.student_main = StudentMain(self.data, tai_khoan)
        self.student_main.show()
        self.student_login.hide()


    def load_data(self):
        try:
            with open("diem_database.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {"Danh_sach_hoc_sinh": []}
        except Exception as e:
            print(f"Lỗi khi đọc file diem_database.json: {e}")

        self.sort_students()

    def sort_students(self):
        self.data["Danh_sach_hoc_sinh"].sort(key=lambda student: int(student.get("Số thứ tự", 0)))