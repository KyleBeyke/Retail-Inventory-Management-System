import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="store_inventory_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class StoreInventory:
    """
    A class to manage store inventory operations, including stock levels and warehouse transfers.
    """

    def __init__(self, db_config):
        """
        Initialize the StoreInventory class with database connection configuration.
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
        Add stock for a specific product in a store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: Quantity to add.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO store_stock (store_id, product_id, stock_level)
                VALUES (%s, %s, %s)
                ON CONFLICT (store_id, product_id)
                DO UPDATE SET stock_level = store_stock.stock_level + EXCLUDED.stock_level;
                """
                cursor.execute(query, (store_id, product_id, quantity))
                conn.commit()
                logging.info(f"Added {quantity} units of product ID {product_id} to store ID {store_id}.")
        except Error as e:
            logging.error(f"Error adding stock for store ID {store_id} and product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def reduce_stock(self, store_id, product_id, quantity):
        """
        Reduce stock for a specific product in a store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: Quantity to reduce.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE store_stock
                SET stock_level = stock_level - %s
                WHERE store_id = %s AND product_id = %s AND stock_level >= %s;
                """
                cursor.execute(query, (quantity, store_id, product_id, quantity))
                if cursor.rowcount == 0:
                    logging.warning(f"Insufficient stock for product ID {product_id} in store ID {store_id}.")
                    raise ValueError("Insufficient stock to reduce.")
                conn.commit()
                logging.info(f"Reduced {quantity} units of product ID {product_id} from store ID {store_id}.")
        except Error as e:
            logging.error(f"Error reducing stock for store ID {store_id} and product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def transfer_stock(self, source_store_id, target_store_id, product_id, quantity):
        """
        Transfer stock of a product from one store to another.
        :param source_store_id: ID of the source store.
        :param target_store_id: ID of the target store.
        :param product_id: ID of the product.
        :param quantity: Quantity to transfer.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Reduce stock from source store
                query_reduce = """
                UPDATE store_stock
                SET stock_level = stock_level - %s
                WHERE store_id = %s AND product_id = %s AND stock_level >= %s;
                """
                cursor.execute(query_reduce, (quantity, source_store_id, product_id, quantity))
                if cursor.rowcount == 0:
                    logging.warning(f"Insufficient stock for product ID {product_id} in source store ID {source_store_id}.")
                    raise ValueError("Insufficient stock to transfer.")

                # Add stock to target store
                query_add = """
                INSERT INTO store_stock (store_id, product_id, stock_level)
                VALUES (%s, %s, %s)
                ON CONFLICT (store_id, product_id)
                DO UPDATE SET stock_level = store_stock.stock_level + EXCLUDED.stock_level;
                """
                cursor.execute(query_add, (target_store_id, product_id, quantity))

                conn.commit()
                logging.info(f"Transferred {quantity} units of product ID {product_id} from store ID {source_store_id} to store ID {target_store_id}.")
        except Error as e:
            logging.error(f"Error transferring stock for product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def get_stock_level(self, store_id, product_id):
        """
        Retrieve the stock level of a specific product in a store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :return: The current stock level.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT stock_level
                FROM store_stock
                WHERE store_id = %s AND product_id = %s;
                """
                cursor.execute(query, (store_id, product_id))
                result = cursor.fetchone()
                if result:
                    stock_level = result[0]
                    logging.info(f"Stock level for product ID {product_id} in store ID {store_id}: {stock_level}")
                    return stock_level
                else:
                    logging.warning(f"No stock record found for product ID {product_id} in store ID {store_id}.")
                    return 0
        except Error as e:
            logging.error(f"Error retrieving stock level for store ID {store_id} and product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

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

    inventory_manager = StoreInventory(db_config)

    # Add stock to a store
    inventory_manager.add_stock(store_id=1, product_id=101, quantity=50)

    # Reduce stock in a store
    inventory_manager.reduce_stock(store_id=1, product_id=101, quantity=10)

    # Transfer stock between stores
    inventory_manager.transfer_stock(source_store_id=1, target_store_id=2, product_id=101, quantity=20)

    # Get stock level for a product in a store
    stock_level = inventory_manager.get_stock_level(store_id=1, product_id=101)
    print(f"Stock Level: {stock_level}")
