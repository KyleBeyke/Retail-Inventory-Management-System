import os
import csv
import json
import logging
import psycopg2
from psycopg2 import sql
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="data_export_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataExportManagement:
    """
    Handles exporting data from the database to CSV and JSON formats.
    """

    def __init__(self, db_config):
        """
        Initialize the DataExportManagement class with database connection configuration.
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

    def export_to_csv(self, table_name, file_path):
        """
        Export data from a table to a CSV file.
        :param table_name: Name of the table to export data from.
        :param file_path: Path of the CSV file to save the data.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT * FROM {table}").format(
                    table=sql.Identifier(table_name)
                ))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Validate headers
                if not self.validator.validate_headers(table_name, columns):
                    raise ValueError(f"Invalid columns for table {table_name}: {columns}")

                # Write to CSV file
                with open(file_path, mode='w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(columns)  # Write headers
                    writer.writerows(rows)

                logging.info(f"Exported data from table {table_name} to CSV file: {file_path}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error exporting data from table {table_name} to CSV: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def export_to_json(self, table_name, file_path):
        """
        Export data from a table to a JSON file.
        :param table_name: Name of the table to export data from.
        :param file_path: Path of the JSON file to save the data.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT * FROM {table}").format(
                    table=sql.Identifier(table_name)
                ))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Validate headers
                if not self.validator.validate_headers(table_name, columns):
                    raise ValueError(f"Invalid columns for table {table_name}: {columns}")

                # Convert rows to list of dictionaries
                data = [dict(zip(columns, row)) for row in rows]

                # Write to JSON file
                with open(file_path, mode='w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)

                logging.info(f"Exported data from table {table_name} to JSON file: {file_path}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error exporting data from table {table_name} to JSON: {e}")
            raise
        finally:
            if conn:
                conn.close()

# Example Usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    export_manager = DataExportManagement(db_config)

    # Export data to CSV
    export_manager.export_to_csv("products", "products_export.csv")

    # Export data to JSON
    export_manager.export_to_json("suppliers", "suppliers_export.json")
