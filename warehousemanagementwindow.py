from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from warehousemanagement import WarehouseManagement

class WarehouseManagementWindow(QWidget):
    def __init__(self, navigation_manager, db_config):
        super().__init__()
        self.navigation_manager = navigation_manager
        self.db_config = db_config
        self.warehouse_manager = WarehouseManagement(db_config)

        self.setWindowTitle("Warehouse Management")
        self.setGeometry(100, 100, 800, 600)

        self.setup_ui()
        self.load_warehouse_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel("Warehouse Management")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(header)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search warehouses...")
        self.search_input.textChanged.connect(self.search_warehouses)
        layout.addWidget(self.search_input)

        # Warehouse table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Warehouse ID", "Warehouse Name", "Location"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Buttons
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Warehouse")
        self.add_button.clicked.connect(self.add_warehouse)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Warehouse")
        self.edit_button.clicked.connect(self.edit_warehouse)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Warehouse")
        self.delete_button.clicked.connect(self.delete_warehouse)
        button_layout.addWidget(self.delete_button)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        button_layout.addWidget(self.back_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_warehouse_data(self):
        try:
            warehouses = self.warehouse_manager.get_all_warehouses()
            self.table.setRowCount(0)
            for warehouse in warehouses:
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(str(warehouse['warehouse_id'])))
                self.table.setItem(row_position, 1, QTableWidgetItem(warehouse['warehouse_name']))
                self.table.setItem(row_position, 2, QTableWidgetItem(warehouse['location']))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load warehouses: {e}")

    def search_warehouses(self):
        query = self.search_input.text().strip().lower()
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item and query in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def add_warehouse(self):
        name, ok_name = QInputDialog.getText(self, "Add Warehouse", "Enter warehouse name:")
        location, ok_location = QInputDialog.getText(self, "Add Warehouse", "Enter warehouse location:")
        if ok_name and ok_location and name and location:
            try:
                self.warehouse_manager.add_warehouse(name, location)
                QMessageBox.information(self, "Success", "Warehouse added successfully.")
                self.load_warehouse_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to add warehouse: {e}")

    def edit_warehouse(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a warehouse to edit.")
            return

        row = selected_rows[0].row()
        warehouse_id = int(self.table.item(row, 0).text())

        name, ok_name = QInputDialog.getText(self, "Edit Warehouse", "Enter new warehouse name:",
                                             text=self.table.item(row, 1).text())
        location, ok_location = QInputDialog.getText(self, "Edit Warehouse", "Enter new warehouse location:",
                                                     text=self.table.item(row, 2).text())
        if ok_name and ok_location and name and location:
            try:
                self.warehouse_manager.update_warehouse(warehouse_id, name, location)
                QMessageBox.information(self, "Success", "Warehouse updated successfully.")
                self.load_warehouse_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update warehouse: {e}")

    def delete_warehouse(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "Please select a warehouse to delete.")
            return

        row = selected_rows[0].row()
        warehouse_id = int(self.table.item(row, 0).text())

        confirmation = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this warehouse?",
                                            QMessageBox.Yes | QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            try:
                self.warehouse_manager.delete_warehouse(warehouse_id)
                QMessageBox.information(self, "Success", "Warehouse deleted successfully.")
                self.load_warehouse_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete warehouse: {e}")

    def go_back(self):
        self.navigation_manager.navigate_to("MainWindow")
