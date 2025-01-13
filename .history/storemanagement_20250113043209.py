import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="store_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class StoreManagement:
    """
    A class to manage store information, including adding, updating,
    retrieving, and deleting store details.
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

    def add_store(self, store_name, location, phone_number=None):
        """
        Add a new store to the database after validating the inputs.
        :param store_name: Name of the store.
        :param location: Location of the store.
        :param phone_number: Phone number of the store (optional).
        :return: The ID of the newly added store.
        """
        # Validate inputs
        DataValidationManagement.validate_non_empty_string(store_name, "Store Name")
        DataValidationManagement.validate_non_empty_string(location, "Location")
        if phone_number:
            DataValidationManagement.validate_phone_number(phone_number, "Phone Number")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO stores (store_name, location, phone_number)
                VALUES (%s, %s, %s)
                RETURNING store_id;
                """
                cursor.execute(query, (store_name, location, phone_number))
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
        Retrieve details of a store by its ID after validating the ID.
        :param store_id: ID of the store.
        :return: A dictionary containing store details.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT store_id, store_name, location, phone_number
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
                        "phone_number": result[3],
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

    def update_store(self, store_id, store_name=None, location=None, phone_number=None):
        """
        Update details of an existing store after validating inputs.
        :param store_id: ID of the store to update.
        :param store_name: New name of the store (optional).
        :param location: New location of the store (optional).
        :param phone_number: New phone number of the store (optional).
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")
        if store_name:
            DataValidationManagement.validate_non_empty_string(store_name, "Store Name")
        if location:
            DataValidationManagement.validate_non_empty_string(location, "Location")
        if phone_number:
            DataValidationManagement.validate_phone_number(phone_number, "Phone Number")

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
                if phone_number:
                    fields.append("phone_number = %s")
                    values.append(phone_number)

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
        Delete a store from the database after validating the ID.
        :param store_id: ID of the store to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(store_id, "Store ID")

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
