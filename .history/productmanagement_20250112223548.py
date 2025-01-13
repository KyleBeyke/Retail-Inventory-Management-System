import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="product_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ProductManagement:
    """
    A class to manage product information, including adding, retrieving,
    updating, and deleting products. Handles product classification into departments,
    classes, and subclasses.
    """

    def __init__(self, db_config):
        """
        Initialize the ProductManagement class with database connection configuration.
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

    def add_product(self, product_name, sku, department_id, class_id, subclass_id, price, description=None):
        """
        Add a new product to the database.
        :param product_name: Name of the product.
        :param sku: Stock Keeping Unit (unique identifier for the product).
        :param department_id: Department ID the product belongs to.
        :param class_id: Class ID the product belongs to.
        :param subclass_id: Subclass ID the product belongs to.
        :param price: Price of the product.
        :param description: Optional description of the product.
        :return: The ID of the newly added product.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO products (product_name, sku, department_id, class_id, subclass_id, price, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING product_id;
                """
                cursor.execute(query, (product_name, sku, department_id, class_id, subclass_id, price, description))
                product_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added product: {product_name} with ID: {product_id}.")
                return product_id
        except Error as e:
            logging.error(f"Error adding product {product_name}: {e}")
            raise
        finally:
            conn.close()

    def get_product(self, product_id):
        """
        Retrieve details of a product by its ID.
        :param product_id: ID of the product.
        :return: A dictionary containing product details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT product_id, product_name, sku, department_id, class_id, subclass_id, price, description
                FROM products
                WHERE product_id = %s;
                """
                cursor.execute(query, (product_id,))
                result = cursor.fetchone()
                if result:
                    product_details = {
                        "product_id": result[0],
                        "product_name": result[1],
                        "sku": result[2],
                        "department_id": result[3],
                        "class_id": result[4],
                        "subclass_id": result[5],
                        "price": result[6],
                        "description": result[7],
                    }
                    logging.info(f"Retrieved product details for ID: {product_id}.")
                    return product_details
                else:
                    logging.warning(f"No product found with ID: {product_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving product with ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def update_product(self, product_id, **kwargs):
        """
        Update details of an existing product.
        :param product_id: ID of the product to update.
        :param kwargs: Fields to update, such as product_name, sku, price, description, etc.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                for key, value in kwargs.items():
                    fields.append(f"{key} = %s")
                    values.append(value)

                if fields:
                    query = sql.SQL("""
                        UPDATE products
                        SET {fields}
                        WHERE product_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(product_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated product with ID: {product_id}.")
                else:
                    logging.warning(f"No fields provided for updating product ID: {product_id}.")
        except Error as e:
            logging.error(f"Error updating product with ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_product(self, product_id):
        """
        Delete a product from the database.
        :param product_id: ID of the product to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM products
                WHERE product_id = %s;
                """
                cursor.execute(query, (product_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No product found with ID: {product_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted product with ID: {product_id}.")
        except Error as e:
            logging.error(f"Error deleting product with ID {product_id}: {e}")
            raise
        finally:
            conn.close()

    def assign_classification(self, product_id, department_id=None, class_id=None, subclass_id=None):
        """
        Assign or update the classification of a product.
        :param product_id: ID of the product.
        :param department_id: New department ID (optional).
        :param class_id: New class ID (optional).
        :param subclass_id: New subclass ID (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if department_id is not None:
                    fields.append("department_id = %s")
                    values.append(department_id)
                if class_id is not None:
                    fields.append("class_id = %s")
                    values.append(class_id)
                if subclass_id is not None:
                    fields.append("subclass_id = %s")
                    values.append(subclass_id)

                if fields:
                    query = sql.SQL("""
                        UPDATE products
                        SET {fields}
                        WHERE product_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(product_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated classification for product ID: {product_id}.")
                else:
                    logging.warning(f"No classification fields provided for product ID: {product_id}.")
        except Error as e:
            logging.error(f"Error assigning classification for product ID {product_id}: {e}")
            raise
        finally:
            conn.close()

# Example usage:
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    product_manager = ProductManagement(db_config)

    # Add a product
    product_id = product_manager.add_product("T-Shirt", "SKU12345", 1, 2, 3, 19.99, "High-quality cotton t-shirt.")

    # Get product details
    details = product_manager.get_product(product_id)
    print(details)

    # Update product details
    product_manager.update_product(product_id, price=17.99)

    # Assign new classification
    product_manager.assign_classification(product_id, department_id=2)

    # Delete the product
    product_manager.delete_product(product_id)
