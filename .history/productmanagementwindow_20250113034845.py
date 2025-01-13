from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox, QLineEdit
from PyQt5.QtCore import Qt
from productmanagement import ProductManagement
import logging

# Configure logging
logging.basicConfig(
    filename="productmanagementwindow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class ProductManagementWindow(QWidget):
    """
    The PyQt window for managing products in the inventory system.
    """

    def __init__(self, db_config, navigation_manager):
        """
        Initialize the ProductManagementWindow with database and navigation dependencies.
        :param db_config: Dictionary with database configuration details.
        :param navigation_manager: Instance of the NavigationManager for handling navigation.
        """
        super().__init__()
        self.setWindowTitle("Product Management")
        self.db_config = db_config
        self.navigation_manager = navigation_manager
        self.product_manager = ProductManagement(db_config)

        # Set up layout and UI components
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setup_ui()

        logging.info("ProductManagementWindow initialized.")

    def setup_ui(self):
        """
        Set up the UI components for the Product Management Window.
        """
        # Header label
        header_label = QLabel("Manage Products")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(header_label)

        # Add table to display products
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["Product ID", "Product Name", "Category", "Price"])
        self.layout.addWidget(self.product_table)

        # Load products
        self.load_products()

        # Input fields
        input_layout = QHBoxLayout()
        self.product_name_input = QLineEdit()
        self.product_name_input.setPlaceholderText("Enter Product Name")
        input_layout.addWidget(self.product_name_input)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Enter Category")
        input_layout.addWidget(self.category_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Enter Price")
        input_layout.addWidget(self.price_input)

        self.layout.addLayout(input_layout)

        # Buttons
        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Product")
        add_button.clicked.connect(self.add_product)
        button_layout.addWidget(add_button)

        delete_button = QPushButton("Delete Selected")
        delete_button.clicked.connect(self.delete_selected_product)
        button_layout.addWidget(delete_button)

        back_button = QPushButton("Back to Main Menu")
        back_button.clicked.connect(self.go_back)
        button_layout.addWidget(back_button)

        self.layout.addLayout(button_layout)

    def load_products(self):
        """
        Load products from the database and populate the table.
        """
        try:
            self.product_table.setRowCount(0)  # Clear existing rows
            products = self.product_manager.get_all_products()
            for row_num, product in enumerate(products):
                self.product_table.insertRow(row_num)
                self.product_table.setItem(row_num, 0, QTableWidgetItem(str(product["product_id"])))
                self.product_table.setItem(row_num, 1, QTableWidgetItem(product["product_name"]))
                self.product_table.setItem(row_num, 2, QTableWidgetItem(product["category"]))
                self.product_table.setItem(row_num, 3, QTableWidgetItem(str(product["price"])))
            logging.info("Products loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading products: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load products: {e}")

    def add_product(self):
        """
        Add a new product using the input fields.
        """
        product_name = self.product_name_input.text().strip()
        category = self.category_input.text().strip()
        try:
            price = float(self.price_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Price must be a valid number.")
            return

        if not product_name or not category or price <= 0:
            QMessageBox.warning(self, "Invalid Input", "Please provide valid product details.")
            return

        try:
            self.product_manager.add_product(product_name, category, price)
            QMessageBox.information(self, "Success", "Product added successfully.")
            self.load_products()  # Refresh table
            self.product_name_input.clear()
            self.category_input.clear()
            self.price_input.clear()
        except Exception as e:
            logging.error(f"Error adding product: {e}")
            QMessageBox.critical(self, "Error", f"Failed to add product: {e}")

    def delete_selected_product(self):
        """
        Delete the selected product from the database.
        """
        selected_row = self.product_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a product to delete.")
            return

        product_id = self.product_table.item(selected_row, 0).text()
        try:
            self.product_manager.delete_product(int(product_id))
            QMessageBox.information(self, "Success", "Product deleted successfully.")
            self.load_products()  # Refresh table
        except Exception as e:
            logging.error(f"Error deleting product ID {product_id}: {e}")
            QMessageBox.critical(self, "Error", f"Failed to delete product: {e}")

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
