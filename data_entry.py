from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog, QComboBox
)
from PyQt6.QtCore import Qt
import os
import pandas as pd

class DataEntryScreen(QWidget):
    def __init__(self, selections, go_to_results, stacked_widget):
        super().__init__()
        self.selections = selections
        self.go_to_results = go_to_results
        self.stacked_widget = stacked_widget

        style_path = os.path.join(os.path.dirname(__file__), '../main/style.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

        self.layout = QVBoxLayout(self)

        self.worker_label = QLabel("Görev Sayısı:")
        self.worker_input = QLineEdit()
        self.worker_input.setPlaceholderText("Örnek: 5")
        self.worker_input.textChanged.connect(self.validate_worker_input)  # canlı kontrol

        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: red; font-size: 12px;")

        self.task_table = QTableWidget()
        self.task_table.setColumnCount(3)
        self.task_table.setHorizontalHeaderLabels(["ID", "Süre", "Öncüller"])

        # Seçimleri yeniden göstermek için comboBox'lar ekleniyor (gizli de olabilir)
        self.goal_combo = QComboBox()
        self.goal_combo.addItems(["Tip-1", "Tip-2", "Tip-E", "Tip-F"])
        self.goal_combo.setCurrentText(self.selections['goal'])
        self.goal_combo.setVisible(False)

        self.method_combo = QComboBox()
        self.method_combo.addItems(["RPW", "IUFF", "Kilbridge & Wester", "COMSOAL"])
        self.method_combo.setCurrentText(self.selections['method'])
        self.method_combo.setVisible(False)

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Düz Hat", "U-Tipi Hat"])
        self.layout_combo.setCurrentText(self.selections['layout'])
        self.layout_combo.setVisible(False)
        self.param_inputs = {}
        if selections['goal'] in ['Tip-1', 'Tip-F']:
            self.param_inputs['cycle_time'] = QLineEdit()
            self.param_inputs['cycle_time'].setPlaceholderText("Çevrim Süresi (sn)")
            self.layout.addWidget(QLabel("Çevrim Süresi:"))
            self.layout.addWidget(self.param_inputs['cycle_time'])
        if selections['goal'] in ['Tip-2', 'Tip-F']:
            self.param_inputs['station_count'] = QLineEdit()
            self.param_inputs['station_count'].setPlaceholderText("İstasyon Sayısı")
            self.layout.addWidget(QLabel("İstasyon Sayısı:"))
            self.layout.addWidget(self.param_inputs['station_count'])
        if selections['goal'] == 'Tip-E':
            self.param_inputs['min_cycle_time'] = QLineEdit()
            self.param_inputs['min_cycle_time'].setPlaceholderText("Minimum Çevrim Süresi")
            self.param_inputs['max_cycle_time'] = QLineEdit()
            self.param_inputs['max_cycle_time'].setPlaceholderText("Maksimum Çevrim Süresi")
            self.param_inputs['cycle_step'] = QLineEdit()
            self.param_inputs['cycle_step'].setPlaceholderText("Artış Miktarı")
            self.layout.addWidget(QLabel("Tip-E Parametreleri:"))
            self.layout.addWidget(self.param_inputs['min_cycle_time'])
            self.layout.addWidget(self.param_inputs['max_cycle_time'])
            self.layout.addWidget(self.param_inputs['cycle_step'])

        self.solve_button = QPushButton("Çöz ve Göster")
        self.solve_button.setObjectName("solve_button")
        self.solve_button.clicked.connect(self.on_solve)

        self.import_button = QPushButton("Excel'den Yükle")
        self.import_button.setObjectName("import_button")
        self.import_button.clicked.connect(self.load_from_excel)


        self.back_button = QPushButton("Ana Menüye Dön")
        self.back_button.setObjectName("back_button")
        self.back_button.clicked.connect(self.go_back_to_main)


        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.solve_button)
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.import_button)


        self.layout.addWidget(self.worker_label)
        self.layout.addWidget(self.worker_input)
        self.layout.addWidget(self.warning_label)  # kırmızı uyarı yazısı
        self.layout.addWidget(self.task_table)
        self.layout.addLayout(button_layout)

    def validate_worker_input(self):
        text = self.worker_input.text()
        if text.isdigit():
            if int(text) > 50:
                self.warning_label.setText("⚠️ Görev sayısı 50'den büyük olamaz.")
            else:
                self.warning_label.setText("")
        else:
            if text:
                self.warning_label.setText("⚠️ Lütfen sadece sayı girin.")
            else:
                self.warning_label.setText("")

        if text.isdigit() and int(text) <= 50:
            self.generate_task_table()
        else:
            self.task_table.setRowCount(0)

    def generate_task_table(self):
        try:
            task_count = int(self.worker_input.text())
            if task_count > 50:
                return  # zaten uyarı verildi, çizelge oluşturma
            self.task_table.setRowCount(task_count)
            for i in range(task_count):
                id_item = QTableWidgetItem(str(i + 1))
                id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.task_table.setItem(i, 0, id_item)
                self.task_table.setItem(i, 1, QTableWidgetItem(""))
                self.task_table.setItem(i, 2, QTableWidgetItem(""))
        except ValueError:
            self.task_table.setRowCount(0)

    def on_solve(self):
        try:
            row_count = self.task_table.rowCount()
            tasks = {}
            precedences = {}

            for i in range(row_count):
                task_id = str(i + 1)
                duration_item = self.task_table.item(i, 1)
                preds_item = self.task_table.item(i, 2)

                if not duration_item or not duration_item.text().strip():
                    raise ValueError(f"Görev {task_id} için süre girilmemiş.")

                try:
                    duration = float(duration_item.text())
                    if duration <= 0:
                        raise ValueError(f"Görev {task_id} süresi sıfırdan büyük olmalıdır.")
                except ValueError:
                    raise ValueError(f"Görev {task_id} için geçerli bir sayı girilmelidir.")

                tasks[task_id] = duration

                if preds_item and preds_item.text().strip():
                    precedences[task_id] = [p.strip() for p in preds_item.text().split(",") if p.strip()]

            # Parametre kontrolleri
            for key, field in self.param_inputs.items():
                val = field.text().strip()
                if val:
                    if key == "station_count":
                        if not val.isdigit():
                            raise ValueError("İstasyon sayısı sadece sayı olmalıdır.")
                        if int(val) > 99:
                            raise ValueError("İstasyon sayısı 99'dan büyük olamaz.")
                    else:
                        float(val)  # geçerli sayı mı diye kontrol

            params = {k: float(v.text()) for k, v in self.param_inputs.items() if v.text()}
            # Çevrim süresi aşıldı mı kontrol et
            if "cycle_time" in params:
                cycle_time = params["cycle_time"]
                for task_id, duration in tasks.items():
                    if duration > cycle_time:
                        raise ValueError(f"Görev {task_id} süresi çevrim süresini ({cycle_time}) aşıyor.")

            inputs = {
                'tasks': tasks,
                'precedences': precedences,
                'params': params
            }

            self.go_to_results(self.selections, inputs)

        except Exception as e:
            QMessageBox.critical(self, "Girdi Hatası", str(e))

    def load_from_excel(self):
        path, _ = QFileDialog.getOpenFileName(self, "Excel Dosyası Seç", filter="Excel Files (*.xlsx)")
        if not path:
            return

        try:
            df = pd.read_excel(path)
            required_cols = ['ID', 'Süre', 'Öncüller']
            if not all(col in df.columns for col in required_cols):
                raise ValueError("Excel dosyasında 'ID', 'Süre' ve 'Öncüller' sütunları olmalıdır.")

            row_count = len(df)
            if row_count > 50:
                QMessageBox.warning(self, "Sınır Aşıldı", "En fazla 50 görev yüklenebilir.")
                return

            # Süreleri sayıya çevir (virgül varsa noktaya çevir)
            def convert_duration(val):
                try:
                    return float(str(val).replace(",", "."))
                except:
                    raise ValueError(f"Süre değeri geçersiz: {val}")

            df["Süre"] = df["Süre"].apply(convert_duration)

            if df["Süre"].isnull().any():
                raise ValueError("'Süre' sütununda boş hücreler bulunamaz.")

            self.worker_input.setText(str(row_count))
            self.task_table.setRowCount(row_count)

            for i in range(row_count):
                id_val = str(df.loc[i, 'ID'])
                sure_val = str(df.loc[i, 'Süre'])
                oncul_val = str(df.loc[i, 'Öncüller']) if not pd.isna(df.loc[i, 'Öncüller']) else ""
                oncul_val = ",".join(str(int(float(x))) for x in oncul_val.split(",") if x.strip())

                id_item = QTableWidgetItem(id_val)
                id_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

                self.task_table.setItem(i, 0, id_item)
                self.task_table.setItem(i, 1, QTableWidgetItem(sure_val))
                self.task_table.setItem(i, 2, QTableWidgetItem(oncul_val))

            self.warning_label.setText("")

        except Exception as e:
            QMessageBox.critical(self, "Yükleme Hatası", f"Excel'den veri yüklenirken hata oluştu:\n{str(e)}")

    def go_back_to_main(self):
        if hasattr(self, 'stacked_widget'):
            self.stacked_widget.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Hata", "Ana menüye dönülemedi.")