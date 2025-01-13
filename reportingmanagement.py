import psycopg2
from psycopg2 import sql, Error
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename="reporting_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ReportingManagement:
    """
    A class to handle reporting for the inventory management system.
    This includes generating and exporting various reports such as inventory levels,
    supplier performance, and stock movements.
    """

    def __init__(self, db_config):
        """
        Initialize the ReportingManagement class with database connection configuration.
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

    def generate_inventory_report(self):
        """
        Generate a report of current inventory levels for all products.
        :return: Pandas DataFrame containing inventory report.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT
                    p.product_id,
                    p.product_name,
                    ss.store_id,
                    s.store_name,
                    ss.quantity
                FROM
                    products p
                JOIN
                    store_stock ss ON p.product_id = ss.product_id
                JOIN
                    stores s ON ss.store_id = s.store_id
                ORDER BY
                    p.product_name;
                """
                cursor.execute(query)
                records = cursor.fetchall()

                report = pd.DataFrame(records, columns=[
                    "Product ID", "Product Name", "Store ID", "Store Name", "Quantity"
                ])
                logging.info("Generated inventory report.")
                return report
        except Error as e:
            logging.error(f"Error generating inventory report: {e}")
            raise
        finally:
            conn.close()

    def generate_supplier_report(self):
        """
        Generate a report of supplier performance and product associations.
        :return: Pandas DataFrame containing supplier report.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT
                    s.supplier_id,
                    s.supplier_name,
                    s.contact_info,
                    COUNT(sp.product_id) AS total_products
                FROM
                    suppliers s
                LEFT JOIN
                    supplier_products sp ON s.supplier_id = sp.supplier_id
                GROUP BY
                    s.supplier_id
                ORDER BY
                    total_products DESC;
                """
                cursor.execute(query)
                records = cursor.fetchall()

                report = pd.DataFrame(records, columns=[
                    "Supplier ID", "Supplier Name", "Contact Info", "Total Products"
                ])
                logging.info("Generated supplier report.")
                return report
        except Error as e:
            logging.error(f"Error generating supplier report: {e}")
            raise
        finally:
            conn.close()

    def generate_stock_movement_report(self, start_date, end_date):
        """
        Generate a report of stock movements within a given date range.
        :param start_date: Start date for the report (YYYY-MM-DD).
        :param end_date: End date for the report (YYYY-MM-DD).
        :return: Pandas DataFrame containing stock movement report.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT
                    sm.movement_id,
                    sm.product_id,
                    p.product_name,
                    sm.store_id,
                    s.store_name,
                    sm.movement_type,
                    sm.quantity,
                    sm.movement_date
                FROM
                    stock_movements sm
                JOIN
                    products p ON sm.product_id = p.product_id
                JOIN
                    stores s ON sm.store_id = s.store_id
                WHERE
                    sm.movement_date BETWEEN %s AND %s
                ORDER BY
                    sm.movement_date;
                """
                cursor.execute(query, (start_date, end_date))
                records = cursor.fetchall()

                report = pd.DataFrame(records, columns=[
                    "Movement ID", "Product ID", "Product Name", "Store ID",
                    "Store Name", "Movement Type", "Quantity", "Movement Date"
                ])
                logging.info(f"Generated stock movement report from {start_date} to {end_date}.")
                return report
        except Error as e:
            logging.error(f"Error generating stock movement report: {e}")
            raise
        finally:
            conn.close()

    def export_report_to_csv(self, report, filename):
        """
        Export a given report to a CSV file.
        :param report: Pandas DataFrame containing the report data.
        :param filename: Name of the CSV file to save.
        :return: None.
        """
        try:
            report.to_csv(filename, index=False)
            logging.info(f"Exported report to CSV file: {filename}.")
        except Exception as e:
            logging.error(f"Error exporting report to CSV: {e}")
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

    report_manager = ReportingManagement(db_config)

    # Generate inventory report
    inventory_report = report_manager.generate_inventory_report()
    print(inventory_report)

    # Generate supplier report
    supplier_report = report_manager.generate_supplier_report()
    print(supplier_report)

    # Generate stock movement report
    stock_report = report_manager.generate_stock_movement_report("2023-01-01", "2023-12-31")
    print(stock_report)

    # Export inventory report to CSV
    report_manager.export_report_to_csv(inventory_report, "inventory_report.csv")
