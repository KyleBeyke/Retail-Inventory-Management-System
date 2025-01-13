import os
import psycopg2
from psycopg2 import Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="backup_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BackupManagement:
    """
    A class to manage database backups and restoration for the inventory management system.
    Provides methods to create backups, restore from backups, and handle backup retention.
    """

    def __init__(self, db_config, backup_dir="backups"):
        """
        Initialize the BackupManagement class.

        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        :param backup_dir: Directory where backups will be stored.
        """
        self.db_config = db_config
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
        logging.info(f"Backup directory initialized at: {backup_dir}")

    def create_backup(self):
        """
        Create a backup of the PostgreSQL database.

        :return: Path to the backup file.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"backup_{timestamp}.sql")

            command = (
                f"pg_dump --dbname=postgresql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']} > {backup_file}"
            )

            os.system(command)

            if os.path.exists(backup_file):
                logging.info(f"Backup created successfully: {backup_file}")
                return backup_file
            else:
                logging.error("Backup creation failed. File not found.")
                raise Exception("Backup creation failed.")
        except Exception as e:
            logging.error(f"Error creating backup: {e}")
            raise

    def restore_backup(self, backup_file):
        """
        Restore the database from a backup file.

        :param backup_file: Path to the backup file to restore from.
        :return: None.
        """
        try:
            if not os.path.exists(backup_file):
                logging.error(f"Backup file does not exist: {backup_file}")
                raise FileNotFoundError(f"Backup file not found: {backup_file}")

            command = (
                f"psql --dbname=postgresql://{self.db_config['user']}:{self.db_config['password']}"
                f"@{self.db_config['host']}:{self.db_config['port']}/{self.db_config['dbname']} < {backup_file}"
            )

            os.system(command)

            logging.info(f"Database restored successfully from backup: {backup_file}")
        except Exception as e:
            logging.error(f"Error restoring backup: {e}")
            raise

    def cleanup_old_backups(self, retention_days=7):
        """
        Remove backup files older than a specified number of days.

        :param retention_days: Number of days to retain backups. Files older than this will be deleted.
        :return: None.
        """
        try:
            now = datetime.now()

            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                if os.path.isfile(file_path):
                    file_creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                    age_days = (now - file_creation_time).days

                    if age_days > retention_days:
                        os.remove(file_path)
                        logging.info(f"Deleted old backup file: {file_path}")
        except Exception as e:
            logging.error(f"Error cleaning up old backups: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    backup_manager = BackupManagement(db_config)

    # Create a backup
    backup_file_path = backup_manager.create_backup()
    print(f"Backup created at: {backup_file_path}")

    # Restore the database from the backup
    backup_manager.restore_backup(backup_file_path)

    # Clean up old backups
    backup_manager.cleanup_old_backups(retention_days=7)
