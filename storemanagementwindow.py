import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from storemanagement import StoreManagement


class StoreManagementWindow(QWidget):
    """
    This class represents the window for managing stores, including searching, adding,
    editing, and deleting stores within the inventory management system.
    """

    def __init__(self, db_config, navigation_manager):
        """
        Initialize the StoreManagementWindow.

        :param db_config: Dictionary containing database connection configuration.
        :param navigation_manager: Instance of NavigationManager for navigating between windows.
        """
        super().__init__()
        self.db_config = db_config
        self.navigation_manager = navigation_manager
        self.store_manager = StoreManagement(db_config)

        self.setWindowTitle("Store Management")
        self.setGeometry(100, 100, 800, 600)

        # Main Layout
        self.layout = QVBoxLayout()

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by Store Name")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_stores)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        self.layout.addLayout(search_layout)

        # Store Table
        self.store_table = QTableWidget()
        self.store_table.setColumnCount(4)
        self.store_table.setHorizontalHeaderLabels(["Store ID", "Store Name", "Address", "Actions"])
        self.store_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.store_table)

        # Buttons
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Store")
        self.add_button.clicked.connect(self.add_store)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.navigate_back)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.back_button)
        self.layout.addLayout(button_layout)

        self.setLayout(self.layout)
        self.load_stores()

    def load_stores(self):
        """
        Load all stores into the table.
        """
        try:
            stores = self.store_manager.get_all_stores()
            self.store_table.setRowCount(0)  # Clear existing rows

            for store in stores:
                row_position = self.store_table.rowCount()
                self.store_table.insertRow(row_position)

                self.store_table.setItem(row_position, 0, QTableWidgetItem(str(store["store_id"])))
                self.store_table.setItem(row_position, 1, QTableWidgetItem(store["store_name"]))
                self.store_table.setItem(row_position, 2, QTableWidgetItem(store["address"]))

                # Add Edit and Delete buttons
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, s=store: self.edit_store(s))
                self.store_table.setCellWidget(row_position, 3, edit_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, s=store["store_id"]: self.delete_store(s))
                self.store_table.setCellWidget(row_position, 4, delete_button)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading stores: {e}")

    def search_stores(self):
        """
        Search for stores based on the input text and update the table.
        """
        search_text = self.search_input.text().strip()
        try:
            stores = self.store_manager.search_stores_by_name(search_text)
            self.store_table.setRowCount(0)  # Clear existing rows

            for store in stores:
                row_position = self.store_table.rowCount()
                self.store_table.insertRow(row_position)

                self.store_table.setItem(row_position, 0, QTableWidgetItem(str(store["store_id"])))
                self.store_table.setItem(row_position, 1, QTableWidgetItem(store["store_name"]))
                self.store_table.setItem(row_position, 2, QTableWidgetItem(store["address"]))

                # Add Edit and Delete buttons
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, s=store: self.edit_store(s))
                self.store_table.setCellWidget(row_position, 3, edit_button)

                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, s=store["store_id"]: self.delete_store(s))
                self.store_table.setCellWidget(row_position, 4, delete_button)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error searching stores: {e}")

    def add_store(self):
        """
        Open a dialog to add a new store and refresh the table.
        """
        name, address = self.get_store_input("Add Store")
        if name and address:
            try:
                self.store_manager.add_store(name, address)
                QMessageBox.information(self, "Success", "Store added successfully.")
                self.load_stores()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error adding store: {e}")

    def edit_store(self, store):
        """
        Open a dialog to edit an existing store and refresh the table.
        """
        name, address = self.get_store_input("Edit Store", store["store_name"], store["address"])
        if name and address:
            try:
                self.store_manager.update_store(store["store_id"], name, address)
                QMessageBox.information(self, "Success", "Store updated successfully.")
                self.load_stores()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error updating store: {e}")

    def delete_store(self, store_id):
        """
        Delete a store and refresh the table.
        """
        confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this store?")
        if confirm == QMessageBox.Yes:
            try:
                self.store_manager.delete_store(store_id)
                QMessageBox.information(self, "Success", "Store deleted successfully.")
                self.load_stores()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting store: {e}")

    def get_store_input(self, title, default_name="", default_address=""):
        """
        Show a dialog to get store name and address.
        :return: A tuple of (name, address).
        """
        name, address = default_name, default_address
        # Here, implement a custom input dialog for the user to input data.
        # For simplicity, assume the data is gathered successfully and returned.
        # Replace this with an actual implementation.
        return name, address

    def navigate_back(self):
        """
        Navigate back to the main menu.
        """
        self.navigation_manager.navigate_to("main_window")
