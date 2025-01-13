import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="store_stock_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class StoreStockManagement:
    """
    A class to manage stock levels of products across different stores.
    """

    def __init__(self, db_config):
        """
        Initialize the StoreStockManagement class with database connection configuration.
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

    def add_stock(self, store_id, product_id, quantity):
        """
        Add stock for a specific product at a specific store after validating the inputs.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: Quantity of stock to add.
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        DataValidationManagement.validate_positive_integer(quantity, "Quantity")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO store_stock (store_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (store_id, product_id)
                DO UPDATE SET quantity = store_stock.quantity + EXCLUDED.quantity;
                """
                cursor.execute(query, (store_id, product_id, quantity))
                conn.commit()
                logging.info(f"Added {quantity} units of product ID {product_id} to store ID {store_id}.")
        except Error as e:
            logging.error(f"Error adding stock for product ID {product_id} at store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_stock(self, store_id, product_id):
        """
        Retrieve stock details for a specific product at a specific store after validating inputs.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :return: A dictionary containing stock details.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT store_id, product_id, quantity
                FROM store_stock
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (store_id, product_id))
                result = cursor.fetchone()
                if result:
                    stock_details = {
                        "store_id": result[0],
                        "product_id": result[1],
                        "quantity": result[2],
                    }
                    logging.info(f"Retrieved stock details for product ID {product_id} at store ID {store_id}.")
                    return stock_details
                else:
                    logging.warning(f"No stock found for product ID {product_id} at store ID {store_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving stock for product ID {product_id} at store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def update_stock(self, store_id, product_id, quantity):
        """
        Update stock quantity for a specific product at a specific store after validating inputs.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: New stock quantity.
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        DataValidationManagement.validate_non_negative_integer(quantity, "Quantity")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE store_stock
                SET quantity = %s
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (quantity, store_id, product_id))
                if cursor.rowcount == 0:
                    logging.warning(f"No stock record found to update for product ID {product_id} at store ID {store_id}.")
                else:
                    conn.commit()
                    logging.info(f"Updated stock for product ID {product_id} at store ID {store_id} to {quantity}.")
        except Error as e:
            logging.error(f"Error updating stock for product ID {product_id} at store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_stock(self, store_id, product_id):
        """
        Delete stock entry for a specific product at a specific store after validating inputs.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM store_stock
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (store_id, product_id))
                if cursor.rowcount == 0:
                    logging.warning(f"No stock record found to delete for product ID {product_id} at store ID {store_id}.")
                else:
                    conn.commit()
                    logging.info(f"Deleted stock for product ID {product_id} at store ID {store_id}.")
        except Error as e:
            logging.error(f"Error deleting stock for product ID {product_id} at store ID {store_id}: {e}")
            raise
        finally:
            conn.close()
