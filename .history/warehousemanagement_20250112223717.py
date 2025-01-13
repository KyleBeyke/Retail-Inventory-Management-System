import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="warehouse_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class WarehouseManagement:
    """
    A class to manage warehouses and their stock levels, including adding new warehouses,
    updating stock, and retrieving stock details.
    """

    def __init__(self, db_config):
        """
        Initialize the WarehouseManagement class with database connection configuration.
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

    def add_warehouse(self, warehouse_name, location):
        """
        Add a new warehouse to the database.
        :param warehouse_name: Name of the warehouse.
        :param location: Location of the warehouse.
        :return: The ID of the newly added warehouse.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO warehouses (warehouse_name, location)
                VALUES (%s, %s)
                RETURNING warehouse_id;
                """
                cursor.execute(query, (warehouse_name, location))
                warehouse_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added warehouse: {warehouse_name} with ID: {warehouse_id}.")
                return warehouse_id
        except Error as e:
            logging.error(f"Error adding warehouse {warehouse_name}: {e}")
            raise
        finally:
            conn.close()

    def get_warehouse(self, warehouse_id):
        """
        Retrieve details of a warehouse by its ID.
        :param warehouse_id: ID of the warehouse.
        :return: A dictionary containing warehouse details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT warehouse_id, warehouse_name, location
                FROM warehouses
                WHERE warehouse_id = %s;
                """
                cursor.execute(query, (warehouse_id,))
                result = cursor.fetchone()
                if result:
                    warehouse_details = {
                        "warehouse_id": result[0],
                        "warehouse_name": result[1],
                        "location": result[2]
                    }
                    logging.info(f"Retrieved warehouse details for ID: {warehouse_id}.")
                    return warehouse_details
                else:
                    logging.warning(f"No warehouse found with ID: {warehouse_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving warehouse with ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def update_warehouse(self, warehouse_id, warehouse_name=None, location=None):
        """
        Update details of an existing warehouse.
        :param warehouse_id: ID of the warehouse to update.
        :param warehouse_name: New name of the warehouse (optional).
        :param location: New location of the warehouse (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if warehouse_name:
                    fields.append("warehouse_name = %s")
                    values.append(warehouse_name)
                if location:
                    fields.append("location = %s")
                    values.append(location)

                if fields:
                    query = sql.SQL("""
                        UPDATE warehouses
                        SET {fields}
                        WHERE warehouse_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(warehouse_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated warehouse with ID: {warehouse_id}.")
                else:
                    logging.warning(f"No fields provided for updating warehouse ID: {warehouse_id}.")
        except Error as e:
            logging.error(f"Error updating warehouse with ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def add_stock(self, warehouse_id, product_id, quantity):
        """
        Add stock for a product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :param quantity: Quantity to add to the stock.
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
                logging.info(f"Added stock for product ID {product_id} in warehouse ID {warehouse_id}. Quantity: {quantity}.")
        except Error as e:
            logging.error(f"Error adding stock for product ID {product_id} in warehouse ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def get_stock(self, warehouse_id, product_id):
        """
        Retrieve stock details for a product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :return: The stock quantity.
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
                    quantity = result[0]
                    logging.info(f"Retrieved stock for product ID {product_id} in warehouse ID {warehouse_id}: {quantity}.")
                    return quantity
                else:
                    logging.warning(f"No stock found for product ID {product_id} in warehouse ID {warehouse_id}.")
                    return 0
        except Error as e:
            logging.error(f"Error retrieving stock for product ID {product_id} in warehouse ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()

    def update_stock(self, warehouse_id, product_id, quantity):
        """
        Update the stock quantity for a product in a specific warehouse.
        :param warehouse_id: ID of the warehouse.
        :param product_id: ID of the product.
        :param quantity: New quantity to set.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE warehouse_stock
                SET quantity = %s
                WHERE warehouse_id = %s AND product_id = %s;
                """
                cursor.execute(query, (quantity, warehouse_id, product_id))
                if cursor.rowcount == 0:
                    logging.warning(f"No stock record found for product ID {product_id} in warehouse ID {warehouse_id} to update.")
                else:
                    conn.commit()
                    logging.info(f"Updated stock for product ID {product_id} in warehouse ID {warehouse_id} to quantity: {quantity}.")
        except Error as e:
            logging.error(f"Error updating stock for product ID {product_id} in warehouse ID {warehouse_id}: {e}")
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

    warehouse_manager = WarehouseManagement(db_config)

    # Add a warehouse
    warehouse_id = warehouse_manager.add_warehouse("Main Warehouse", "123 Warehouse Lane")

    # Add stock
    warehouse_manager.add_stock(warehouse_id, product_id=1, quantity=50)

    # Get stock
    stock = warehouse_manager.get_stock(warehouse_id, product_id=1)
    print(f"Stock for product ID 1: {stock}")

    # Update stock
    warehouse_manager.update_stock(warehouse_id, product_id=1, quantity=100)
