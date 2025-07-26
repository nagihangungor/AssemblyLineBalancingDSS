from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QDialog, QGroupBox, QGridLayout, QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from algorithms.rpw import rpw_schedule
from algorithms.rpw_u import rpw_u_schedule
from algorithms.iuff import iuff_schedule
from algorithms.kilbridge_wester import assign_kw
from algorithms.comsoal import comsoal
from algorithms.comsoal_u_type import comsoal_u_type
from algorithms.utils import find_min_cycle_time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import networkx as nx
import math
from fpdf import FPDF
import os

class ResultsScreen(QWidget):
    def __init__(self, selections, inputs, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Çözüm Ekranı")
        self.selections = selections
        self.tasks = inputs['tasks']
        self.precedences = inputs['precedences']
        self.params = inputs['params']

        style_path = os.path.join(os.path.dirname(__file__), '../main/style.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())

        self.layout = QVBoxLayout()
        self.result_title = QLabel(f"Yöntem: {selections['method']}")
        self.graph_button = QPushButton("İstasyon Yük Grafiği")
        self.network_button = QPushButton("Öncelik Ağı")
        self.compare_button = QPushButton("Karşılaştır")
        self.export_txt = QPushButton("TXT Kaydet")
        self.export_pdf = QPushButton("PDF Kaydet")
        self.back_button = QPushButton("Geri Dön")

        self.graph_button.clicked.connect(self.show_bar_chart_dialog)
        self.network_button.clicked.connect(self.show_precedence_network_dialog)
        self.compare_button.clicked.connect(self.show_comparison_dialog)
        self.export_txt.clicked.connect(self.export_results)
        self.export_pdf.clicked.connect(self.export_as_pdf)
        self.back_button.clicked.connect(self.go_back)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.graph_button)
        button_layout.addWidget(self.network_button)
        button_layout.addWidget(self.compare_button)
        button_layout.addWidget(self.export_txt)
        button_layout.addWidget(self.export_pdf)
        button_layout.addWidget(self.back_button)

        self.layout.addWidget(self.result_title)
        self.setLayout(self.layout)

        self.solve_and_display()
        self.layout.addLayout(button_layout)

    def solve_and_display(self):
        layout_type = self.selections.get('layout')
        method = self.selections['method']

        if layout_type == 'U-Tipi Hat':
            self.solve_u_type()
            return

        algorithm_map = {
            'RPW': rpw_schedule,
            'IUFF': iuff_schedule,
            'Kilbridge & Wester': assign_kw,
            'COMSOAL': lambda tasks, precedences, cycle_time:
            comsoal(tasks, precedences, cycle_time, num_iterations=100)[0]
        }

        algorithm_fn = algorithm_map.get(method)
        if not algorithm_fn:
            QMessageBox.warning(self, "Uyarı", "Seçilen algoritma desteklenmiyor.")
            return

        self.solve_generic(algorithm_fn)


    def solve_u_type(self):
        method = self.selections['method']
        u_algorithms = {
            'COMSOAL': lambda tasks, precedences, c: comsoal_u_type(tasks, precedences, c, num_iterations=30),
            'RPW': rpw_u_schedule  # Replace with rpw_u_schedule if applicable
        }

        if method not in u_algorithms:
            QMessageBox.warning(self, "Uyarı", f"'{method}' algoritması U-Tipi yerleşim için desteklenmiyor.")
            return

        algorithm_fn = u_algorithms[method]
        self.solve_generic(algorithm_fn)

    def solve_generic(self, algorithm_fn):
        goal = self.selections['goal']
        total_task_time = sum(self.tasks.values())

        if goal == 'Tip-2':
            station_count = int(self.params.get('station_count'))
            cycle_time, stations = find_min_cycle_time(self.tasks, self.precedences, station_count, algorithm_fn)
            if cycle_time is None:
                QMessageBox.critical(self, "Hata", "Tip-2 çözüm bulunamadı.")
                return
            self.params['cycle_time'] = cycle_time

        elif goal == 'Tip-F':
            cycle_time = self.params.get('cycle_time')
            station_count = int(self.params.get('station_count'))
            stations = algorithm_fn(self.tasks, self.precedences, cycle_time)
            if len(stations) > station_count:
                QMessageBox.critical(self, "Hata",
                                     f"Tip-F: {station_count} istasyon sınırı aşıldı. {len(stations)} istasyon oluştu.")
                return

        elif goal == 'Tip-E':
            C_min = float(self.params['min_cycle_time'])
            C_max = float(self.params['max_cycle_time'])
            C_step = float(self.params['cycle_step'])

            best_efficiency = -1
            best_output = []
            best_cycle = C_min

            cycle_time = C_min
            while cycle_time <= C_max:
                stations = algorithm_fn(self.tasks, self.precedences, cycle_time)
                num_stations = len(stations)
                efficiency = (total_task_time / (num_stations * cycle_time)) * 100
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_output = stations
                    best_cycle = cycle_time
                cycle_time += C_step

            stations = best_output
            cycle_time = best_cycle

        else:
            cycle_time = self.params.get('cycle_time')
            stations = algorithm_fn(self.tasks, self.precedences, cycle_time)

        self.display_results(stations, cycle_time)

    def display_results(self, stations, cycle_time):

        # Eski bileşenleri temizle
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            widget = item.widget() if item else None
            if widget and widget != self.result_title:
                widget.setParent(None)

        total_task_time = sum(self.tasks.values())
        station_loads = [sum(self.tasks[t] for t in station) for station in stations]
        self.station_loads = station_loads
        self.station_assignments = stations
        num_stations = len(stations)
        efficiency = (total_task_time / (num_stations * cycle_time)) * 100
        balance_delay = 100 - efficiency
        avg_load = total_task_time / num_stations
        smoothness_index = math.sqrt(sum((load - avg_load) ** 2 for load in station_loads))

        table = QTableWidget()
        table.setRowCount(len(stations))
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["İstasyon", "Görevler", "Yük (sn)"])
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                border: none;
                gridline-color: #4CA1AF;
            }
            QHeaderView::section {
                background-color: #2C3E50;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        for i, station in enumerate(stations):
            table.setItem(i, 0, QTableWidgetItem(f"İstasyon {i + 1}"))
            table.setItem(i, 1, QTableWidgetItem(", ".join(station)))
            table.setItem(i, 2, QTableWidgetItem(f"{station_loads[i]:.2f}"))
            if i % 2 == 0:
                for col in range(3):
                    table.item(i, col).setBackground(QColor("#f5f5f5"))

        table.resizeColumnsToContents()
        table.resizeRowsToContents()
        table.setWordWrap(True)

        perf_box = QGroupBox("Performans Ölçütleri")
        perf_layout = QGridLayout()
        perf_data = [
            ("Çevrim Süresi", f"{cycle_time:.2f}"),
            ("Toplam Görev Süresi", f"{total_task_time:.2f}"),
            ("İstasyon Sayısı", str(num_stations)),
            ("Hat Verimliliği", f"{efficiency:.2f}%"),
            ("Denge Gecikmesi", f"{balance_delay:.2f}%"),
            ("Düzgünlük İndeksi", f"{smoothness_index:.2f}"),
        ]
        for i, (label, value) in enumerate(perf_data):
            perf_layout.addWidget(QLabel(label + ":"), i, 0)
            perf_layout.addWidget(QLabel(value), i, 1)
        perf_box.setLayout(perf_layout)

        self.layout.addWidget(table)
        self.layout.addWidget(perf_box)

    def show_bar_chart_dialog(self):
        fig, ax = plt.subplots()
        names = [f"İstasyon {i+1}" for i in range(len(self.station_loads))]
        ax.bar(names, self.station_loads)
        ax.set_ylabel("Yük")
        ax.set_title("İstasyon Yük Grafiği")
        fig.tight_layout()
        dlg = QDialog(self)
        dlg.setLayout(QVBoxLayout())
        dlg.layout().addWidget(FigureCanvas(fig))
        dlg.setWindowTitle("Yük Grafiği")
        dlg.exec()

    def show_precedence_network_dialog(self):

        G = nx.DiGraph()
        for task, preds in self.precedences.items():
            for pred in preds:
                G.add_edge(int(pred), int(task))  # int dönüşümü ile sıralama bozulmasın

        pos = nx.shell_layout(G)  # Alternatif: nx.planar_layout(G) veya nx.kamada_kawai_layout(G)
        fig, ax = plt.subplots(figsize=(10, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', edgecolors='black',
                node_size=1800, font_size=10, ax=ax)


        ax.set_title("Öncelik Ağı")
        ax.axis("off")

        dialog = QDialog(self)
        dialog.setWindowTitle("Öncelik Ağı")
        layout = QVBoxLayout()
        layout.addWidget(FigureCanvas(fig))
        dialog.setLayout(layout)
        dialog.resize(700, 500)
        dialog.exec()

    def show_comparison_dialog(self):
        methods = {
            "RPW": rpw_schedule,
            "IUFF": iuff_schedule,
            "Kilbridge & Wester": assign_kw,
            "COMSOAL": comsoal
        }
        comparison_data = []
        total_task_time = sum(self.tasks.values())
        goal = self.selections['goal']

        for name, func in methods.items():
            try:
                if goal == 'Tip-2':
                    station_count = int(self.params.get('station_count'))
                    cycle_time, stations = find_min_cycle_time(self.tasks, self.precedences, station_count, func)
                else:
                    cycle_time = self.params.get('cycle_time')
                    if cycle_time is None:
                        comparison_data.append((name, '-', '-', '-', "Hata: çevrim süresi hesaplanamadı"))
                        continue
                    cycle_time = float(cycle_time)
                    if name == "COMSOAL":
                        stations, _ = func(self.tasks, self.precedences, cycle_time, num_iterations=30)
                    else:
                        stations = func(self.tasks, self.precedences, cycle_time)

                n = len(stations)
                if n == 0 or cycle_time == 0:
                    raise ValueError("Geçersiz istasyon sayısı veya çevrim süresi")

                loads = [sum(self.tasks[t] for t in s) for s in stations]
                eff = (total_task_time / (n * cycle_time)) * 100
                delay = 100 - eff
                avg = total_task_time / n
                si = math.sqrt(sum((l - avg) ** 2 for l in loads))

                comparison_data.append((name, n, eff, delay, si))

            except Exception as e:
                comparison_data.append((name, '-', '-', '-', f"Hata: {str(e)}"))

        dialog = QDialog(self)
        dialog.setWindowTitle("Algoritma Karşılaştırması")
        layout = QVBoxLayout()
        table = QTableWidget()
        table.setRowCount(len(comparison_data))
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Algoritma", "İstasyon Sayısı", "Verimlilik %", "Denge Gecikmesi %", "Düzgünlük İndeksi"])
        for row, (name, n, eff, delay, si) in enumerate(comparison_data):
            table.setItem(row, 0, QTableWidgetItem(str(name)))
            table.setItem(row, 1, QTableWidgetItem(str(n)))
            table.setItem(row, 2, QTableWidgetItem(f"{eff}" if isinstance(eff, str) else f"{eff:.2f}"))
            table.setItem(row, 3, QTableWidgetItem(f"{delay}" if isinstance(delay, str) else f"{delay:.2f}"))
            table.setItem(row, 4, QTableWidgetItem(f"{si}" if isinstance(si, str) else f"{si:.2f}"))

        table.resizeColumnsToContents()
        layout.addWidget(table)
        dialog.setLayout(layout)
        dialog.resize(600, 300)
        dialog.exec()

    def export_results(self):
        path, _ = QFileDialog.getSaveFileName(self, "TXT Kaydet", filter="Text Files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                for i, s in enumerate(self.station_assignments):
                    f.write(f"İstasyon {i+1}: {', '.join(s)}\n")


    def export_as_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", filter="PDF Files (*.pdf)")
        if path:
            try:
                pdf = FPDF()
                pdf.add_page()

                font_path = os.path.join("fonts", "FreeSerif.ttf")
                pdf.add_font("FreeSerif", "", font_path, uni=True)
                pdf.set_font("FreeSerif", size=10)

                for i, s in enumerate(self.station_assignments):
                    görevler_str = ", ".join(s)
                    pdf.multi_cell(0, 10, f"İstasyon {i + 1}: {görevler_str}")

                pdf.output(path)
                QMessageBox.information(self, "Kaydedildi", "PDF başarıyla oluşturuldu.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturulurken hata oluştu:\n{str(e)}")

    def go_back(self):
        if self.stacked_widget:
            self.stacked_widget.setCurrentIndex(1)
