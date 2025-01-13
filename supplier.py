import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="supplier_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Supplier:
    """
    A class to handle operations related to suppliers in the inventory management system.
    """

    def __init__(self, db_config):
        """
        Initialize the Supplier class with database connection configuration.
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

    def create_supplier(self, name, contact_email, phone=None, address=None):
        """
        Create a new supplier in the database.

        :param name: Name of the supplier.
        :param contact_email: Email address of the supplier.
        :param phone: Optional phone number of the supplier.
        :param address: Optional address of the supplier.
        :return: ID of the newly created supplier.
        """
        query = """
        INSERT INTO suppliers (name, contact_email, phone, address)
        VALUES (%s, %s, %s, %s)
        RETURNING supplier_id;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (name, contact_email, phone, address))
                supplier_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Supplier created: {name} (ID: {supplier_id})")
                return supplier_id
        except Error as e:
            logging.error(f"Error creating supplier '{name}': {e}")
            raise
        finally:
            conn.close()

    def get_supplier_by_id(self, supplier_id):
        """
        Retrieve a supplier by its ID.

        :param supplier_id: The ID of the supplier to retrieve.
        :return: A dictionary containing the supplier details or None if not found.
        """
        query = """
        SELECT supplier_id, name, contact_email, phone, address
        FROM suppliers
        WHERE supplier_id = %s;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (supplier_id,))
                result = cursor.fetchone()
                if result:
                    supplier = {
                        "supplier_id": result[0],
                        "name": result[1],
                        "contact_email": result[2],
                        "phone": result[3],
                        "address": result[4]
                    }
                    logging.info(f"Supplier retrieved: {supplier}")
                    return supplier
                else:
                    logging.warning(f"Supplier with ID {supplier_id} not found.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving supplier with ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def update_supplier(self, supplier_id, name=None, contact_email=None, phone=None, address=None):
        """
        Update an existing supplier's details.

        :param supplier_id: ID of the supplier to update.
        :param name: New name for the supplier (optional).
        :param contact_email: New contact email for the supplier (optional).
        :param phone: New phone number for the supplier (optional).
        :param address: New address for the supplier (optional).
        :return: Boolean indicating whether the update was successful.
        """
        updates = []
        values = []

        if name:
            updates.append("name = %s")
            values.append(name)
        if contact_email:
            updates.append("contact_email = %s")
            values.append(contact_email)
        if phone:
            updates.append("phone = %s")
            values.append(phone)
        if address:
            updates.append("address = %s")
            values.append(address)

        if not updates:
            logging.warning("No fields provided to update.")
            return False

        query = sql.SQL("UPDATE suppliers SET {fields} WHERE supplier_id = %s").format(
            fields=sql.SQL(", ").join(map(sql.SQL, updates))
        )
        values.append(supplier_id)

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Supplier updated (ID: {supplier_id})")
                    return True
                else:
                    logging.warning(f"No supplier found with ID {supplier_id}. Update failed.")
                    return False
        except Error as e:
            logging.error(f"Error updating supplier with ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_supplier(self, supplier_id):
        """
        Delete a supplier by its ID.

        :param supplier_id: ID of the supplier to delete.
        :return: Boolean indicating whether the deletion was successful.
        """
        query = """
        DELETE FROM suppliers
        WHERE supplier_id = %s;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (supplier_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Supplier deleted (ID: {supplier_id})")
                    return True
                else:
                    logging.warning(f"No supplier found with ID {supplier_id}. Deletion failed.")
                    return False
        except Error as e:
            logging.error(f"Error deleting supplier with ID {supplier_id}: {e}")
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

    supplier_manager = Supplier(db_config)

    # Create a new supplier
    new_supplier_id = supplier_manager.create_supplier(
        name="Example Supplier",
        contact_email="supplier@example.com",
        phone="123-456-7890",
        address="123 Example Street, Nashville, TN"
    )

    # Retrieve the newly created supplier
    supplier = supplier_manager.get_supplier_by_id(new_supplier_id)
    print(supplier)

    # Update the supplier
    supplier_manager.update_supplier(new_supplier_id, phone="987-654-3210")

    # Delete the supplier
    supplier_manager.delete_supplier(new_supplier_id)
