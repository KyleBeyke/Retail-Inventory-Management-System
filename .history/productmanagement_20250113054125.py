from psycopg2 import sql
from psycopg2.extensions import connection
from DataValidationManagement import DataValidationManagement
import logging


class ProductManagement:
    """
    Manages product-related operations, including adding, updating, and deleting products,
    and ensuring relationships with categories, suppliers, and stock.
    """

    def __init__(self, db_connection: connection):
        """
        Initializes the ProductManagement class.

        :param db_connection: A psycopg2 database connection object.
        """
        self.db_connection = db_connection
        self.data_validator = DataValidationManagement()

    def add_product(self, product_name: str, category_id: int, supplier_id: int, price: float, stock_quantity: int):
        """
        Adds a new product to the products table and updates stock.

        :param product_name: Name of the product.
        :param category_id: ID of the product's category.
        :param supplier_id: ID of the product's supplier.
        :param price: Price of the product.
        :param stock_quantity: Initial stock quantity for the product.
        :return: None
        """
        try:
            # Validate inputs
            self.data_validator.validate_non_empty_string(product_name, "product_name")
            self.data_validator.validate_positive_integer(category_id, "category_id")
            self.data_validator.validate_positive_integer(supplier_id, "supplier_id")
            self.data_validator.validate_positive_float(price, "price")
            self.data_validator.validate_non_negative_integer(stock_quantity, "stock_quantity")

            # Validate category and supplier existence
            self.validate_category_and_supplier(category_id, supplier_id)

            # Insert the product into the products table
            query = sql.SQL(
                """
                INSERT INTO products (product_name, category_id, supplier_id, price)
                VALUES (%s, %s, %s, %s)
                RETURNING product_id
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (product_name, category_id, supplier_id, price))
                product_id = cursor.fetchone()[0]
                self.db_connection.commit()

            # Update stock in the store_stock table
            stock_query = sql.SQL(
                """
                INSERT INTO store_stock (store_id, product_id, quantity)
                SELECT store_id, %s, %s FROM stores
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(stock_query, (product_id, stock_quantity))
                self.db_connection.commit()

            logging.info(f"Product added: {product_name} (ID: {product_id}) with initial stock {stock_quantity}.")
        except Exception as e:
            logging.error(f"Failed to add product '{product_name}': {e}")
            raise

    def update_product(self, product_id: int, product_name: str = None, category_id: int = None,
                       supplier_id: int = None, price: float = None):
        """
        Updates an existing product's details.

        :param product_id: ID of the product to update.
        :param product_name: (Optional) New name of the product.
        :param category_id: (Optional) New category ID of the product.
        :param supplier_id: (Optional) New supplier ID of the product.
        :param price: (Optional) New price of the product.
        :return: None
        """
        try:
            # Validate product existence
            self.data_validator.validate_positive_integer(product_id, "product_id")
            self.validate_product_exists(product_id)

            # Prepare update fields
            update_fields = []
            params = []
            if product_name:
                self.data_validator.validate_non_empty_string(product_name, "product_name")
                update_fields.append("product_name = %s")
                params.append(product_name)
            if category_id:
                self.data_validator.validate_positive_integer(category_id, "category_id")
                self.validate_category_exists(category_id)
                update_fields.append("category_id = %s")
                params.append(category_id)
            if supplier_id:
                self.data_validator.validate_positive_integer(supplier_id, "supplier_id")
                self.validate_supplier_exists(supplier_id)
                update_fields.append("supplier_id = %s")
                params.append(supplier_id)
            if price is not None:
                self.data_validator.validate_positive_float(price, "price")
                update_fields.append("price = %s")
                params.append(price)

            if not update_fields:
                raise ValueError("No valid fields provided for update.")

            # Build and execute update query
            query = sql.SQL(
                f"""
                UPDATE products
                SET {', '.join(update_fields)}
                WHERE product_id = %s
                """
            )
            params.append(product_id)
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, tuple(params))
                self.db_connection.commit()

            logging.info(f"Product ID {product_id} updated successfully.")
        except Exception as e:
            logging.error(f"Failed to update product ID {product_id}: {e}")
            raise

    def delete_product(self, product_id: int):
        """
        Deletes a product from the products table.

        :param product_id: ID of the product to delete.
        :return: None
        """
        try:
            self.data_validator.validate_positive_integer(product_id, "product_id")
            self.validate_product_exists(product_id)

            # Delete the product
            query = sql.SQL("DELETE FROM products WHERE product_id = %s")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (product_id,))
                self.db_connection.commit()

            logging.info(f"Product ID {product_id} deleted successfully.")
        except Exception as e:
            logging.error(f"Failed to delete product ID {product_id}: {e}")
            raise

    def validate_category_and_supplier(self, category_id: int, supplier_id: int):
        """
        Validates the existence of a category and supplier in their respective tables.

        :param category_id: ID of the category to validate.
        :param supplier_id: ID of the supplier to validate.
        :return: None
        """
        try:
            category_query = sql.SQL("SELECT 1 FROM categories WHERE category_id = %s")
            supplier_query = sql.SQL("SELECT 1 FROM suppliers WHERE supplier_id = %s")

            with self.db_connection.cursor() as cursor:
                cursor.execute(category_query, (category_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Category ID {category_id} does not exist.")

                cursor.execute(supplier_query, (supplier_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Supplier ID {supplier_id} does not exist.")
        except Exception as e:
            logging.error(f"Validation failed for category ID {category_id} and supplier ID {supplier_id}: {e}")
            raise

    def validate_product_exists(self, product_id: int):
        """
        Validates the existence of a product in the products table.

        :param product_id: ID of the product to validate.
        :return: None
        """
        try:
            query = sql.SQL("SELECT 1 FROM products WHERE product_id = %s")
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (product_id,))
                if cursor.fetchone() is None:
                    raise ValueError(f"Product ID {product_id} does not exist.")
        except Exception as e:
            logging.error(f"Product validation failed for product ID {product_id}: {e}")
            raise
