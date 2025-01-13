import os
import csv
import json
import logging
import psycopg2
from psycopg2 import sql
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="data_import_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataImportManagement:
    """
    Handles importing data into the database from CSV and JSON formats.
    """

    def __init__(self, db_config):
        """
        Initialize the DataImportManagement class with database connection configuration.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        """
        self.db_config = db_config
        self.validator = DataValidationManagement()

    def _connect(self):
        """
        Establish a connection to the PostgreSQL database.
        :return: A psycopg2 connection object.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def import_from_csv(self, table_name, file_path):
        """
        Import data from a CSV file into a table.
        :param table_name: Name of the table to import data into.
        :param file_path: Path of the CSV file to import.
        :return: None
        """
        if not os.path.exists(file_path):
            logging.error(f"CSV file not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            conn = self._connect()
            with conn.cursor() as cursor, open(file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                columns = reader.fieldnames

                # Validate headers
                if not self.validator.validate_headers(table_name, columns):
                    raise ValueError(f"Invalid columns for table {table_name}: {columns}")

                batch_data = []
                for row in reader:
                    # Validate row data
                    if not self.validator.validate_row(table_name, row):
                        logging.warning(f"Skipping invalid row: {row}")
                        continue

                    batch_data.append(row)

                    # Batch insert every 100 rows
                    if len(batch_data) >= 100:
                        self._insert_batch(cursor, table_name, columns, batch_data)
                        batch_data = []

                # Insert any remaining data
                if batch_data:
                    self._insert_batch(cursor, table_name, columns, batch_data)

                conn.commit()
                logging.info(f"Imported data from CSV file: {file_path} into table {table_name}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error importing data from CSV to table {table_name}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def import_from_json(self, table_name, file_path):
        """
        Import data from a JSON file into a table.
        :param table_name: Name of the table to import data into.
        :param file_path: Path of the JSON file to import.
        :return: None
        """
        if not os.path.exists(file_path):
            logging.error(f"JSON file not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            conn = self._connect()
            with conn.cursor() as cursor, open(file_path, mode='r', encoding='utf-8') as file:
                data = json.load(file)

                if not isinstance(data, list):
                    logging.error("JSON file must contain a list of records.")
                    raise ValueError("JSON file must contain a list of records.")

                batch_data = []
                for row in data:
                    # Validate row data
                    if not self.validator.validate_row(table_name, row):
                        logging.warning(f"Skipping invalid row: {row}")
                        continue

                    batch_data.append(row)

                    # Batch insert every 100 rows
                    if len(batch_data) >= 100:
                        self._insert_batch(cursor, table_name, row.keys(), batch_data)
                        batch_data = []

                # Insert any remaining data
                if batch_data:
                    self._insert_batch(cursor, table_name, row.keys(), batch_data)

                conn.commit()
                logging.info(f"Imported data from JSON file: {file_path} into table {table_name}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error importing data from JSON to table {table_name}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def _insert_batch(self, cursor, table_name, columns, batch_data):
        """
        Insert a batch of data into the table.
        :param cursor: Database cursor.
        :param table_name: Name of the table to insert data into.
        :param columns: List of column names.
        :param batch_data: List of row dictionaries to insert.
        """
        try:
            insert_query = sql.SQL("INSERT INTO {table} ({fields}) VALUES {values}")
            values_template = sql.SQL(",").join(
                sql.SQL("({})").format(sql.SQL(",").join(sql.Placeholder() * len(columns)))
                for _ in batch_data
            )

            cursor.execute(
                insert_query.format(
                    table=sql.Identifier(table_name),
                    fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                    values=values_template
                ),
                [value for row in batch_data for value in row.values()]
            )

        except psycopg2.Error as e:
            logging.error(f"Error during batch insert to table {table_name}: {e}")
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

    import_manager = DataImportManagement(db_config)

    # Import data from CSV
    import_manager.import_from_csv("products", "products_import.csv")

    # Import data from JSON
    import_manager.import_from_json("suppliers", "suppliers_import.json")
