import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="store_stock_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class StoreStockManagement:
    """
    A class to manage stock levels of products in stores, including adding, updating,
    retrieving, and transferring stock between stores.
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
        Add stock for a product in a specific store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: Quantity of stock to add.
        :return: None.
        """
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
            logging.error(f"Error adding stock for product ID {product_id} in store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def update_stock(self, store_id, product_id, new_quantity):
        """
        Update the stock quantity of a product in a store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param new_quantity: New stock quantity to set.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE store_stock
                SET quantity = %s
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (new_quantity, store_id, product_id))
                conn.commit()
                logging.info(f"Updated stock for product ID {product_id} in store ID {store_id} to {new_quantity} units.")
        except Error as e:
            logging.error(f"Error updating stock for product ID {product_id} in store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_stock(self, store_id, product_id):
        """
        Retrieve the stock quantity of a product in a store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :return: Stock quantity (int) or None if not found.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT quantity
                FROM store_stock
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (store_id, product_id))
                result = cursor.fetchone()
                if result:
                    logging.info(f"Retrieved stock for product ID {product_id} in store ID {store_id}: {result[0]} units.")
                    return result[0]
                else:
                    logging.warning(f"No stock found for product ID {product_id} in store ID {store_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving stock for product ID {product_id} in store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def transfer_stock(self, from_store_id, to_store_id, product_id, quantity):
        """
        Transfer stock of a product from one store to another.
        :param from_store_id: ID of the source store.
        :param to_store_id: ID of the destination store.
        :param product_id: ID of the product.
        :param quantity: Quantity of stock to transfer.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Check if source store has sufficient stock
                check_query = """
                SELECT quantity
                FROM store_stock
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(check_query, (from_store_id, product_id))
                result = cursor.fetchone()
                if not result or result[0] < quantity:
                    logging.warning(f"Insufficient stock in store ID {from_store_id} for product ID {product_id}.")
                    raise ValueError("Insufficient stock in source store.")

                # Deduct stock from source store
                deduct_query = """
                UPDATE store_stock
                SET quantity = quantity - %s
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(deduct_query, (quantity, from_store_id, product_id))

                # Add stock to destination store
                add_query = """
                INSERT INTO store_stock (store_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (store_id, product_id)
                DO UPDATE SET quantity = store_stock.quantity + EXCLUDED.quantity;
                """
                cursor.execute(add_query, (to_store_id, product_id, quantity))

                conn.commit()
                logging.info(f"Transferred {quantity} units of product ID {product_id} from store ID {from_store_id} to store ID {to_store_id}.")
        except Error as e:
            logging.error(f"Error transferring stock for product ID {product_id} from store ID {from_store_id} to store ID {to_store_id}: {e}")
            raise
        finally:
            conn.close()

# Example usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    stock_manager = StoreStockManagement(db_config)

    # Add stock
    stock_manager.add_stock(store_id=1, product_id=101, quantity=50)

    # Update stock
    stock_manager.update_stock(store_id=1, product_id=101, new_quantity=100)

    # Get stock
    quantity = stock_manager.get_stock(store_id=1, product_id=101)
    print(f"Stock quantity: {quantity}")

    # Transfer stock
    stock_manager.transfer_stock(from_store_id=1, to_store_id=2, product_id=101, quantity=20)
