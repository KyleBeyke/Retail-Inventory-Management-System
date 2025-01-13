import os
import csv
import json
import logging
import psycopg2
from psycopg2 import sql

# Configure logging
logging.basicConfig(
    filename="data_export_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataExportManagement:
    """
    Handles exporting data from the database into CSV and JSON formats.
    """

    def __init__(self, db_config):
        """
        Initialize the DataExportManagement class with database connection configuration.
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
        except psycopg2.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def export_to_csv(self, table_name, file_path, filter_conditions=None):
        """
        Export data from a table to a CSV file with optional filtering.
        :param table_name: Name of the table to export.
        :param file_path: Path to save the CSV file.
        :param filter_conditions: Optional SQL WHERE clause for filtering data.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                base_query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table_name))
                if filter_conditions:
                    query = base_query + sql.SQL(" WHERE ") + sql.SQL(filter_conditions)
                else:
                    query = base_query

                cursor.execute(query)
                rows = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]

                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(headers)  # Write headers
                    writer.writerows(rows)  # Write data

                logging.info(f"Exported table {table_name} to CSV file: {file_path}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error exporting table {table_name} to CSV: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def export_to_json(self, table_name, file_path, filter_conditions=None):
        """
        Export data from a table to a JSON file with optional filtering.
        :param table_name: Name of the table to export.
        :param file_path: Path to save the JSON file.
        :param filter_conditions: Optional SQL WHERE clause for filtering data.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                base_query = sql.SQL("SELECT * FROM {table}").format(table=sql.Identifier(table_name))
                if filter_conditions:
                    query = base_query + sql.SQL(" WHERE ") + sql.SQL(filter_conditions)
                else:
                    query = base_query

                cursor.execute(query)
                rows = cursor.fetchall()
                headers = [desc[0] for desc in cursor.description]

                data = [dict(zip(headers, row)) for row in rows]

                with open(file_path, mode='w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4)

                logging.info(f"Exported table {table_name} to JSON file: {file_path}")

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error exporting table {table_name} to JSON: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def list_tables(self):
        """
        Retrieve a list of all tables in the database.
        :return: List of table names.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = [row[0] for row in cursor.fetchall()]

                logging.info("Retrieved list of tables from the database.")
                return tables

        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error retrieving list of tables: {e}")
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

    # Export a table to CSV
    export_manager.export_to_csv("products", "products_export.csv", filter_conditions="price > 100")

    # Export a table to JSON
    export_manager.export_to_json("suppliers", "suppliers_export.json", filter_conditions="country = 'USA'")

    # List all tables in the database
    tables = export_manager.list_tables()
    print(tables)
