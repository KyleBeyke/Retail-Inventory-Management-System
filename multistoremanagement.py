import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="multi_store_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class MultiStoreManagement:
    """
    A class to manage multiple stores, including adding new stores,
    retrieving store details, and listing all stores.
    """

    def __init__(self, db_config):
        """
        Initialize the MultiStoreManagement class with database connection configuration.
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

    def add_store(self, store_name, location, contact_number=None, store_type="Retail"):
        """
        Add a new store to the database.
        :param store_name: Name of the store.
        :param location: Address or location of the store.
        :param contact_number: Contact number of the store (optional).
        :param store_type: Type of store (e.g., 'Retail', 'Warehouse'). Defaults to 'Retail'.
        :return: The ID of the newly added store.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO stores (store_name, location, contact_number, store_type)
                VALUES (%s, %s, %s, %s)
                RETURNING store_id;
                """
                cursor.execute(query, (store_name, location, contact_number, store_type))
                store_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added new store: {store_name} with ID: {store_id}.")
                return store_id
        except Error as e:
            logging.error(f"Error adding store {store_name}: {e}")
            raise
        finally:
            conn.close()

    def get_store(self, store_id):
        """
        Retrieve details of a specific store by its ID.
        :param store_id: The ID of the store to retrieve.
        :return: A dictionary containing store details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT store_id, store_name, location, contact_number, store_type, created_at
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
                        "contact_number": result[3],
                        "store_type": result[4],
                        "created_at": result[5]
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

    def update_store(self, store_id, store_name=None, location=None, contact_number=None, store_type=None):
        """
        Update details of an existing store.
        :param store_id: ID of the store to update.
        :param store_name: New name of the store (optional).
        :param location: New location or address (optional).
        :param contact_number: New contact number (optional).
        :param store_type: New type of the store (optional).
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
                if contact_number:
                    fields.append("contact_number = %s")
                    values.append(contact_number)
                if store_type:
                    fields.append("store_type = %s")
                    values.append(store_type)

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

    def list_stores(self, store_type_filter=None):
        """
        List all stores with an optional filter for store type.
        :param store_type_filter: Filter stores by type (e.g., 'Retail', 'Warehouse').
        :return: A list of dictionaries containing store details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                if store_type_filter:
                    query = """
                    SELECT store_id, store_name, location, contact_number, store_type, created_at
                    FROM stores
                    WHERE store_type = %s
                    ORDER BY created_at DESC;
                    """
                    cursor.execute(query, (store_type_filter,))
                else:
                    query = """
                    SELECT store_id, store_name, location, contact_number, store_type, created_at
                    FROM stores
                    ORDER BY created_at DESC;
                    """
                    cursor.execute(query)
                results = cursor.fetchall()
                store_list = [
                    {
                        "store_id": row[0],
                        "store_name": row[1],
                        "location": row[2],
                        "contact_number": row[3],
                        "store_type": row[4],
                        "created_at": row[5]
                    }
                    for row in results
                ]
                logging.info("Retrieved list of stores.")
                return store_list
        except Error as e:
            logging.error(f"Error listing stores: {e}")
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

    store_manager = MultiStoreManagement(db_config)

    # Add a store
    store_id = store_manager.add_store("Downtown Store", "123 Main St", contact_number="555-1234")

    # Get store details
    details = store_manager.get_store(store_id)
    print(details)

    # Update store details
    store_manager.update_store(store_id, location="456 Elm St")

    # List all stores
    all_stores = store_manager.list_stores()
    print("All Stores:", all_stores)

    # Delete the store
    store_manager.delete_store(store_id)
