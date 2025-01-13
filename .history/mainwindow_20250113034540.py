from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt
import logging

# Configure logging
logging.basicConfig(
    filename="mainwindow.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class MainWindow(QMainWindow):
    """
    The main application window that serves as a container for the navigation manager.
    """

    def __init__(self, navigation_manager):
        """
        Initialize the MainWindow with the NavigationManager instance.
        :param navigation_manager: The NavigationManager instance to handle navigation.
        """
        super().__init__()
        self.navigation_manager = navigation_manager

        # Set up the main window
        self.setWindowTitle("BeykeTechnik Retail Inventory Management System")
        self.setGeometry(100, 100, 800, 600)

        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Set up layout
        self.layout = QVBoxLayout(self.central_widget)

        # Add navigation controls
        self.setup_navigation_controls()

        # Add the navigation manager to the layout
        self.layout.addWidget(self.navigation_manager)

        logging.info("MainWindow initialized.")

    def setup_navigation_controls(self):
        """
        Set up navigation controls for testing and demonstration purposes.
        """
        label = QLabel("Main Menu", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        self.layout.addWidget(label)

        # Example navigation buttons
        product_button = QPushButton("Go to Product Management")
        product_button.clicked.connect(lambda: self.navigate_to("ProductManagementWindow"))
        self.layout.addWidget(product_button)

        inventory_button = QPushButton("Go to Inventory Management")
        inventory_button.clicked.connect(lambda: self.navigate_to("InventoryManagementWindow"))
        self.layout.addWidget(inventory_button)

        # Add additional navigation buttons here as needed
        sales_button = QPushButton("Go to Store Sales Management")
        sales_button.clicked.connect(lambda: self.navigate_to("StoreSalesManagementWindow"))
        self.layout.addWidget(sales_button)

    def navigate_to(self, window_name):
        """
        Navigate to a specific window using the navigation manager.
        :param window_name: Name of the window to navigate to.
        """
        try:
            self.navigation_manager.navigate_to(window_name)
            logging.info(f"Navigated to {window_name} from MainWindow.")
        except ValueError as e:
            logging.error(f"Navigation error: {e}")
