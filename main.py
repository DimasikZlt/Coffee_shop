import sqlite3
import sys

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QRadioButton, QMainWindow, QWidget, QTableWidgetItem


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.setMinimumSize(QtCore.QSize(810, 600))
        self.db = sqlite3.connect('coffee.sqlite')
        self.show_table()

    def show_table(self):
        self.tableWidget.setColumnCount(6)
        records = self.get_records()
        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setHorizontalHeaderLabels(
            ('Сорт', 'Обжарка', 'Помол', 'Описание вкуса', 'Цена', 'Объем')
        )
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        # header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        for row, record in enumerate(records):
            for col, item in enumerate(record):
                cell = QTableWidgetItem(str(item))
                cell.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, col, cell)

    def get_records(self):
        request = """
                SELECT sort.name, roasting.name, beans_type.milling, sort.description,
                coffee_shop.price, coffee_shop.volume
                FROM coffee_shop
                INNER JOIN sort ON coffee_shop.sort_id = sort.id
                INNER JOIN roasting ON coffee_shop.roasting_id = roasting.id
                INNER JOIN beans_type ON coffee_shop.beans_type_id = beans_type.id
            """
        return self.db.cursor().execute(request).fetchall()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
