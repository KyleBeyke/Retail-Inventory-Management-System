import pandas as pd
import psycopg2
import logging

# Configure logging
logging.basicConfig(
    filename="dataimport.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataImportManagement:
    """
    A class to manage the import of data into the database from various formats (CSV, Excel, etc.).
    """

    def __init__(self, db_connection):
        """
        Initialize the DataImportManagement class.
        :param db_connection: A psycopg2 connection object to the database.
        """
        self.db_connection = db_connection

    def import_from_csv(self, input_file, table_name):
        """
        Import data from a CSV file into a specified database table.
        :param input_file: Path to the input CSV file.
        :param table_name: Name of the table to insert data into.
        :return: None.
        """
        try:
            logging.info("Starting CSV import...")
            df = pd.read_csv(input_file)

            with self.db_connection.cursor() as cursor:
                for index, row in df.iterrows():
                    columns = ", ".join(row.index)
                    placeholders = ", ".join(["%s"] * len(row))
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, tuple(row.values))
                self.db_connection.commit()

            logging.info(f"Data successfully imported from {input_file} to {table_name}.")
        except Exception as e:
            logging.error(f"Error importing from CSV: {e}")
            raise

    def import_from_excel(self, input_file, table_name, sheet_name=0):
        """
        Import data from an Excel file into a specified database table.
        :param input_file: Path to the input Excel file.
        :param table_name: Name of the table to insert data into.
        :param sheet_name: Sheet name or index to read from.
        :return: None.
        """
        try:
            logging.info("Starting Excel import...")
            df = pd.read_excel(input_file, sheet_name=sheet_name)

            with self.db_connection.cursor() as cursor:
                for index, row in df.iterrows():
                    columns = ", ".join(row.index)
                    placeholders = ", ".join(["%s"] * len(row))
                    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    cursor.execute(query, tuple(row.values))
                self.db_connection.commit()

            logging.info(f"Data successfully imported from {input_file} to {table_name}.")
        except Exception as e:
            logging.error(f"Error importing from Excel: {e}")
            raise