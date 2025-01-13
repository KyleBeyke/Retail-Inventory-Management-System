import psycopg2
from psycopg2.extras import RealDictCursor
import logging

class Product:
    """
    Represents a product in the inventory management system.
    Handles all operations related to products, including CRUD (Create, Read, Update, Delete).
    """

    def __init__(self, db_config):
        """
        Initialize the Product class with database connection settings.

        :param db_config: A dictionary containing database connection parameters.
        Example:
        {
            'dbname': 'inventory_db',
            'user': 'inventory_user',
            'password': 'inventory_pass',
            'host': 'localhost',
            'port': '5432'
        }
        """
        self.db_config = db_config

        # Configure logging
        logging.basicConfig(
            filename='app.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _connect(self):
        """
        Establish a connection to the database.
        :return: A database connection object.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def create_product(self, name, sku, description, category_id=None, supplier_id=None):
        """
        Create a new product in the database.

        :param name: Name of the product.
        :param sku: Stock Keeping Unit (unique identifier for the product).
        :param description: Description of the product.
        :param category_id: (Optional) ID of the product's category.
        :param supplier_id: (Optional) ID of the product's supplier.
        :return: The ID of the newly created product.
        """
        query = """
        INSERT INTO products (name, sku, description, category_id, supplier_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING product_id;
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, (name, sku, description, category_id, supplier_id))
            product_id = cursor.fetchone()[0]
            conn.commit()
            logging.info(f"Product created: {name} (ID: {product_id})")
            return product_id
        except psycopg2.Error as e:
            logging.error(f"Error creating product: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def get_product_by_id(self, product_id):
        """
        Retrieve a product by its ID.

        :param product_id: The ID of the product to retrieve.
        :return: A dictionary representing the product, or None if not found.
        """
        query = """
        SELECT * FROM products WHERE product_id = %s;
        """
        try:
            conn = self._connect()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, (product_id,))
            product = cursor.fetchone()
            logging.info(f"Product retrieved: {product_id}")
            return product
        except psycopg2.Error as e:
            logging.error(f"Error retrieving product: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def update_product(self, product_id, name=None, sku=None, description=None, category_id=None, supplier_id=None):
        """
        Update an existing product's details.

        :param product_id: The ID of the product to update.
        :param name: (Optional) New name of the product.
        :param sku: (Optional) New SKU of the product.
        :param description: (Optional) New description of the product.
        :param category_id: (Optional) New category ID of the product.
        :param supplier_id: (Optional) New supplier ID of the product.
        """
        query = """
        UPDATE products
        SET name = COALESCE(%s, name),
            sku = COALESCE(%s, sku),
            description = COALESCE(%s, description),
            category_id = COALESCE(%s, category_id),
            supplier_id = COALESCE(%s, supplier_id)
        WHERE product_id = %s;
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, (name, sku, description, category_id, supplier_id, product_id))
            conn.commit()
            logging.info(f"Product updated: {product_id}")
        except psycopg2.Error as e:
            logging.error(f"Error updating product: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

    def delete_product(self, product_id):
        """
        Delete a product from the database.

        :param product_id: The ID of the product to delete.
        """
        query = """
        DELETE FROM products WHERE product_id = %s;
        """
        try:
            conn = self._connect()
            cursor = conn.cursor()
            cursor.execute(query, (product_id,))
            conn.commit()
            logging.info(f"Product deleted: {product_id}")
        except psycopg2.Error as e:
            logging.error(f"Error deleting product: {e}")
            raise
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    # Example usage
    db_config = {
        'dbname': 'inventory_db',
        'user': 'inventory_user',
        'password': 'inventory_pass',
        'host': 'localhost',
        'port': '5432'
    }

    product_manager = Product(db_config)

    # Create a new product
    product_id = product_manager.create_product(
        name="Example Product",
        sku="EX123",
        description="An example product description.",
        category_id=1,
        supplier_id=1
    )

    # Retrieve the product
    product = product_manager.get_product_by_id(product_id)
    print(product)

    # Update the product
    product_manager.update_product(product_id, name="Updated Product Name")

    # Delete the product
    product_manager.delete_product(product_id)