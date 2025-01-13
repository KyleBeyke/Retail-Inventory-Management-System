from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QComboBox, QMessageBox, QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from purchaseordermanagement import PurchaseOrderManagement
from suppliermanagement import SupplierManagement
from productmanagement import ProductManagement
import logging

# Configure logging
logging.basicConfig(
    filename="purchaseordermanagementwindow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class PurchaseOrderManagementWindow(QWidget):
    """
    The PyQt window for managing purchase orders.
    """

    def __init__(self, db_config, navigation_manager):
        """
        Initialize the PurchaseOrderManagementWindow.
        :param db_config: Dictionary with database configuration details.
        :param navigation_manager: Instance of the NavigationManager for handling navigation.
        """
        super().__init__()
        self.setWindowTitle("Purchase Order Management")
        self.db_config = db_config
        self.navigation_manager = navigation_manager

        self.po_manager = PurchaseOrderManagement(db_config)
        self.supplier_manager = SupplierManagement(db_config)
        self.product_manager = ProductManagement(db_config)

        # Set up layout and UI components
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()

        logging.info("PurchaseOrderManagementWindow initialized.")

    def setup_ui(self):
        """
        Set up the UI components for the Purchase Order Management Window.
        """
        # Header label
        header_label = QLabel("Manage Purchase Orders")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(header_label)

        # Add table to display purchase orders
        self.po_table = QTableWidget()
        self.po_table.setColumnCount(5)
        self.po_table.setHorizontalHeaderLabels(
            ["PO ID", "Supplier", "Order Date", "Total Items", "Total Cost"]
        )
        self.layout.addWidget(self.po_table)

        # Load purchase orders
        self.load_purchase_orders()

        # Input fields for adding new purchase orders
        input_layout = QVBoxLayout()

        self.supplier_dropdown = QComboBox()
        self.load_suppliers()
        input_layout.addWidget(self.supplier_dropdown)

        self.order_date_input = QDateEdit()
        self.order_date_input.setCalendarPopup(True)
        self.order_date_input.setDate(QDate.currentDate())
        input_layout.addWidget(self.order_date_input)

        self.product_input = QComboBox()
        self.load_products()
        input_layout.addWidget(self.product_input)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Enter Quantity")
        input_layout.addWidget(self.quantity_input)

        self.layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Purchase Order")
        add_button.clicked.connect(self.add_purchase_order)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Delete Purchase Order")
        delete_button.clicked.connect(self.delete_purchase_order)
        button_layout.addWidget(delete_button)

        back_button = QPushButton("Back to Main Menu")
        back_button.clicked.connect(self.go_back)
        button_layout.addWidget(back_button)

        self.layout.addLayout(button_layout)

    def load_purchase_orders(self):
        """
        Load purchase orders from the database and populate the table.
        """
        try:
            self.po_table.setRowCount(0)  # Clear existing rows
            purchase_orders = self.po_manager.get_all_purchase_orders()
            for row_num, po in enumerate(purchase_orders):
                self.po_table.insertRow(row_num)
                self.po_table.setItem(row_num, 0, QTableWidgetItem(str(po["po_id"])))
                self.po_table.setItem(row_num, 1, QTableWidgetItem(po["supplier_name"]))
                self.po_table.setItem(row_num, 2, QTableWidgetItem(po["order_date"]))
                self.po_table.setItem(row_num, 3, QTableWidgetItem(str(po["total_items"])))
                self.po_table.setItem(row_num, 4, QTableWidgetItem(f"${po['total_cost']:.2f}"))
            logging.info("Purchase orders loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading purchase orders: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load purchase orders: {e}")

    def load_suppliers(self):
        """
        Load supplier names into the dropdown.
        """
        try:
            suppliers = self.supplier_manager.get_all_suppliers()
            self.supplier_dropdown.clear()
            for supplier in suppliers:
                self.supplier_dropdown.addItem(supplier["supplier_name"], supplier["supplier_id"])
            logging.info("Suppliers loaded into dropdown.")
        except Exception as e:
            logging.error(f"Error loading suppliers: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load suppliers: {e}")

    def load_products(self):
        """
        Load product names into the dropdown.
        """
        try:
            products = self.product_manager.get_all_products()
            self.product_input.clear()
            for product in products:
                self.product_input.addItem(product["product_name"], product["product_id"])
            logging.info("Products loaded into dropdown.")
        except Exception as e:
            logging.error(f"Error loading products: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load products: {e}")

    def add_purchase_order(self):
        """
        Add a new purchase order to the database.
        """
        supplier_id = self.supplier_dropdown.currentData()
        order_date = self.order_date_input.date().toString("yyyy-MM-dd")
        product_id = self.product_input.currentData()
        quantity = self.quantity_input.text().strip()

        if not supplier_id or not product_id or not quantity.isdigit():
            QMessageBox.warning(self, "Input Error", "Please fill in all fields with valid data.")
            return

        try:
            self.po_manager.add_purchase_order(
                supplier_id=supplier_id,
                order_date=order_date,
                product_id=int(product_id),
                quantity=int(quantity)
            )
            QMessageBox.information(self, "Success", "Purchase order added successfully.")
            self.load_purchase_orders()
            self.quantity_input.clear()
        except Exception as e:
            logging.error(f"Error adding purchase order: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add purchase order: {e}")

    def delete_purchase_order(self):
        """
        Delete a selected purchase order from the database.
        """
        selected_row = self.po_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Selection Error", "Please select a purchase order to delete.")
            return

        po_id = self.po_table.item(selected_row, 0).text()

        try:
            self.po_manager.delete_purchase_order(int(po_id))
            QMessageBox.information(self, "Success", f"Purchase Order ID {po_id} deleted successfully.")
            self.load_purchase_orders()
        except Exception as e:
            logging.error(f"Error deleting purchase order: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete purchase order: {e}")

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
