import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox,
    QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt

class MainMenu(QMainWindow):
    def __init__(self, go_next):
        super().__init__()
        self.go_next = go_next

        self.setWindowTitle("Hat Dengeleme DSS")
        self.setFixedSize(800, 500)

        # Stil dosyasını yükle
        style_path = os.path.join(os.path.dirname(__file__), '../main/style.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sol Panel
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(20)

        title_label = QLabel("Montaj Hattı Dengeleme Sistemi")
        title_label.setProperty("role", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        left_layout.addWidget(title_label)

        hedef_label = QLabel("Hedef Seçimi:")
        hedef_label.setStyleSheet("font-weight: bold;")
        self.hedef_combo = QComboBox()
        self.hedef_combo.addItems(["Tip-1", "Tip-2", "Tip-E", "Tip-F"])
        left_layout.addWidget(hedef_label)
        left_layout.addWidget(self.hedef_combo)

        algoritma_label = QLabel("Algoritma Seçimi:")
        algoritma_label.setStyleSheet("font-weight: bold;")
        self.algoritma_combo = QComboBox()
        self.algoritma_combo.addItems(["RPW", "IUFF", "Kilbridge & Wester", "COMSOAL"])
        left_layout.addWidget(algoritma_label)
        left_layout.addWidget(self.algoritma_combo)

        yerlesim_label = QLabel("Yerleşim Tipi:")
        yerlesim_label.setStyleSheet("font-weight: bold;")
        self.yerlisim_combo = QComboBox()
        self.yerlisim_combo.addItems(["Düz Hat", "U-Tipi Hat"])
        left_layout.addWidget(yerlesim_label)
        left_layout.addWidget(self.yerlisim_combo)

        self.devam_button = QPushButton("Devam Et")
        self.devam_button.setObjectName("devam")
        self.devam_button.clicked.connect(self.devam_et)
        left_layout.addStretch()
        left_layout.addWidget(self.devam_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Sağ Panel
        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")  # 🔥 önemli

        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        right_layout.setSpacing(15)
        right_layout.addStretch()

        welcome_label = QLabel("Hoş Geldiniz!")
        welcome_label.setStyleSheet("font-size: 28px; font-weight: bold; color: white;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(welcome_label)

        info_label = QLabel("Montaj hattı dengeleme sistemi parametrelerini seçiniz")
        info_label.setStyleSheet("font-size: 15px; color: white;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setWordWrap(True)
        right_layout.addWidget(info_label)

        right_layout.addStretch()



        left_panel.setStyleSheet("QFrame { background-color: white; border-radius: 20px; }")

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)

    def devam_et(self):
        selections = {
            'goal': self.hedef_combo.currentText(),
            'method': self.algoritma_combo.currentText(),
            'layout': self.yerlisim_combo.currentText()
        }

        # ⛔ U tipi için desteklenmeyen algoritmalar kontrolü
        unsupported_for_u = ['IUFF', 'Kilbridge & Wester']
        if selections['layout'] == 'U-Tipi Hat' and selections['method'] in unsupported_for_u:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "Uyarı",
                f"'{selections['method']}' algoritması U-Tipi hat yerleşimini desteklememektedir.\n"
                f"Lütfen RPW veya COMSOAL algoritmalarını seçiniz."
            )
            return  # ekran geçişi yapılmaz

        if callable(self.go_next):
            self.go_next(selections)


if __name__ == "__main__":
    def dummy_next(selections):
        print("Seçilenler:", selections)

    app = QApplication(sys.argv)
    window = MainMenu(dummy_next)
    window.show()
    sys.exit(app.exec())