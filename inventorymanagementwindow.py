from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QLineEdit, QComboBox
)
from PyQt5.QtCore import Qt
from inventorymanagement import InventoryManagement
import logging

# Configure logging
logging.basicConfig(
    filename="inventorymanagementwindow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class InventoryManagementWindow(QWidget):
    """
    The PyQt window for managing inventory levels and stock transfers.
    """

    def __init__(self, db_config, navigation_manager):
        """
        Initialize the InventoryManagementWindow with database and navigation dependencies.
        :param db_config: Dictionary with database configuration details.
        :param navigation_manager: Instance of the NavigationManager for handling navigation.
        """
        super().__init__()
        self.setWindowTitle("Inventory Management")
        self.db_config = db_config
        self.navigation_manager = navigation_manager
        self.inventory_manager = InventoryManagement(db_config)

        # Set up layout and UI components
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()

        logging.info("InventoryManagementWindow initialized.")

    def setup_ui(self):
        """
        Set up the UI components for the Inventory Management Window.
        """
        # Header label
        header_label = QLabel("Manage Inventory")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(header_label)

        # Add table to display inventory
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(
            ["Product ID", "Product Name", "Store", "Stock Level", "Reorder Level"]
        )
        self.layout.addWidget(self.inventory_table)

        # Load inventory data
        self.load_inventory()

        # Input fields for stock adjustment
        input_layout = QHBoxLayout()
        self.product_id_input = QLineEdit()
        self.product_id_input.setPlaceholderText("Enter Product ID")
        input_layout.addWidget(self.product_id_input)

        self.store_input = QComboBox()
        self.store_input.setPlaceholderText("Select Store")
        self.load_stores()
        input_layout.addWidget(self.store_input)

        self.stock_level_input = QLineEdit()
        self.stock_level_input.setPlaceholderText("Enter New Stock Level")
        input_layout.addWidget(self.stock_level_input)

        self.layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()

        update_button = QPushButton("Update Stock Level")
        update_button.clicked.connect(self.update_stock_level)
        button_layout.addWidget(update_button)

        transfer_button = QPushButton("Transfer Stock")
        transfer_button.clicked.connect(self.transfer_stock)
        button_layout.addWidget(transfer_button)

        back_button = QPushButton("Back to Main Menu")
        back_button.clicked.connect(self.go_back)
        button_layout.addWidget(back_button)

        self.layout.addLayout(button_layout)

    def load_inventory(self):
        """
        Load inventory data from the database and populate the table.
        """
        try:
            self.inventory_table.setRowCount(0)  # Clear existing rows
            inventory = self.inventory_manager.get_all_inventory()
            for row_num, item in enumerate(inventory):
                self.inventory_table.insertRow(row_num)
                self.inventory_table.setItem(row_num, 0, QTableWidgetItem(str(item["product_id"])))
                self.inventory_table.setItem(row_num, 1, QTableWidgetItem(item["product_name"]))
                self.inventory_table.setItem(row_num, 2, QTableWidgetItem(item["store_name"]))
                self.inventory_table.setItem(row_num, 3, QTableWidgetItem(str(item["stock_level"])))
                self.inventory_table.setItem(row_num, 4, QTableWidgetItem(str(item["reorder_level"])))
            logging.info("Inventory loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading inventory: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {e}")

    def load_stores(self):
        """
        Load the list of stores into the store dropdown.
        """
        try:
            stores = self.inventory_manager.get_all_stores()
            self.store_input.clear()
            for store in stores:
                self.store_input.addItem(store["store_name"], store["store_id"])
            logging.info("Stores loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading stores: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load stores: {e}")

    def update_stock_level(self):
        """
        Update the stock level for a specific product in a store.
        """
        try:
            product_id = int(self.product_id_input.text().strip())
            store_id = self.store_input.currentData()
            stock_level = int(self.stock_level_input.text().strip())

            if stock_level < 0:
                QMessageBox.warning(self, "Invalid Input", "Stock level must be non-negative.")
                return

            self.inventory_manager.update_stock(product_id, store_id, stock_level)
            QMessageBox.information(self, "Success", "Stock level updated successfully.")
            self.load_inventory()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please provide valid input for all fields.")
        except Exception as e:
            logging.error(f"Error updating stock level: {e}")
            QMessageBox.critical(self, "Error", f"Failed to update stock level: {e}")

    def transfer_stock(self):
        """
        Transfer stock from one store to another.
        """
        # Additional functionality can be added here for stock transfer between stores
        QMessageBox.information(self, "Info", "Stock transfer functionality is not yet implemented.")
        logging.info("Stock transfer functionality triggered but not implemented.")

    def go_back(self):
        """
        Navigate back to the main menu.
        """
        try:
            self.navigation_manager.navigate_to("MainWindow")
            logging.info("Navigated back to MainWindow.")
        except Exception as e:
            logging.error(f"Error navigating back to MainWindow: {e}")
            QMessageBox.critical(self, "Error", f"Failed to navigate back: {e}")
