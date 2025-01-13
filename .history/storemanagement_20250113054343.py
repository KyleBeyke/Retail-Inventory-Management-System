from psycopg2 import sql
from psycopg2.extensions import connection
from DataValidationManagement import DataValidationManagement
import logging


class StoreManagement:
    """
    Manages store-related operations, including adding, updating, deleting, and retrieving store details.
    """

    def __init__(self, db_connection: connection):
        """
        Initializes the StoreManagement class.

        :param db_connection: A psycopg2 database connection object.
        """
        self.db_connection = db_connection
        self.data_validator = DataValidationManagement()

    def add_store(self, store_name: str, location: str):
        """
        Adds a new store to the stores table.

        :param store_name: Name of the store.
        :param location: Location of the store.
        :return: None
        """
        try:
            # Validate inputs
            self.data_validator.validate_non_empty_string(store_name, "store_name")
            self.data_validator.validate_non_empty_string(location, "location")

            # Insert the store into the database
            query = sql.SQL(
                """
                INSERT INTO stores (store_name, location)
                VALUES (%s, %s)
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (store_name, location))
                self.db_connection.commit()

            logging.info(f"Store added: {store_name} at {location}.")
        except Exception as e:
            logging.error(f"Failed to add store '{store_name}': {e}")
            raise

    def update_store(self, store_id: int, store_name: str = None, location: str = None):
        """
        Updates an existing store's details.

        :param store_id: ID of the store to update.
        :param store_name: (Optional) New name of the store.
        :param location: (Optional) New location of the store.
        :return: None
        """
        try:
            # Validate store ID
            self.data_validator.validate_positive_integer(store_id, "store_id")
            self.validate_store_exists(store_id)

            # Prepare update fields
            update_fields = []
            params = []
            if store_name:
                self.data_validator.validate_non_empty_string(store_name, "store_name")
                update_fields.append("store_name = %s")
                params.append(store_name)
            if location:
                self.data_validator.validate_non_empty_string(location, "location")
                update_fields.append("location = %s")
                params.append(location)

            if not update_fields:
                raise ValueError("No valid fields provided for update.")

            # Build and execute update query
            query = sql.SQL(
                f"""
                UPDATE stores
                SET {', '.join(update_fields)}
                WHERE store_id = %s
                """
            )
            params.append(store_id)
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                self.db_connection.commit()

            logging.info(f"Store ID {store_id} updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update store ID {store_id}: {e}")
            raise

    def delete_store(self, store_id: int):
        """
        Deletes a store from the stores table.

        :param store_id: ID of the store to delete.
        :return: None
        """
        try:
            # Validate store ID
            self.data_validator.validate_positive_integer(store_id, "store_id")
            self.validate_store_exists(store_id)

            # Delete the store
            query = sql.SQL("DELETE FROM stores WHERE store_id = %s")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (store_id,))
                self.db_connection.commit()

            logging.info(f"Store ID {store_id} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete store ID {store_id}: {e}")
            raise

    def retrieve_stores(self):
        """
        Retrieves all stores from the stores table.

        :return: A list of dictionaries containing store details.
        """
        try:
            query = sql.SQL("SELECT * FROM stores ORDER BY store_id ASC")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query)
                stores = cursor.fetchall()

            store_list = [
                {
                    "store_id": store[0],
                    "store_name": store[1],
                    "location": store[2]
                }
                for store in stores
            ]

            logging.info("Retrieved all stores.")
            return store_list
        except Exception as e:
            logging.error(f"Failed to retrieve stores: {e}")
            raise

    def validate_store_exists(self, store_id: int):
        """
        Validates the existence of a store in the stores table.

        :param store_id: ID of the store to validate.
        :return: None
        """
        try:
            query = sql.SQL("SELECT 1 FROM stores WHERE store_id = %s")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (store_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Store ID {store_id} does not exist.")
        except Exception as e:
            logging.error(f"Store validation failed for store ID {store_id}: {e}")
            raise
