import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="store_sales_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class StoreSalesManagement:
    """
    A class to manage sales transactions and records for stores.
    """

    def __init__(self, db_config):
        """
        Initialize the StoreSalesManagement class with database connection configuration.
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

    def record_sale(self, store_id, product_id, quantity, sale_price):
        """
        Record a sale transaction for a specific product at a store after validating inputs.
        :param store_id: ID of the store where the sale occurred.
        :param product_id: ID of the product sold.
        :param quantity: Quantity of the product sold.
        :param sale_price: Sale price per unit of the product.
        :return: The ID of the recorded sale transaction.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        DataValidationManagement.validate_positive_integer(quantity, "Quantity")
        DataValidationManagement.validate_positive_float(sale_price, "Sale Price")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Deduct stock before recording the sale
                stock_query = """
                UPDATE store_stock
                SET quantity = quantity - %s
                WHERE store_id = %s AND product_id = %s AND quantity >= %s;
                """
                cursor.execute(stock_query, (quantity, store_id, product_id, quantity))

                if cursor.rowcount == 0:
                    logging.warning(f"Insufficient stock for product ID {product_id} at store ID {store_id}.")
                    raise ValueError("Insufficient stock to complete the sale.")

                # Record the sale
                sale_query = """
                INSERT INTO store_sales (store_id, product_id, quantity, sale_price, total_price)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING sale_id;
                """
                total_price = quantity * sale_price
                cursor.execute(sale_query, (store_id, product_id, quantity, sale_price, total_price))
                sale_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Recorded sale: Sale ID {sale_id}, Store ID {store_id}, Product ID {product_id}.")
                return sale_id
        except Error as e:
            logging.error(f"Error recording sale for product ID {product_id} at store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_sales_by_store(self, store_id):
        """
        Retrieve all sales records for a specific store after validating the store ID.
        :param store_id: ID of the store.
        :return: A list of dictionaries containing sales records.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT sale_id, product_id, quantity, sale_price, total_price, sale_date
                FROM store_sales
                WHERE store_id = %s;
                """
                cursor.execute(query, (store_id,))
                results = cursor.fetchall()
                sales_records = [
                    {
                        "sale_id": row[0],
                        "product_id": row[1],
                        "quantity": row[2],
                        "sale_price": row[3],
                        "total_price": row[4],
                        "sale_date": row[5],
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(sales_records)} sales records for store ID {store_id}.")
                return sales_records
        except Error as e:
            logging.error(f"Error retrieving sales for store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_sales_by_product(self, product_id):
        """
        Retrieve all sales records for a specific product across all stores after validating the product ID.
        :param product_id: ID of the product.
        :return: A list of dictionaries containing sales records.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT sale_id, store_id, quantity, sale_price, total_price, sale_date
                FROM store_sales
                WHERE product_id = %s;
                """
                cursor.execute(query, (product_id,))
                results = cursor.fetchall()
                sales_records = [
                    {
                        "sale_id": row[0],
                        "store_id": row[1],
                        "quantity": row[2],
                        "sale_price": row[3],
                        "total_price": row[4],
                        "sale_date": row[5],
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(sales_records)} sales records for product ID {product_id}.")
                return sales_records
        except Error as e:
            logging.error(f"Error retrieving sales for product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_sale(self, sale_id):
        """
        Delete a sale transaction from the database after validating the sale ID.
        :param sale_id: ID of the sale transaction to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(sale_id, "Sale ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM store_sales
                WHERE sale_id = %s;
                """
                cursor.execute(query, (sale_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No sale record found with ID {sale_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted sale record with ID {sale_id}.")
        except Error as e:
            logging.error(f"Error deleting sale record with ID {sale_id}: {e}")
            raise
        finally:
            conn.close()
