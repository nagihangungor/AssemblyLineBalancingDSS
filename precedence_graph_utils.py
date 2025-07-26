
import matplotlib.pyplot as plt
import networkx as nx
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


def hierarchy_pos(G, root=None, width=1.0, horiz_gap=0.4, horiz_loc=0, ycenter=0.5):
    def _hierarchy_pos(G, root, width=1.0, horiz_gap=0.4,
                       horiz_loc=0, ycenter=0.5, pos=None, parent=None):
        if pos is None:
            pos = {root: (horiz_loc, ycenter)}
        else:
            pos[root] = (horiz_loc, ycenter)
        children = list(G.successors(root))
        if parent:
            children = [c for c in children if c != parent]
        if len(children) != 0:
            dy = width / len(children)
            nexty = ycenter - width / 2 - dy / 2
            for child in children:
                nexty += dy
                pos = _hierarchy_pos(G, child, width=dy, horiz_gap=horiz_gap,
                                     horiz_loc=horiz_loc + horiz_gap, ycenter=nexty, pos=pos, parent=root)
        return pos

    if root is None:
        roots = [n for n, d in G.in_degree() if d == 0]
        if not roots:
            raise ValueError("Grafikte kök (in_degree=0) yok, muhtemelen döngü var.")
        root = roots[0]
    pos = _hierarchy_pos(G, root, width, horiz_gap, horiz_loc, ycenter)

    last_tasks = [n for n in G.nodes if G.out_degree(n) == 0]
    if last_tasks:
        max_x = max(x for x, y in pos.values())
        for n in last_tasks:
            pos[n] = (max_x, ycenter)

    return pos


def show_precedence_network_dialog(self):
    try:
        G = nx.DiGraph()
        for task, preds in self.precedences.items():
            for pred in preds:
                G.add_edge(int(pred), int(task))

        pos = hierarchy_pos(G, horiz_gap=1.5)
        print("📍 Pozisyonlar:", pos)

        fig, ax = plt.subplots(figsize=(14, 6))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', edgecolors='black',
                node_size=1800, font_size=10, ax=ax, arrows=True)

        edge_labels = {}
        for u, v in G.edges():
            try:
                edge_labels[(u, v)] = str(int(self.tasks[str(v)]))
            except KeyError:
                edge_labels[(u, v)] = "?"

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9, ax=ax)
        ax.set_title("Öncelik Ağı (Soldan Sağa)", fontsize=12)
        ax.axis("off")

        dialog = QDialog(self)
        dialog.setWindowTitle("Öncelik Ağı")
        layout = QVBoxLayout()
        layout.addWidget(FigureCanvas(fig))
        dialog.setLayout(layout)
        dialog.resize(900, 600)
        dialog.exec()

    except Exception as e:
        print("❌ Öncelik grafiği çizim hatası:", str(e))
