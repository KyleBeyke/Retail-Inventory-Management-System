import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="warehouse_stock_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class WarehouseStockManagement:
    """
    A class to manage stock levels in warehouses, including adding stock,
    retrieving stock information, and transferring stock between warehouses.
    """

    def __init__(self, db_config):
        """
        Initialize the WarehouseStockManagement class with database connection configuration.
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

    def add_stock(self, warehouse_id, product_id, quantity):
        """
        Add stock for a specific product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :param quantity: Quantity of the product to add.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO warehouse_stock (warehouse_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (warehouse_id, product_id)
                DO UPDATE SET quantity = warehouse_stock.quantity + EXCLUDED.quantity;
                """
                cursor.execute(query, (warehouse_id, product_id, quantity))
                conn.commit()
                logging.info(f"Added {quantity} units of product ID {product_id} to warehouse ID {warehouse_id}.")
        except Error as e:
            logging.error(f"Error adding stock to warehouse ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def remove_stock(self, warehouse_id, product_id, quantity):
        """
        Remove stock for a specific product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :param quantity: Quantity of the product to remove.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Ensure sufficient stock before removing
                cursor.execute("""
                SELECT quantity FROM warehouse_stock
                WHERE warehouse_id = %s AND product_id = %s;
                """, (warehouse_id, product_id))
                result = cursor.fetchone()
                if result and result[0] >= quantity:
                    query = """
                    UPDATE warehouse_stock
                    SET quantity = quantity - %s
                    WHERE warehouse_id = %s AND product_id = %s;
                    """
                    cursor.execute(query, (quantity, warehouse_id, product_id))
                    conn.commit()
                    logging.info(f"Removed {quantity} units of product ID {product_id} from warehouse ID {warehouse_id}.")
                else:
                    logging.warning(f"Insufficient stock for product ID {product_id} in warehouse ID {warehouse_id}.")
                    raise ValueError("Insufficient stock to complete the operation.")
        except Error as e:
            logging.error(f"Error removing stock from warehouse ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def get_stock(self, warehouse_id, product_id):
        """
        Retrieve stock levels for a specific product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :return: Quantity of the product in stock.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT quantity
                FROM warehouse_stock
                WHERE warehouse_id = %s AND product_id = %s;
                """
                cursor.execute(query, (warehouse_id, product_id))
                result = cursor.fetchone()
                if result:
                    logging.info(f"Retrieved stock level for product ID {product_id} in warehouse ID {warehouse_id}: {result[0]} units.")
                    return result[0]
                else:
                    logging.warning(f"No stock record found for product ID {product_id} in warehouse ID {warehouse_id}.")
                    return 0
        except Error as e:
            logging.error(f"Error retrieving stock for product ID {product_id} in warehouse ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def transfer_stock(self, source_warehouse_id, target_warehouse_id, product_id, quantity):
        """
        Transfer stock of a specific product between warehouses.
        :param source_warehouse_id: ID of the source warehouse.
        :param target_warehouse_id: ID of the target warehouse.
        :param product_id: ID of the product.
        :param quantity: Quantity of the product to transfer.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Ensure sufficient stock in the source warehouse
                cursor.execute("""
                SELECT quantity FROM warehouse_stock
                WHERE warehouse_id = %s AND product_id = %s;
                """, (source_warehouse_id, product_id))
                result = cursor.fetchone()
                if result and result[0] >= quantity:
                    # Deduct stock from source warehouse
                    cursor.execute("""
                    UPDATE warehouse_stock
                    SET quantity = quantity - %s
                    WHERE warehouse_id = %s AND product_id = %s;
                    """, (quantity, source_warehouse_id, product_id))

                    # Add stock to target warehouse
                    cursor.execute("""
                    INSERT INTO warehouse_stock (warehouse_id, product_id, quantity)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (warehouse_id, product_id)
                    DO UPDATE SET quantity = warehouse_stock.quantity + EXCLUDED.quantity;
                    """, (target_warehouse_id, product_id, quantity))

                    conn.commit()
                    logging.info(f"Transferred {quantity} units of product ID {product_id} from warehouse ID {source_warehouse_id} to warehouse ID {target_warehouse_id}.")
                else:
                    logging.warning(f"Insufficient stock in source warehouse ID {source_warehouse_id} for product ID {product_id}.")
                    raise ValueError("Insufficient stock to complete the transfer.")
        except Error as e:
            logging.error(f"Error transferring stock for product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

# Example Usage
if __name__ == "__main__":
    # Database configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    warehouse_stock_manager = WarehouseStockManagement(db_config)

    # Add stock to a warehouse
    warehouse_stock_manager.add_stock(warehouse_id=1, product_id=101, quantity=50)

    # Get stock levels
    stock_level = warehouse_stock_manager.get_stock(warehouse_id=1, product_id=101)
    print(f"Stock level: {stock_level}")

    # Transfer stock between warehouses
    warehouse_stock_manager.transfer_stock(source_warehouse_id=1, target_warehouse_id=2, product_id=101, quantity=20)

    # Remove stock from a warehouse
    warehouse_stock_manager.remove_stock(warehouse_id=1, product_id=101, quantity=10)
