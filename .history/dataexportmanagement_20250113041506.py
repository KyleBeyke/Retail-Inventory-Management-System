import csv
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename="dataexport.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataExportManagement:
    """
    A class to manage the export of data from the database to various formats (CSV, Excel, etc.).
    """

    def __init__(self, db_connection):
        """
        Initialize the DataExportManagement class.
        :param db_connection: A psycopg2 connection object to the database.
        """
        self.db_connection = db_connection

    def export_to_csv(self, query, output_file):
        """
        Export the result of a query to a CSV file.
        :param query: SQL query to fetch data.
        :param output_file: Path to the output CSV file.
        :return: None.
        """
        try:
            logging.info("Starting CSV export...")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                df = pd.DataFrame(data, columns=column_names)
                df.to_csv(output_file, index=False)
                logging.info(f"Data successfully exported to {output_file}.")
        except Exception as e:
            logging.error(f"Error exporting to CSV: {e}")
            raise

    def export_to_excel(self, query, output_file):
        """
        Export the result of a query to an Excel file.
        :param query: SQL query to fetch data.
        :param output_file: Path to the output Excel file.
        :return: None.
        """
        try:
            logging.info("Starting Excel export...")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query)
                data = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]

                df = pd.DataFrame(data, columns=column_names)
                df.to_excel(output_file, index=False)
                logging.info(f"Data successfully exported to {output_file}.")
        except Exception as e:
            logging.error(f"Error exporting to Excel: {e}")
            raise
