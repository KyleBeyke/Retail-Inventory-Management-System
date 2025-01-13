from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QMenuBar, QAction, QWidget, QLabel, QMessageBox
from PyQt5.QtCore import Qt
from navigation import NavigationManager
import logging

# Configure logging
logging.basicConfig(
    filename="application.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class MainWindow(QMainWindow):
    """
    Main application window that serves as the entry point and navigation hub for the inventory management system.
    """

    def __init__(self, navigation_manager):
        """
        Initialize the MainWindow class.
        :param navigation_manager: Instance of NavigationManager for window navigation.
        """
        super().__init__()
        self.navigation_manager = navigation_manager
        self.setWindowTitle("BeykeTechnik Retail Inventory Management System")
        self.setGeometry(100, 100, 1200, 800)

        # Set up the layout
        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Add welcome message
        self.welcome_label = QLabel("Welcome to the BeykeTechnik Retail Inventory Management System")
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.welcome_label)

        # Configure the menu bar
        self.menu_bar = QMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self._setup_menu()

        # Log the initialization
        logging.info("Main window initialized.")

    def _setup_menu(self):
        """
        Configure the menu bar with navigation options.
        """
        # Product menu
        product_menu = self.menu_bar.addMenu("Products")
        product_management_action = QAction("Manage Products", self)
        product_management_action.triggered.connect(self._navigate_to_product_management)
        product_menu.addAction(product_management_action)

        # Inventory menu
        inventory_menu = self.menu_bar.addMenu("Inventory")
        inventory_management_action = QAction("Manage Inventory", self)
        inventory_management_action.triggered.connect(self._navigate_to_inventory_management)
        inventory_menu.addAction(inventory_management_action)

        # Suppliers menu
        suppliers_menu = self.menu_bar.addMenu("Suppliers")
        supplier_management_action = QAction("Manage Suppliers", self)
        supplier_management_action.triggered.connect(self._navigate_to_supplier_management)
        suppliers_menu.addAction(supplier_management_action)

        # Purchase Orders menu
        po_menu = self.menu_bar.addMenu("Purchase Orders")
        po_management_action = QAction("Manage Purchase Orders", self)
        po_management_action.triggered.connect(self._navigate_to_purchase_order_management)
        po_menu.addAction(po_management_action)

        # Reports menu
        reports_menu = self.menu_bar.addMenu("Reports")
        reports_action = QAction("View Reports", self)
        reports_action.triggered.connect(self._navigate_to_reports)
        reports_menu.addAction(reports_action)

        # Settings menu
        settings_menu = self.menu_bar.addMenu("Settings")
        settings_action = QAction("Configure Settings", self)
        settings_action.triggered.connect(self._navigate_to_settings)
        settings_menu.addAction(settings_action)

        # User menu
        user_menu = self.menu_bar.addMenu("Users")
        user_management_action = QAction("Manage Users", self)
        user_management_action.triggered.connect(self._navigate_to_user_management)
        user_menu.addAction(user_management_action)

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _navigate_to_product_management(self):
        """
        Navigate to the Product Management window.
        """
        self.navigation_manager.navigate_to("ProductManagementWindow")

    def _navigate_to_inventory_management(self):
        """
        Navigate to the Inventory Management window.
        """
        self.navigation_manager.navigate_to("InventoryManagementWindow")

    def _navigate_to_supplier_management(self):
        """
        Navigate to the Supplier Management window.
        """
        self.navigation_manager.navigate_to("SupplierManagementWindow")

    def _navigate_to_purchase_order_management(self):
        """
        Navigate to the Purchase Order Management window.
        """
        self.navigation_manager.navigate_to("PurchaseOrderManagementWindow")

    def _navigate_to_reports(self):
        """
        Navigate to the Reporting window.
        """
        self.navigation_manager.navigate_to("ReportingWindow")

    def _navigate_to_settings(self):
        """
        Navigate to the Settings window.
        """
        self.navigation_manager.navigate_to("SettingsWindow")

    def _navigate_to_user_management(self):
        """
        Navigate to the User Management window.
        """
        self.navigation_manager.navigate_to("UserManagementWindow")

    def _show_about_dialog(self):
        """
        Display an About dialog with application information.
        """
        QMessageBox.information(
            self,
            "About",
            "BeykeTechnik Retail Inventory Management System\nVersion 1.0\nDeveloped by Kyle Beyke"
        )

# Example usage for testing
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    class MockNavigationManager:
        def navigate_to(self, window_name):
            print(f"Navigation to {window_name} triggered.")

    app = QApplication(sys.argv)
    navigation_manager = MockNavigationManager()
    main_window = MainWindow(navigation_manager)
    main_window.show()
    sys.exit(app.exec_())