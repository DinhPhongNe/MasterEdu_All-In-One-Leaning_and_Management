from PyQt6.QtWidgets import QMainWindow
from PyQt6 import uic

class ComingSoon(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("gui/coming_soon.ui", self)