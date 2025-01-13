from PyQt5.QtWidgets import QStackedWidget
import logging

# Configure logging
logging.basicConfig(
    filename="navigation.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class NavigationManager(QStackedWidget):
    """
    A class to manage navigation between different windows in the application.
    """

    def __init__(self):
        """
        Initialize the NavigationManager with a QStackedWidget.
        """
        super().__init__()
        self.windows = {}
        logging.info("NavigationManager initialized.")

    def register_window(self, window_name, window_instance):
        """
        Register a window with the navigation manager.
        :param window_name: Unique name of the window.
        :param window_instance: Instance of the window to register.
        """
        if window_name in self.windows:
            logging.warning(f"Window {window_name} is already registered. Overwriting.")
        self.windows[window_name] = window_instance
        self.addWidget(window_instance)
        logging.info(f"Registered window: {window_name}")

    def navigate_to(self, window_name):
        """
        Navigate to a specific window by its name.
        :param window_name: The name of the window to navigate to.
        """
        if window_name not in self.windows:
            logging.error(f"Window {window_name} is not registered.")
            raise ValueError(f"Window {window_name} is not registered.")
        self.setCurrentWidget(self.windows[window_name])
        logging.info(f"Navigated to window: {window_name}")
