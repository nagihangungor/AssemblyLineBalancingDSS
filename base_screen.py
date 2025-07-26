from PyQt6.QtWidgets import QWidget, QHBoxLayout, QFrame, QVBoxLayout
from PyQt6.QtCore import Qt

class BaseScreen(QWidget):
    def __init__(self, show_right_panel=True):
        super().__init__()

        self.setStyleSheet("background-color: #f0f2f5;")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Sol panel
        self.left_panel = QFrame()
        self.left_panel.setStyleSheet("background-color: white; border-radius: 20px;")
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(20, 20, 20, 20)
        self.left_layout.setSpacing(20)
        self.main_layout.addWidget(self.left_panel, 1)

        # Sağ panel (isteğe bağlı)
        if show_right_panel:
            self.right_panel = QFrame()
            self.right_panel.setStyleSheet("""
                background-color: #4c84ff;
                border-top-right-radius: 20px;
                border-bottom-right-radius: 20px;
            """)
            self.right_layout = QVBoxLayout(self.right_panel)
            self.right_layout.setContentsMargins(40, 40, 40, 40)
            self.right_layout.setSpacing(15)
            self.main_layout.addWidget(self.right_panel, 1)
