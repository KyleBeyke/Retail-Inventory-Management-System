import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="store_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class StoreManagement:
    """
    A class to manage stores, including adding stores, retrieving store details,
    managing stock levels at specific stores, and associating warehouses.
    """

    def __init__(self, db_config):
        """
        Initialize the StoreManagement class with database connection configuration.
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

    def add_store(self, store_name, location, contact_info):
        """
        Add a new store to the database.
        :param store_name: Name of the store.
        :param location: Location of the store (e.g., address).
        :param contact_info: Contact information for the store.
        :return: The ID of the newly added store.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO stores (store_name, location, contact_info)
                VALUES (%s, %s, %s)
                RETURNING store_id;
                """
                cursor.execute(query, (store_name, location, contact_info))
                store_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added store: {store_name} with ID: {store_id}.")
                return store_id
        except Error as e:
            logging.error(f"Error adding store {store_name}: {e}")
            raise
        finally:
            conn.close()

    def get_store(self, store_id):
        """
        Retrieve details of a store by its ID.
        :param store_id: ID of the store.
        :return: A dictionary containing store details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT store_id, store_name, location, contact_info
                FROM stores
                WHERE store_id = %s;
                """
                cursor.execute(query, (store_id,))
                result = cursor.fetchone()
                if result:
                    store_details = {
                        "store_id": result[0],
                        "store_name": result[1],
                        "location": result[2],
                        "contact_info": result[3]
                    }
                    logging.info(f"Retrieved store details for ID: {store_id}.")
                    return store_details
                else:
                    logging.warning(f"No store found with ID: {store_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving store with ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def update_store(self, store_id, store_name=None, location=None, contact_info=None):
        """
        Update details of an existing store.
        :param store_id: ID of the store to update.
        :param store_name: New name of the store (optional).
        :param location: New location of the store (optional).
        :param contact_info: New contact information for the store (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if store_name:
                    fields.append("store_name = %s")
                    values.append(store_name)
                if location:
                    fields.append("location = %s")
                    values.append(location)
                if contact_info:
                    fields.append("contact_info = %s")
                    values.append(contact_info)

                if fields:
                    query = sql.SQL("""
                        UPDATE stores
                        SET {fields}
                        WHERE store_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(store_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated store with ID: {store_id}.")
                else:
                    logging.warning(f"No fields provided for updating store ID: {store_id}.")
        except Error as e:
            logging.error(f"Error updating store with ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_store(self, store_id):
        """
        Delete a store from the database.
        :param store_id: ID of the store to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM stores
                WHERE store_id = %s;
                """
                cursor.execute(query, (store_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No store found with ID: {store_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted store with ID: {store_id}.")
        except Error as e:
            logging.error(f"Error deleting store with ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def manage_store_stock(self, store_id, product_id, quantity):
        """
        Update stock levels for a product at a specific store.
        :param store_id: ID of the store.
        :param product_id: ID of the product.
        :param quantity: New quantity of the product at the store.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO store_stock (store_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON CONFLICT (store_id, product_id)
                DO UPDATE SET quantity = EXCLUDED.quantity;
                """
                cursor.execute(query, (store_id, product_id, quantity))
                conn.commit()
                logging.info(f"Updated stock for product ID {product_id} at store ID {store_id} to {quantity}.")
        except Error as e:
            logging.error(f"Error managing stock for product ID {product_id} at store ID {store_id}: {e}")
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

    store_manager = StoreManagement(db_config)

    # Add a store
    store_id = store_manager.add_store("Downtown Store", "123 Main St, Nashville, TN", "555-1234")

    # Get store details
    details = store_manager.get_store(store_id)
    print(details)

    # Update store details
    store_manager.update_store(store_id, contact_info="555-5678")

    # Manage stock for a product at the store
    store_manager.manage_store_stock(store_id, product_id=2001, quantity=150)

    # Delete the store
    store_manager.delete_store(store_id)
