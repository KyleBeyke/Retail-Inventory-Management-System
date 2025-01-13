from psycopg2 import sql
from psycopg2.extensions import connection
from datetime import datetime
from DataValidationManagement import DataValidationManagement
import logging


class StoreSalesManagement:
    """
    Manages store sales, including adding sales, generating reports, and stock adjustments.
    """

    def __init__(self, db_connection: connection):
        """
        Initializes the StoreSalesManagement class.

        :param db_connection: A psycopg2 database connection object.
        """
        self.db_connection = db_connection
        self.data_validator = DataValidationManagement()

    def validate_store_and_product(self, store_id, product_id):
        """
        Validates that the store_id and product_id exist in the respective tables.

        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :return: None
        :raises ValueError: If the store or product does not exist.
        """
        try:
            # Validate store existence
            store_query = sql.SQL("SELECT 1 FROM stores WHERE store_id = %s")
            product_query = sql.SQL("SELECT 1 FROM products WHERE product_id = %s")

            with self.db_connection.cursor() as cursor:
                cursor.execute(store_query, (store_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Store ID {store_id} does not exist.")

                cursor.execute(product_query, (product_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Product ID {product_id} does not exist.")
        except Exception as e:
            logging.error(f"Validation failed for store_id={store_id}, product_id={product_id}: {e}")
            raise

    def add_sale(self, store_id: int, product_id: int, quantity: int, sale_price: float, sale_date: datetime = None):
        """
        Records a sale in the store_sales table and adjusts stock levels in the store_stock table.

        :param store_id: ID of the store where the sale occurred.
        :param product_id: ID of the product sold.
        :param quantity: Quantity of the product sold.
        :param sale_price: Sale price of the product.
        :param sale_date: Date of the sale. Defaults to the current date.
        :return: None
        """
        try:
            # Validate inputs
            self.data_validator.validate_positive_integer(store_id, "store_id")
            self.data_validator.validate_positive_integer(product_id, "product_id")
            self.data_validator.validate_positive_integer(quantity, "quantity")
            self.data_validator.validate_positive_float(sale_price, "sale_price")
            sale_date = sale_date or datetime.now()

            # Validate existence of store and product
            self.validate_store_and_product(store_id, product_id)

            # Check stock availability
            stock_query = sql.SQL("SELECT quantity FROM store_stock WHERE store_id = %s AND product_id = %s")
            with self.db_connection.cursor() as cursor:
                cursor.execute(stock_query, (store_id, product_id))
                stock_result = cursor.fetchone()
                if not stock_result or stock_result[0] < quantity:
                    raise ValueError(f"Insufficient stock for product ID {product_id} in store ID {store_id}.")

            # Insert the sale into store_sales
            sale_query = sql.SQL(
                """
                INSERT INTO store_sales (store_id, product_id, quantity, sale_price, sale_date)
                VALUES (%s, %s, %s, %s, %s)
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(sale_query, (store_id, product_id, quantity, sale_price, sale_date))
                self.db_connection.commit()

            # Update stock in store_stock
            update_stock_query = sql.SQL(
                "UPDATE store_stock SET quantity = quantity - %s WHERE store_id = %s AND product_id = %s"
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(update_stock_query, (quantity, store_id, product_id))
                self.db_connection.commit()

            logging.info(f"Sale added: Store ID {store_id}, Product ID {product_id}, Quantity {quantity}.")
        except Exception as e:
            logging.error(f"Failed to add sale: {e}")
            raise

    def generate_sales_report(self, store_id: int, start_date: datetime, end_date: datetime):
        """
        Generates a sales report for a given store and date range.

        :param store_id: ID of the store.
        :param start_date: Start date for the report.
        :param end_date: End date for the report.
        :return: List of sales records.
        """
        try:
            # Validate inputs
            self.data_validator.validate_positive_integer(store_id, "store_id")
            self.data_validator.validate_date_range(start_date, end_date)

            # Generate the report
            report_query = sql.SQL(
                """
                SELECT sale_id, product_id, quantity, sale_price, sale_date
                FROM store_sales
                WHERE store_id = %s AND sale_date BETWEEN %s AND %s
                ORDER BY sale_date ASC
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(report_query, (store_id, start_date, end_date))
                report = cursor.fetchall()

            logging.info(f"Sales report generated for Store ID {store_id} from {start_date} to {end_date}.")
            return report
        except Exception as e:
            logging.error(f"Failed to generate sales report: {e}")
            raise

# Example usage (to be removed in production):
if __name__ == "__main__":
    try:
        from psycopg2 import connect
        connection = connect(
            dbname="inventory_db",
            user="inventory_user",
            password="inventory_pass",
            host="localhost",
            port=5432
        )

        sales_manager = StoreSalesManagement(connection)

        # Add a sale
        sales_manager.add_sale(store_id=1, product_id=101, quantity=2, sale_price=19.99)

        # Generate a report
        report = sales_manager.generate_sales_report(store_id=1, start_date="2025-01-01", end_date="2025-01-31")
        for row in report:
            print(row)

    except Exception as e:
        logging.error(f"Error: {e}")
