import os
import shutil
from datetime import datetime, timedelta
import logging
import psycopg2
from psycopg2 import sql, Error

# Configure logging
logging.basicConfig(
    filename="system_maintenance.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SystemMaintenanceManagement:
    """
    A class to handle routine system maintenance tasks such as log rotation,
    temporary file cleanup, and database optimization.
    """

    def __init__(self, log_directory="logs", temp_directory="temp", db_config=None):
        """
        Initialize the SystemMaintenanceManagement class.
        :param log_directory: Path to the directory containing log files.
        :param temp_directory: Path to the directory containing temporary files.
        :param db_config: Dictionary containing database connection details.
        """
        self.log_directory = log_directory
        self.temp_directory = temp_directory
        self.db_config = db_config

    def rotate_logs(self, retention_days=30):
        """
        Rotate and archive old logs older than a specified number of days.
        :param retention_days: Number of days to retain logs before archiving.
        :return: None
        """
        try:
            if not os.path.exists(self.log_directory):
                logging.warning(f"Log directory '{self.log_directory}' does not exist.")
                return

            now = datetime.now()
            archive_dir = os.path.join(self.log_directory, "archive")
            os.makedirs(archive_dir, exist_ok=True)

            for file_name in os.listdir(self.log_directory):
                file_path = os.path.join(self.log_directory, file_name)
                if os.path.isfile(file_path):
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_mod_time > timedelta(days=retention_days):
                        shutil.move(file_path, os.path.join(archive_dir, file_name))
                        logging.info(f"Archived log file: {file_name}")
        except Exception as e:
            logging.error(f"Error rotating logs: {e}")
            raise

    def clean_temp_files(self, retention_days=7):
        """
        Delete temporary files older than a specified number of days.
        :param retention_days: Number of days to retain temporary files.
        :return: None
        """
        try:
            if not os.path.exists(self.temp_directory):
                logging.warning(f"Temporary directory '{self.temp_directory}' does not exist.")
                return

            now = datetime.now()

            for file_name in os.listdir(self.temp_directory):
                file_path = os.path.join(self.temp_directory, file_name)
                if os.path.isfile(file_path):
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_mod_time > timedelta(days=retention_days):
                        os.remove(file_path)
                        logging.info(f"Deleted temporary file: {file_name}")
        except Exception as e:
            logging.error(f"Error cleaning temporary files: {e}")
            raise

    def optimize_database(self):
        """
        Perform database optimization tasks, such as vacuuming and analyzing tables.
        :return: None
        """
        if not self.db_config:
            logging.error("Database configuration is not provided.")
            return

        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("VACUUM;")
                cursor.execute("ANALYZE;")
                conn.commit()
                logging.info("Database optimization completed successfully.")
        except Error as e:
            logging.error(f"Error optimizing the database: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def remove_old_archives(self, archive_directory=None, retention_days=90):
        """
        Delete archived log files older than a specified number of days.
        :param archive_directory: Path to the directory containing archived logs.
        :param retention_days: Number of days to retain archived logs.
        :return: None
        """
        archive_directory = archive_directory or os.path.join(self.log_directory, "archive")

        try:
            if not os.path.exists(archive_directory):
                logging.warning(f"Archive directory '{archive_directory}' does not exist.")
                return

            now = datetime.now()

            for file_name in os.listdir(archive_directory):
                file_path = os.path.join(archive_directory, file_name)
                if os.path.isfile(file_path):
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_mod_time > timedelta(days=retention_days):
                        os.remove(file_path)
                        logging.info(f"Deleted old archive file: {file_name}")
        except Exception as e:
            logging.error(f"Error removing old archive files: {e}")
            raise

    def perform_full_maintenance(self):
        """
        Perform a full maintenance routine, including log rotation,
        temporary file cleanup, and database optimization.
        :return: None
        """
        logging.info("Starting full system maintenance routine.")
        try:
            self.rotate_logs()
            self.clean_temp_files()
            self.optimize_database()
            self.remove_old_archives()
            logging.info("Full system maintenance routine completed successfully.")
        except Exception as e:
            logging.error(f"Error during full system maintenance routine: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    # Example database configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    maintenance_manager = SystemMaintenanceManagement(
        log_directory="logs",
        temp_directory="temp",
        db_config=db_config
    )

    # Rotate logs older than 30 days
    maintenance_manager.rotate_logs()

    # Clean temporary files older than 7 days
    maintenance_manager.clean_temp_files()

    # Optimize the database
    maintenance_manager.optimize_database()

    # Remove old archived logs older than 90 days
    maintenance_manager.remove_old_archives()

    # Perform a full maintenance routine
    maintenance_manager.perform_full_maintenance()
