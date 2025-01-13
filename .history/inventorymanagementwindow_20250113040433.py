from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from inventorymanagement import InventoryManagement

class InventoryManagementWindow(QWidget):
    """
    A PyQt window for managing inventory.
    """

    def __init__(self, db_config, navigation_manager):
        super().__init__()

        self.db_config = db_config
        self.inventory_manager = InventoryManagement(db_config)
        self.navigation_manager = navigation_manager

        self.setWindowTitle("Inventory Management")
        self.setGeometry(200, 200, 800, 600)

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()

        # Header Label
        header_label = QLabel("Manage Inventory")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header_label)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by product name or ID")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_inventory)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Inventory Table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "Product ID", "Product Name", "Stock Quantity", "Reorder Level", "Actions"
        ])
        layout.addWidget(self.inventory_table)

        # Add New Product Button
        add_product_button = QPushButton("Add New Product")
        add_product_button.clicked.connect(self.add_new_product)
        layout.addWidget(add_product_button)

        # Back Button
        back_button = QPushButton("Back to Main Menu")
        back_button.clicked.connect(self.go_back)
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.load_inventory()

    def load_inventory(self):
        """Load inventory data into the table."""
        try:
            inventory = self.inventory_manager.get_all_inventory()
            self.inventory_table.setRowCount(0)

            for row_idx, item in enumerate(inventory):
                self.inventory_table.insertRow(row_idx)
                self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(str(item["product_id"])))
                self.inventory_table.setItem(row_idx, 1, QTableWidgetItem(item["product_name"]))
                self.inventory_table.setItem(row_idx, 2, QTableWidgetItem(str(item["stock_quantity"])))
                self.inventory_table.setItem(row_idx, 3, QTableWidgetItem(str(item["reorder_level"])))

                # Add "Edit" and "Delete" buttons
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, row=row_idx: self.edit_inventory(row))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, row=row_idx: self.delete_inventory(row))
                action_layout = QHBoxLayout()
                action_layout.addWidget(edit_button)
                action_layout.addWidget(delete_button)
                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.inventory_table.setCellWidget(row_idx, 4, action_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load inventory: {e}")

    def search_inventory(self):
        """Search inventory based on input."""
        query = self.search_input.text().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a search term.")
            return

        try:
            results = self.inventory_manager.search_inventory(query)
            self.inventory_table.setRowCount(0)

            for row_idx, item in enumerate(results):
                self.inventory_table.insertRow(row_idx)
                self.inventory_table.setItem(row_idx, 0, QTableWidgetItem(str(item["product_id"])))
                self.inventory_table.setItem(row_idx, 1, QTableWidgetItem(item["product_name"]))
                self.inventory_table.setItem(row_idx, 2, QTableWidgetItem(str(item["stock_quantity"])))
                self.inventory_table.setItem(row_idx, 3, QTableWidgetItem(str(item["reorder_level"])))

                # Add "Edit" and "Delete" buttons
                edit_button = QPushButton("Edit")
                edit_button.clicked.connect(lambda _, row=row_idx: self.edit_inventory(row))
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, row=row_idx: self.delete_inventory(row))
                action_layout = QHBoxLayout()
                action_layout.addWidget(edit_button)
                action_layout.addWidget(delete_button)
                action_widget = QWidget()
                action_widget.setLayout(action_layout)
                self.inventory_table.setCellWidget(row_idx, 4, action_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed: {e}")

    def add_new_product(self):
        """Add a new product to the inventory."""
        QMessageBox.information(self, "Info", "This feature is under construction.")

    def edit_inventory(self, row):
        """Edit inventory item."""
        product_id = self.inventory_table.item(row, 0).text()
        QMessageBox.information(self, "Info", f"Editing product ID: {product_id} (Feature under construction)")

    def delete_inventory(self, row):
        """Delete inventory item."""
        product_id = self.inventory_table.item(row, 0).text()
        try:
            confirmation = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete product ID: {product_id}?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmation == QMessageBox.Yes:
                self.inventory_manager.delete_inventory_item(int(product_id))
                QMessageBox.information(self, "Success", f"Product ID: {product_id} deleted.")
                self.load_inventory()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete product: {e}")

    def go_back(self):
        """Navigate back to the main menu."""
        self.navigation_manager.go_to_main_menu()
        self.close()

# Example usage:
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Example db_config and navigation manager stub
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    class NavigationManagerStub:
        def go_to_main_menu(self):
            print("Navigating to Main Menu")

    navigation_manager = NavigationManagerStub()

    window = InventoryManagementWindow(db_config, navigation_manager)
    window.show()

    sys.exit(app.exec_())
