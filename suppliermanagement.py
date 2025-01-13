import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="supplier_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SupplierManagement:
    """
    A class to manage supplier information, including adding suppliers,
    retrieving supplier details, and managing supplier-product relationships.
    """

    def __init__(self, db_config):
        """
        Initialize the SupplierManagement class with database connection configuration.
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

    def add_supplier(self, supplier_name, contact_info, address):
        """
        Add a new supplier to the database.
        :param supplier_name: Name of the supplier.
        :param contact_info: Contact information of the supplier (e.g., email, phone).
        :param address: Address of the supplier.
        :return: The ID of the newly added supplier.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO suppliers (supplier_name, contact_info, address)
                VALUES (%s, %s, %s)
                RETURNING supplier_id;
                """
                cursor.execute(query, (supplier_name, contact_info, address))
                supplier_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added supplier: {supplier_name} with ID: {supplier_id}.")
                return supplier_id
        except Error as e:
            logging.error(f"Error adding supplier {supplier_name}: {e}")
            raise
        finally:
            conn.close()

    def get_supplier(self, supplier_id):
        """
        Retrieve details of a supplier by their ID.
        :param supplier_id: ID of the supplier.
        :return: A dictionary containing supplier details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT supplier_id, supplier_name, contact_info, address
                FROM suppliers
                WHERE supplier_id = %s;
                """
                cursor.execute(query, (supplier_id,))
                result = cursor.fetchone()
                if result:
                    supplier_details = {
                        "supplier_id": result[0],
                        "supplier_name": result[1],
                        "contact_info": result[2],
                        "address": result[3]
                    }
                    logging.info(f"Retrieved supplier details for ID: {supplier_id}.")
                    return supplier_details
                else:
                    logging.warning(f"No supplier found with ID: {supplier_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving supplier with ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def update_supplier(self, supplier_id, supplier_name=None, contact_info=None, address=None):
        """
        Update details of an existing supplier.
        :param supplier_id: ID of the supplier to update.
        :param supplier_name: New name of the supplier (optional).
        :param contact_info: New contact information (optional).
        :param address: New address (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if supplier_name:
                    fields.append("supplier_name = %s")
                    values.append(supplier_name)
                if contact_info:
                    fields.append("contact_info = %s")
                    values.append(contact_info)
                if address:
                    fields.append("address = %s")
                    values.append(address)

                if fields:
                    query = sql.SQL("""
                        UPDATE suppliers
                        SET {fields}
                        WHERE supplier_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(supplier_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated supplier with ID: {supplier_id}.")
                else:
                    logging.warning(f"No fields provided for updating supplier ID: {supplier_id}.")
        except Error as e:
            logging.error(f"Error updating supplier with ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_supplier(self, supplier_id):
        """
        Delete a supplier from the database.
        :param supplier_id: ID of the supplier to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM suppliers
                WHERE supplier_id = %s;
                """
                cursor.execute(query, (supplier_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No supplier found with ID: {supplier_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted supplier with ID: {supplier_id}.")
        except Error as e:
            logging.error(f"Error deleting supplier with ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def add_supplier_product(self, supplier_id, product_id):
        """
        Link a product to a supplier.
        :param supplier_id: ID of the supplier.
        :param product_id: ID of the product.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO supplier_products (supplier_id, product_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
                """
                cursor.execute(query, (supplier_id, product_id))
                conn.commit()
                logging.info(f"Linked product ID {product_id} to supplier ID {supplier_id}.")
        except Error as e:
            logging.error(f"Error linking product ID {product_id} to supplier ID {supplier_id}: {e}")
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

    supplier_manager = SupplierManagement(db_config)

    # Add a supplier
    supplier_id = supplier_manager.add_supplier("Acme Corp", "acme@example.com", "123 Acme St")

    # Get supplier details
    details = supplier_manager.get_supplier(supplier_id)
    print(details)

    # Update supplier details
    supplier_manager.update_supplier(supplier_id, contact_info="newemail@example.com")

    # Link a product to the supplier
    supplier_manager.add_supplier_product(supplier_id, product_id=101)

    # Delete the supplier
    supplier_manager.delete_supplier(supplier_id)
