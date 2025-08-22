from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QComboBox, QTextEdit
)
from PyQt6.QtCore import Qt
import sys
import openpyxl as op
from openpyxl import load_workbook

class ExcelFilterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фильтр Excel — PyQt6 + openpyxl (Python 3.9)")
        self.resize(800, 420)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self.input_edit = QLineEdit()
        self.input_btn = QPushButton("Выбрать файл…")
        input_row = QHBoxLayout()
        input_row.addWidget(QLabel("Входной .xlsx:"))
        input_row.addWidget(self.input_edit)
        input_row.addWidget(self.input_btn)

        self.column_combo = QComboBox()
        self.value_edit = QLineEdit()
        col_row = QHBoxLayout()
        col_row.addWidget(QLabel("Столбец:"))
        col_row.addWidget(self.column_combo, 1)
        col_row.addWidget(QLabel("Значение:"))
        col_row.addWidget(self.value_edit, 1)

        self.output_edit = QLineEdit()
        self.output_btn = QPushButton("Сохранить как…")
        output_row = QHBoxLayout()
        output_row.addWidget(QLabel("Результат:"))
        output_row.addWidget(self.output_edit)
        output_row.addWidget(self.output_btn)

        self.run_btn = QPushButton("Выполнить фильтрацию")
        self.log = QTextEdit()
        self.log.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addLayout(input_row)
        layout.addLayout(col_row)
        layout.addLayout(output_row)
        layout.addWidget(self.run_btn)
        layout.addWidget(QLabel("Лог:"))
        layout.addWidget(self.log, 1)
        self.setLayout(layout)

    def _connect_signals(self):
        self.input_btn.clicked.connect(self.browse_input)
        self.output_btn.clicked.connect(self.browse_output)
        self.run_btn.clicked.connect(self.run_filter)

    def browse_input(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите Excel-файл", "", "Excel (*.xlsx)")
        if path:
            self.input_edit.setText(path)
            self.populate_columns(Path(path))

    def browse_output(self):
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить результат", "", "Excel (*.xlsx)")
        if path and not path.lower().endswith(".xlsx"):
            path += ".xlsx"
        if path:
            self.output_edit.setText(path)

    def populate_columns(self, path: Path):
        self.column_combo.clear() # очищаем старые пункты

        try:
            # открываем на чтение
            wb = load_workbook(filename=str(path), read_only=True, data_only=True) # data_only = True берёт не формулы, а значения
            # берём первый лист
            ws = wb.active

            # берём список ячеек, убирая пробелы и превращая их в строки. None меняем на ""
            headers = [str(cell.value).strip() if cell.value is not None else "" for cell in ws[1]]
            headers = [h for h in headers if h] # убираем пустые значения

            # если всё пусто
            if not headers:
                self.column_combo.addItems(["- в первой строке нет заголовков -"])
                self.log.append("В первой строке не найдены заголовки!")
                return

            self.column_combo.addItems(headers)

            self.log.append(f"Загружены столбцы: {', '.join(headers)}")

        except FileNotFoundError:
            self.log.append("Файл не найден. Проверь путь.")
        except Exception as e:
            self.log.append("Ошибка при чтении Excel: {e!r}")

    def run_filter(self):
        self.log.append("Нажата кнопка \"Выполнить фильтрацию\" — логику добавим на следующем шаге.")


def main():
    app = QApplication(sys.argv)
    win = ExcelFilterApp()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
