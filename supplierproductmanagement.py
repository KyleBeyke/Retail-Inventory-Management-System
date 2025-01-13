import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="supplier_product_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SupplierProductManagement:
    """
    A class to manage the relationships between suppliers and products, including linking suppliers
    to products, retrieving linked products, and unlinking products.
    """

    def __init__(self, db_config):
        """
        Initialize the SupplierProductManagement class with database connection configuration.
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

    def link_supplier_to_product(self, supplier_id, product_id):
        """
        Link a supplier to a product.
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

    def get_products_by_supplier(self, supplier_id):
        """
        Retrieve all products linked to a given supplier.
        :param supplier_id: ID of the supplier.
        :return: A list of dictionaries containing product details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT p.product_id, p.product_name, p.description, p.price
                FROM products p
                JOIN supplier_products sp ON p.product_id = sp.product_id
                WHERE sp.supplier_id = %s;
                """
                cursor.execute(query, (supplier_id,))
                results = cursor.fetchall()
                products = [
                    {
                        "product_id": row[0],
                        "product_name": row[1],
                        "description": row[2],
                        "price": row[3]
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(products)} products for supplier ID {supplier_id}.")
                return products
        except Error as e:
            logging.error(f"Error retrieving products for supplier ID {supplier_id}: {e}")
            raise
        finally:
            conn.close()

    def get_suppliers_by_product(self, product_id):
        """
        Retrieve all suppliers linked to a given product.
        :param product_id: ID of the product.
        :return: A list of dictionaries containing supplier details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT s.supplier_id, s.supplier_name, s.contact_info, s.address
                FROM suppliers s
                JOIN supplier_products sp ON s.supplier_id = sp.supplier_id
                WHERE sp.product_id = %s;
                """
                cursor.execute(query, (product_id,))
                results = cursor.fetchall()
                suppliers = [
                    {
                        "supplier_id": row[0],
                        "supplier_name": row[1],
                        "contact_info": row[2],
                        "address": row[3]
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(suppliers)} suppliers for product ID {product_id}.")
                return suppliers
        except Error as e:
            logging.error(f"Error retrieving suppliers for product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def unlink_supplier_from_product(self, supplier_id, product_id):
        """
        Unlink a supplier from a product.
        :param supplier_id: ID of the supplier.
        :param product_id: ID of the product.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM supplier_products
                WHERE supplier_id = %s AND product_id = %s;
                """
                cursor.execute(query, (supplier_id, product_id))
                if cursor.rowcount == 0:
                    logging.warning(f"No link found between supplier ID {supplier_id} and product ID {product_id}.")
                else:
                    conn.commit()
                    logging.info(f"Unlinked product ID {product_id} from supplier ID {supplier_id}.")
        except Error as e:
            logging.error(f"Error unlinking product ID {product_id} from supplier ID {supplier_id}: {e}")
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

    supplier_product_manager = SupplierProductManagement(db_config)

    # Link a supplier to a product
    supplier_product_manager.link_supplier_to_product(supplier_id=1, product_id=101)

    # Get products by supplier
    products = supplier_product_manager.get_products_by_supplier(supplier_id=1)
    print(products)

    # Get suppliers by product
    suppliers = supplier_product_manager.get_suppliers_by_product(product_id=101)
    print(suppliers)

    # Unlink a supplier from a product
    supplier_product_manager.unlink_supplier_from_product(supplier_id=1, product_id=101)
