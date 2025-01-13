import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="product_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class ProductManagement:
    """
    A class to manage product information, including adding, updating, retrieving,
    and deleting products in the inventory system.
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

    def add_product(self, product_name, sku, price, description=None):
        """
        Add a new product to the database after validating the inputs.
        :param product_name: Name of the product.
        :param sku: Stock Keeping Unit (SKU) of the product.
        :param price: Price of the product.
        :param description: Description of the product (optional).
        :return: The ID of the newly added product.
        """
        # Validate inputs
        DataValidationManagement.validate_non_empty_string(product_name, "Product Name")
        DataValidationManagement.validate_non_empty_string(sku, "SKU")
        DataValidationManagement.validate_positive_number(price, "Price")

        if description:
            DataValidationManagement.validate_non_empty_string(description, "Description")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO products (product_name, sku, price, description)
                VALUES (%s, %s, %s, %s)
                RETURNING product_id;
                """
                cursor.execute(query, (product_name, sku, price, description))
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
        Retrieve details of a product by its ID after validating the ID.
        :param product_id: ID of the product.
        :return: A dictionary containing product details.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT product_id, product_name, sku, price, description
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
                        "price": result[3],
                        "description": result[4]
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

    def update_product(self, product_id, product_name=None, sku=None, price=None, description=None):
        """
        Update details of an existing product after validating inputs.
        :param product_id: ID of the product to update.
        :param product_name: New name of the product (optional).
        :param sku: New SKU of the product (optional).
        :param price: New price of the product (optional).
        :param description: New description of the product (optional).
        :return: None.
        """
        # Validate inputs
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")
        if product_name:
            DataValidationManagement.validate_non_empty_string(product_name, "Product Name")
        if sku:
            DataValidationManagement.validate_non_empty_string(sku, "SKU")
        if price is not None:
            DataValidationManagement.validate_positive_number(price, "Price")
        if description:
            DataValidationManagement.validate_non_empty_string(description, "Description")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if product_name:
                    fields.append("product_name = %s")
                    values.append(product_name)
                if sku:
                    fields.append("sku = %s")
                    values.append(sku)
                if price is not None:
                    fields.append("price = %s")
                    values.append(price)
                if description:
                    fields.append("description = %s")
                    values.append(description)

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
        Delete a product from the database after validating the ID.
        :param product_id: ID of the product to delete.
        :return: None.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(product_id, "Product ID")

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
