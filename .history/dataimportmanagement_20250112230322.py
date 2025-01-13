import psycopg2
import csv
import os
import logging
from psycopg2 import Error

# Configure logging
logging.basicConfig(
    filename="data_import_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataImportManagement:
    """
    A class to handle importing data into the system from external sources.
    Supports formats like CSV and integrates data validation before insertion.
    """

    def __init__(self, db_config):
        """
        Initialize the DataImportManagement class with database connection configuration.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        """
        self.db_config = db_config

    def _connect(self):
        """
        Establish a connection to the PostgreSQL database.
        :return: A psycopg2 connection object.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def import_csv_to_table(self, file_path, table_name, column_mapping):
        """
        Import data from a CSV file into a specified database table.
        :param file_path: Path to the CSV file.
        :param table_name: Name of the table to import data into.
        :param column_mapping: Dictionary mapping CSV headers to database columns.
        :return: Number of rows successfully imported.
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                with open(file_path, mode="r") as csv_file:
                    reader = csv.DictReader(csv_file)
                    headers = reader.fieldnames

                    # Validate column mapping
                    if not set(column_mapping.keys()).issubset(set(headers)):
                        logging.error("Column mapping keys do not match CSV headers.")
                        raise ValueError("Column mapping keys do not match CSV headers.")

                    rows_imported = 0
                    for row in reader:
                        # Prepare SQL statement
                        columns = [column_mapping[col] for col in column_mapping]
                        values = [row[col] for col in column_mapping]
                        placeholders = ", ".join(["%s"] * len(values))

                        query = f"""
                        INSERT INTO {table_name} ({", ".join(columns)})
                        VALUES ({placeholders})
                        ON CONFLICT DO NOTHING;
                        """
                        cursor.execute(query, values)
                        rows_imported += 1

                conn.commit()
                logging.info(f"Successfully imported {rows_imported} rows into {table_name}.")
                return rows_imported
        except Error as e:
            logging.error(f"Error importing CSV data into table {table_name}: {e}")
            raise
        finally:
            conn.close()

    def validate_csv(self, file_path, required_columns):
        """
        Validate the CSV file to ensure it contains the required columns.
        :param file_path: Path to the CSV file.
        :param required_columns: List of required column headers.
        :return: Boolean indicating whether the file is valid.
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, mode="r") as csv_file:
                reader = csv.DictReader(csv_file)
                headers = reader.fieldnames
                missing_columns = [col for col in required_columns if col not in headers]

                if missing_columns:
                    logging.warning(f"Missing required columns: {missing_columns}")
                    return False

                logging.info("CSV file validation passed.")
                return True
        except Exception as e:
            logging.error(f"Error validating CSV file {file_path}: {e}")
            raise

    def import_data_from_directory(self, directory_path, table_name, column_mapping, required_columns=None):
        """
        Import multiple CSV files from a directory into a specified table.
        :param directory_path: Path to the directory containing CSV files.
        :param table_name: Name of the table to import data into.
        :param column_mapping: Dictionary mapping CSV headers to database columns.
        :param required_columns: List of required column headers for validation (optional).
        :return: Total number of rows imported.
        """
        if not os.path.isdir(directory_path):
            logging.error(f"Directory not found: {directory_path}")
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        total_rows_imported = 0
        try:
            for file_name in os.listdir(directory_path):
                if file_name.endswith(".csv"):
                    file_path = os.path.join(directory_path, file_name)
                    logging.info(f"Processing file: {file_path}")

                    # Validate file
                    if required_columns:
                        if not self.validate_csv(file_path, required_columns):
                            logging.warning(f"Skipping invalid file: {file_path}")
                            continue

                    # Import file
                    rows_imported = self.import_csv_to_table(file_path, table_name, column_mapping)
                    total_rows_imported += rows_imported

            logging.info(f"Total rows imported from directory: {total_rows_imported}.")
            return total_rows_imported
        except Exception as e:
            logging.error(f"Error importing data from directory {directory_path}: {e}")
            raise

# Example Usage:
if __name__ == "__main__":
    # Database configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    data_import_manager = DataImportManagement(db_config)

    # Import a single CSV file
    column_mapping = {
        "Product Name": "product_name",
        "SKU": "sku",
        "Quantity": "quantity",
        "Price": "price"
    }
    required_columns = ["Product Name", "SKU", "Quantity", "Price"]
    rows = data_import_manager.import_csv_to_table("products.csv", "products", column_mapping)
    print(f"Rows imported: {rows}")

    # Import multiple CSV files from a directory
    total_rows = data_import_manager.import_data_from_directory("data/import", "products", column_mapping, required_columns)
    print(f"Total rows imported: {total_rows}")
