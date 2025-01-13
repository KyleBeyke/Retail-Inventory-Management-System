import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="warehouse_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class WarehouseManagement:
    """
    A class to manage warehouse information, including adding, updating,
    retrieving, and deleting warehouse details.
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

    def add_warehouse(self, warehouse_name, location, capacity):
        """
        Add a new warehouse to the database after validating the inputs.
        :param warehouse_name: Name of the warehouse.
        :param location: Location of the warehouse.
        :param capacity: Maximum capacity of the warehouse.
        :return: The ID of the newly added warehouse.
        """
        # Validate inputs
        DataValidationManagement.validate_non_empty_string(warehouse_name, "Warehouse Name")
        DataValidationManagement.validate_non_empty_string(location, "Location")
        DataValidationManagement.validate_positive_number(capacity, "Capacity")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO warehouses (warehouse_name, location, capacity)
                VALUES (%s, %s, %s)
                RETURNING warehouse_id;
                """
                cursor.execute(query, (warehouse_name, location, capacity))
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
        Retrieve details of a warehouse by its ID after validating the ID.
        :param warehouse_id: ID of the warehouse.
        :return: A dictionary containing warehouse details.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(warehouse_id, "Warehouse ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT warehouse_id, warehouse_name, location, capacity
                FROM warehouses
                WHERE warehouse_id = %s;
                """
                cursor.execute(query, (warehouse_id,))
                result = cursor.fetchone()
                if result:
                    warehouse_details = {
                        "warehouse_id": result[0],
                        "warehouse_name": result[1],
                        "location": result[2],
                        "capacity": result[3],
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

    def update_warehouse(self, warehouse_id, warehouse_name=None, location=None, capacity=None):
        """
        Update details of an existing warehouse after validating inputs.
        :param warehouse_id: ID of the warehouse to update.
        :param warehouse_name: New name of the warehouse (optional).
        :param location: New location of the warehouse (optional).
        :param capacity: New capacity of the warehouse (optional).
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(warehouse_id, "Warehouse ID")
        if warehouse_name:
            DataValidationManagement.validate_non_empty_string(warehouse_name, "Warehouse Name")
        if location:
            DataValidationManagement.validate_non_empty_string(location, "Location")
        if capacity is not None:
            DataValidationManagement.validate_positive_number(capacity, "Capacity")

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
                if capacity is not None:
                    fields.append("capacity = %s")
                    values.append(capacity)

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

    def delete_warehouse(self, warehouse_id):
        """
        Delete a warehouse from the database after validating the ID.
        :param warehouse_id: ID of the warehouse to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(warehouse_id, "Warehouse ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM warehouses
                WHERE warehouse_id = %s;
                """
                cursor.execute(query, (warehouse_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No warehouse found with ID: {warehouse_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted warehouse with ID: {warehouse_id}.")
        except Error as e:
            logging.error(f"Error deleting warehouse with ID {warehouse_id}: {e}")
            raise
        finally:
            conn.close()
