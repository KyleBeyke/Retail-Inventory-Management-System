from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt
from suppliermanagement import SupplierManagement
import logging

# Configure logging
logging.basicConfig(
    filename="suppliermanagementwindow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class SupplierManagementWindow(QWidget):
    """
    The PyQt window for managing suppliers and supplier-product relationships.
    """

    def __init__(self, db_config, navigation_manager):
        """
        Initialize the SupplierManagementWindow with database and navigation dependencies.
        :param db_config: Dictionary with database configuration details.
        :param navigation_manager: Instance of the NavigationManager for handling navigation.
        """
        super().__init__()
        self.setWindowTitle("Supplier Management")
        self.db_config = db_config
        self.navigation_manager = navigation_manager
        self.supplier_manager = SupplierManagement(db_config)

        # Set up layout and UI components
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()

        logging.info("SupplierManagementWindow initialized.")

    def setup_ui(self):
        """
        Set up the UI components for the Supplier Management Window.
        """
        # Header label
        header_label = QLabel("Manage Suppliers")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(header_label)

        # Add table to display suppliers
        self.supplier_table = QTableWidget()
        self.supplier_table.setColumnCount(4)
        self.supplier_table.setHorizontalHeaderLabels(
            ["Supplier ID", "Supplier Name", "Contact Info", "Address"]
        )
        self.layout.addWidget(self.supplier_table)

        # Load supplier data
        self.load_suppliers()

        # Input fields for adding/updating suppliers
        input_layout = QVBoxLayout()

        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Enter Supplier Name")
        input_layout.addWidget(self.supplier_name_input)

        self.contact_info_input = QLineEdit()
        self.contact_info_input.setPlaceholderText("Enter Contact Info")
        input_layout.addWidget(self.contact_info_input)

        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Enter Address")
        input_layout.addWidget(self.address_input)

        self.layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Supplier")
        add_button.clicked.connect(self.add_supplier)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Delete Supplier")
        delete_button.clicked.connect(self.delete_supplier)
        button_layout.addWidget(delete_button)

        back_button = QPushButton("Back to Main Menu")
        back_button.clicked.connect(self.go_back)
        button_layout.addWidget(back_button)

        self.layout.addLayout(button_layout)

    def load_suppliers(self):
        """
        Load supplier data from the database and populate the table.
        """
        try:
            self.supplier_table.setRowCount(0)  # Clear existing rows
            suppliers = self.supplier_manager.get_all_suppliers()
            for row_num, supplier in enumerate(suppliers):
                self.supplier_table.insertRow(row_num)
                self.supplier_table.setItem(row_num, 0, QTableWidgetItem(str(supplier["supplier_id"])))
                self.supplier_table.setItem(row_num, 1, QTableWidgetItem(supplier["supplier_name"]))
                self.supplier_table.setItem(row_num, 2, QTableWidgetItem(supplier["contact_info"]))
                self.supplier_table.setItem(row_num, 3, QTableWidgetItem(supplier["address"]))
            logging.info("Suppliers loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading suppliers: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load suppliers: {e}")

    def add_supplier(self):
        """
        Add a new supplier to the database.
        """
        supplier_name = self.supplier_name_input.text().strip()
        contact_info = self.contact_info_input.text().strip()
        address = self.address_input.text().strip()

        if not supplier_name or not contact_info or not address:
            QMessageBox.warning(self, "Input Error", "All fields are required to add a supplier.")
            return

        try:
            self.supplier_manager.add_supplier(supplier_name, contact_info, address)
            QMessageBox.information(self, "Success", "Supplier added successfully.")
            self.load_suppliers()
            self.supplier_name_input.clear()
            self.contact_info_input.clear()
            self.address_input.clear()
        except Exception as e:
            logging.error(f"Error adding supplier: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add supplier: {e}")

    def delete_supplier(self):
        """
        Delete a selected supplier from the database.
        """
        selected_row = self.supplier_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a supplier to delete.")
            return

        supplier_id = self.supplier_table.item(selected_row, 0).text()

        try:
            self.supplier_manager.delete_supplier(int(supplier_id))
            QMessageBox.information(self, "Success", f"Supplier ID {supplier_id} deleted successfully.")
            self.load_suppliers()
        except Exception as e:
            logging.error(f"Error deleting supplier: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete supplier: {e}")

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
