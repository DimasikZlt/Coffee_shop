import sqlite3
import sys

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, \
    QMessageBox, QDialog
from main_ui import Ui_Form
from addEditCoffeeForm_ui import Ui_Dialog


class CoffeeDataInput(QDialog, Ui_Dialog):
    def __init__(self, parent, is_new_record: bool = True):
        super().__init__(parent)
        self.setModal(True)
        self.parent_window = parent
        self.db = parent.db
        self.is_new = is_new_record
        self.cb_items = None
        # uic.loadUi('addEditCoffeeForm.ui', self)
        self.setupUi(self)
        self.accepted.connect(self.save_coffee_item)

    def get_items_for_combobox(self):
        request_beans = """
            SELECT id, milling
            FROM beans_type                                
        """
        beans_types = {
            bean_type: bean_id
            for bean_id, bean_type in
            self.db.cursor().execute(request_beans).fetchall()
        }
        request_sorts = """
            SELECT id, name
            FROM sort                          
        """
        coffee_sorts = {
            sort_name: sort_id
            for sort_id, sort_name in
            self.db.cursor().execute(request_sorts).fetchall()
        }
        request_roastings = """
            SELECT id, name
            FROM roasting                          
        """
        coffee_roastings = {
            roasting_name: roasting_id
            for roasting_id, roasting_name in
            self.db.cursor().execute(request_roastings).fetchall()
        }
        return {
            'coffee_sort': coffee_sorts,
            'beans_type': beans_types,
            'roasting': coffee_roastings,
        }

    def fill_cb_value_from_db(self):
        self.cb_items = self.get_items_for_combobox()
        self.cb_sort.addItems(sort for sort in self.cb_items['coffee_sort'].keys())
        self.cb_mill.addItems(mill for mill in self.cb_items['beans_type'].keys())
        self.cb_roast.addItems(roast for roast in self.cb_items['roasting'].keys())

    def save_coffee_item(self):
        sort_id = self.cb_items['coffee_sort'][self.cb_sort.currentText()]
        roasting_id = self.cb_items['roasting'][self.cb_roast.currentText()]
        beans_type_id = self.cb_items['beans_type'][self.cb_mill.currentText()]
        price = float(self.dsb_price.value())
        volume = float(self.dsb_volume.value())
        items = (sort_id, roasting_id, beans_type_id, price, volume)
        if self.is_new:
            self.add_new_coffee_item(items)
            return
        self.update_coffee_item(items)

    def add_new_coffee_item(self, items):
        request = """
                INSERT INTO coffee_shop(sort_id, roasting_id, beans_type_id, price, volume)
                VALUES(?, ?, ?, ?, ?)
            """
        self.db.cursor().execute(request, items)
        self.db.commit()
        self.parent_window.show_table()

    def update_coffee_item(self, items):
        row = self.parent_window.tableWidget.selectedItems()[0].row()
        coffee_id = int(self.parent_window.tableWidget.item(row, 0).text())
        request = """
                UPDATE coffee_shop
                SET sort_id = ?,
                    roasting_id = ?,
                    beans_type_id = ?,
                    price = ?,
                    volume = ?
                WHERE id = ?
            """
        self.db.cursor().execute(request, (*items, coffee_id))
        self.db.commit()
        self.parent_window.show_table()


class MainWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        # uic.loadUi('main.ui', self)
        self.setupUi(self)
        self.setMinimumSize(QtCore.QSize(810, 600))
        self.db = sqlite3.connect('data/coffee.sqlite')
        self.show_table()
        self.btn_add.clicked.connect(self.add_new_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.coffee_data_input = None

    def show_table(self):
        self.tableWidget.setColumnCount(7)
        records = self.get_records()
        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setHorizontalHeaderLabels(
            ('ID', 'Сорт', 'Обжарка', 'Помол', 'Описание вкуса', 'Цена', 'Объем')
        )
        self.tableWidget.setColumnHidden(0, True)
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QtWidgets.QHeaderView.ResizeToContents)
        for row, record in enumerate(records):
            for col, item in enumerate(record):
                cell = QTableWidgetItem(str(item))
                cell.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, col, cell)

    def get_records(self):
        request = """
                SELECT coffee_shop.id, sort.name, roasting.name, beans_type.milling, 
                sort.description, coffee_shop.price, coffee_shop.volume
                FROM coffee_shop
                INNER JOIN sort ON coffee_shop.sort_id = sort.id
                INNER JOIN roasting ON coffee_shop.roasting_id = roasting.id
                INNER JOIN beans_type ON coffee_shop.beans_type_id = beans_type.id
            """
        return self.db.cursor().execute(request).fetchall()

    def add_new_record(self):
        self.coffee_data_input = CoffeeDataInput(self)
        self.coffee_data_input.fill_cb_value_from_db()
        self.coffee_data_input.show()

    def edit_record(self):
        self.coffee_data_input = CoffeeDataInput(self, False)
        self.coffee_data_input.fill_cb_value_from_db()
        items = self.tableWidget.selectedItems()
        if items:
            row = self.tableWidget.selectedItems()[0].row()
            self.coffee_data_input.cb_sort.setCurrentText(self.tableWidget.item(row, 1).text())
            self.coffee_data_input.cb_roast.setCurrentText(self.tableWidget.item(row, 2).text())
            self.coffee_data_input.cb_mill.setCurrentText(self.tableWidget.item(row, 3).text())
            self.coffee_data_input.dsb_price.setValue(float(self.tableWidget.item(row, 5).text()))
            self.coffee_data_input.dsb_volume.setValue(float(self.tableWidget.item(row, 6).text()))
            self.coffee_data_input.show()

    def delete_record(self):
        items = self.tableWidget.selectedItems()
        if items:
            row = self.tableWidget.selectedItems()[0].row()
            coffee_id = int(self.tableWidget.item(row, 0).text())
            is_ok = QMessageBox.question(
                self, 'Подтверждение удаления', f"Действительно удалить запись в строке {row + 1}",
                QMessageBox.Yes, QMessageBox.No)
            if is_ok == QMessageBox.Yes:
                request = """
                        DELETE FROM coffee_shop
                        WHERE coffee_shop.id = ?
                    """
                self.db.cursor().execute(request, (coffee_id,))
                self.db.commit()
                self.tableWidget.removeRow(row)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
