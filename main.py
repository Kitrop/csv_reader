import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QMainWindow, \
    QTableWidget, QTableWidgetItem
import csv


class HashTable:
    def __init__(self, size):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        hash_value = sum(ord(ch) for ch in key) % self.size
        return hash_value

    def put(self, key, value):
        hash_value = self._hash(key)
        for entry in self.table[hash_value]:
            if entry[0] == key:
                entry[1] = value  # replace the old value
                return
        self.table[hash_value].append([key, value])

    def get(self, key):
        hash_value = self._hash(key)
        for entry in self.table[hash_value]:
            if entry[0] == key:
                return entry[1]
        return "Не найдено"

    def delete(self, key):
        hash_value = self._hash(key)
        for i, entry in enumerate(self.table[hash_value]):
            if entry[0] == key:
                del self.table[hash_value][i]
                return
        raise KeyError(f"Key {key} not found")

    def items(self):
        result = []
        for bucket in self.table:
            result.extend(bucket)
        return result


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('2С: бухгалтерия')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.sales_label = QLabel()
        self.sales_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.sales_label)

        self.revenue_label = QLabel()
        self.revenue_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.revenue_label)

        self.total_revenue_label = QLabel()
        self.total_revenue_label.setStyleSheet("font-size: 18pt;")
        layout.addWidget(self.total_revenue_label)

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        layout.addWidget(self.table_widget)

        self.revenue_percent_table = QTableWidget()
        self.revenue_percent_table.setColumnCount(2)
        self.revenue_percent_table.setHorizontalHeaderLabels(["Товар", "Процент от общей выручки"])
        layout.addWidget(self.revenue_percent_table)

        button = QPushButton('Загрузить')
        button.clicked.connect(self.load_data)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def read_data_from_file(self, filename):
        """Чтение данных из файла и возврат списка строк"""

        with open(filename, 'r', encoding="utf-8") as file:
            lines = file.readlines()
        return lines

    def update_sales_data(self, lines):
        """Обновление словарей с данными о продажах"""
        sales_by_product = HashTable(100)  # Использование хэш-таблицы
        total_revenue = 0
        revenue_by_product = {}
        units_sold_by_product = {}

        for line in lines[1:]:
            data = line.split(',')
            product = data[2].strip()
            sales = int(data[4])
            revenue = int(data[5])
            units_sold = int(data[4])
            total_revenue += revenue

            sales_by_product.put(product, sales)

            if product in revenue_by_product:
                revenue_by_product[product] += revenue
                units_sold_by_product[product] += units_sold
            else:
                revenue_by_product[product] = revenue
                units_sold_by_product[product] = units_sold

        return sales_by_product, total_revenue, revenue_by_product, units_sold_by_product

    def calculate_max_values(self, sales_by_product, revenue_by_product, units_sold_by_product, total_revenue):
        """Вычисление товаров с наибольшими продажами и выручкой"""
        print(sales_by_product.items())
        max_sales_product = max(sales_by_product.items(), key=lambda x: x[1])[0]
        max_revenue_product = max(revenue_by_product, key=revenue_by_product.get)

        for product, units_sold in units_sold_by_product.items():
            revenue_percent = round((revenue_by_product[product] / total_revenue) * 100, 2)
            self.revenue_percent_table.insertRow(self.revenue_percent_table.rowCount())
            self.revenue_percent_table.setItem(self.revenue_percent_table.rowCount() - 1, 0, QTableWidgetItem(product))
            self.revenue_percent_table.setItem(self.revenue_percent_table.rowCount() - 1, 1,
                                               QTableWidgetItem(str(revenue_percent) + "%"))

        max_units_sold_product = max(units_sold_by_product.items(), key=lambda x: x[1])[0]

        return max_sales_product, max_revenue_product, max_units_sold_product

    def update_labels(self, max_sales_product, max_revenue_product, max_units_sold_product, total_revenue):
        """Обновление текста в ui"""
        self.sales_label.setText(f"Товар с максимальными продажами: {max_sales_product}")
        self.revenue_label.setText(f"Товар с максимальными доходами: {max_revenue_product}")
        self.total_revenue_label.setText(f"Общая выручка: {total_revenue} ₽")

    def load_data(self):
        filename = 'data.csv'
        with open(filename, 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)
            self.display_data(data)

        lines = self.read_data_from_file("data.csv")
        sales_by_product, total_revenue, revenue_by_product, units_sold = self.update_sales_data(lines)
        max_sales_product, max_revenue_product, max_units_sold_product = self.calculate_max_values(sales_by_product,
                                                                                                   revenue_by_product,
                                                                                                   units_sold,
                                                                                                   total_revenue)
        self.update_labels(max_sales_product, max_revenue_product, max_units_sold_product, total_revenue)

    def display_data(self, data):
        """Отображение данных в таблице"""
        self.text_edit.clear()
        self.table_widget.setRowCount(0)
        for row_number, row_data in enumerate(data):
            self.table_widget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                self.table_widget.setItem(row_number, column_number, item)


def bubble_sort_csv(filename):
    """Сортировка пузырьком по столбцу общая стоимость"""
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        data = [row for row in reader]

    for i in range(len(data)):
        for j in range(len(data) - 1):
            if int(data[j][5]) > int(data[j + 1][5]):
                data[j], data[j + 1] = data[j + 1], data[j]

    # Вывод отсортированных данных в консоль
    print(header)
    for row in data:
        print(row)


def selection_sort_csv(filename):
    """Сортировка вставкой"""
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        data = [row for row in reader]

    for i in range(len(data)):
        min_index = i
        for j in range(i + 1, len(data)):
            if int(data[j][2]) < int(data[min_index][2]):
                min_index = j

        data[i], data[min_index] = data[min_index], data[i]

    # Вывод отсортированных данных в консоль
    print(header)
    for row in data:
        print(row)


selection_sort_csv('data.csv')
bubble_sort_csv('data.csv')

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())
