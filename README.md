# AssemblyLineBalancingDSS
Desicion Support System for Assembly Line Balancing

# Assembly Line Balancing Decision Support System

This repository contains the implementation and report of my bachelor thesis on assembly line balancing problems. The system is developed in Python and supports multiple heuristic algorithms (COMSOAL, RPW, Kilbridge & Wester, IUFF) for both straight-line and U-shaped layouts (only working for rpw and comsoal).

## 🔧 Features

- User-friendly interface built with PyQt6
- Multiple algorithms with modular structure
- Tip-1, Tip-2, Tip-E, Tip-F solutions supported
- Precedence diagram visualization
- Export with Pdf and notebook
- Work balance diagram

## 📁 Folder Structure

📁 assembly-line-dss/
├── algorithm/                 # All implemented algorithms
│   ├── comsoal.py
│   ├── rpw.py
│   ├── kilbridge.py
│   ├── rpw_u.py
│   ├── comsoal_u_type.py
│   ├──utils.py
│   ├──_init_.py
│   └── iuff.py
│
├── screen/                   # PyQt6 screen interfaces
│   ├── main_menu.py
│   ├── data_entry_screen.py
│   ├── base_screen.py
│   └── results_screen.py
│
├── data/                     # Sample input data (CSV, Excel)
│   ├── sample_input.xlsx
│   └── task_example.csv
│
├── utils/                    # Utility functions (e.g., cycle time calculator)
│   └── presedence_graph_utils.py
│
├── README.md                 # Project overview and usage
└── main.py                   # Application entry point

## 📌 Technologies

- Python
- PyQt6
- NetworkX & Matplotlib
- Pandas, NumPy



Nagihan Güngör – Eskişehir Technical University  
Bachelor of Science in Industrial Engineering (2025 expected)
