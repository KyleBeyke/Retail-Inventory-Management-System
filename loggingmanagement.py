import logging
import os
from datetime import datetime

class LoggingManagement:
    """
    A class to manage logging configurations and provide a centralized logging utility.
    This class ensures consistent logging standards across the application.
    """

    def __init__(self, log_dir="logs"):
        """
        Initialize the LoggingManagement class.

        :param log_dir: Directory where log files will be stored.
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.loggers = {}
        logging.info(f"Logging directory initialized at: {log_dir}")

    def get_logger(self, name, log_file=None):
        """
        Get a logger instance with the specified name. Optionally set a log file for the logger.

        :param name: Name of the logger.
        :param log_file: File path for logging. If not provided, logs will only output to the console.
        :return: A configured logger instance.
        """
        if name in self.loggers:
            return self.loggers[name]

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # Optionally add a file handler
        if log_file:
            log_file_path = os.path.join(self.log_dir, log_file)
            file_handler = logging.FileHandler(log_file_path, mode='a')
            file_handler.setLevel(logging.INFO)
            file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            logging.info(f"Logger {name} configured to log to file: {log_file_path}")

        self.loggers[name] = logger
        return logger

    def log_message(self, name, level, message):
        """
        Log a message using a specific logger by name.

        :param name: Name of the logger.
        :param level: Log level ('INFO', 'WARNING', 'ERROR', 'DEBUG').
        :param message: Message to log.
        """
        logger = self.get_logger(name)
        log_methods = {
            'INFO': logger.info,
            'WARNING': logger.warning,
            'ERROR': logger.error,
            'DEBUG': logger.debug
        }

        if level in log_methods:
            log_methods[level](message)
        else:
            logger.info(f"Invalid log level specified: {level}. Defaulted to INFO. Message: {message}")

    def archive_old_logs(self, retention_days=7):
        """
        Archive log files older than the specified retention period.

        :param retention_days: Number of days to retain log files before archiving.
        :return: None.
        """
        try:
            now = datetime.now()
            archive_dir = os.path.join(self.log_dir, "archive")
            os.makedirs(archive_dir, exist_ok=True)

            for filename in os.listdir(self.log_dir):
                file_path = os.path.join(self.log_dir, filename)

                if os.path.isfile(file_path) and not filename.startswith("archive"):
                    file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_days = (now - file_creation_time).days

                    if age_days > retention_days:
                        archived_path = os.path.join(archive_dir, filename)
                        os.rename(file_path, archived_path)
                        logging.info(f"Archived old log file: {file_path} to {archived_path}")
        except Exception as e:
            logging.error(f"Error archiving old log files: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    # Initialize logging manager
    log_manager = LoggingManagement()

    # Get a logger instance
    app_logger = log_manager.get_logger("Application", log_file="application.log")

    # Log messages
    log_manager.log_message("Application", "INFO", "This is an info message.")
    log_manager.log_message("Application", "ERROR", "This is an error message.")

    # Archive old logs
    log_manager.archive_old_logs(retention_days=7)
