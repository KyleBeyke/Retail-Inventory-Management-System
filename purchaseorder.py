import psycopg2
from psycopg2 import sql, Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="purchase_order_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class PurchaseOrder:
    """
    A class to handle operations related to purchase orders in the inventory management system.
    """

    def __init__(self, db_config):
        """
        Initialize the PurchaseOrder class with database connection configuration.
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

    def create_purchase_order(self, supplier_id, order_date=None, expected_date=None, items=None):
        """
        Create a new purchase order in the database.
        :param supplier_id: ID of the supplier associated with the purchase order.
        :param order_date: The date the order was placed (default: today).
        :param expected_date: The expected delivery date for the order (optional).
        :param items: List of tuples (product_id, quantity, unit_price) to be included in the order.
        :return: ID of the newly created purchase order.
        """
        if not items:
            raise ValueError("At least one item must be included in the purchase order.")

        order_date = order_date or datetime.now().date()

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Insert into purchase_orders table
                query_po = """
                INSERT INTO purchase_orders (supplier_id, order_date, expected_date)
                VALUES (%s, %s, %s)
                RETURNING purchase_order_id;
                """
                cursor.execute(query_po, (supplier_id, order_date, expected_date))
                purchase_order_id = cursor.fetchone()[0]

                # Insert items into purchase_order_items table
                query_items = """
                INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s);
                """
                for product_id, quantity, unit_price in items:
                    cursor.execute(query_items, (purchase_order_id, product_id, quantity, unit_price))

                conn.commit()
                logging.info(f"Purchase order created (ID: {purchase_order_id}) for supplier ID {supplier_id}.")
                return purchase_order_id
        except Error as e:
            logging.error(f"Error creating purchase order: {e}")
            raise
        finally:
            conn.close()

    def get_purchase_order_by_id(self, purchase_order_id):
        """
        Retrieve a purchase order and its items by ID.
        :param purchase_order_id: The ID of the purchase order to retrieve.
        :return: A dictionary containing purchase order details and its items, or None if not found.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Retrieve purchase order details
                query_po = """
                SELECT purchase_order_id, supplier_id, order_date, expected_date
                FROM purchase_orders
                WHERE purchase_order_id = %s;
                """
                cursor.execute(query_po, (purchase_order_id,))
                po = cursor.fetchone()

                if not po:
                    logging.warning(f"Purchase order with ID {purchase_order_id} not found.")
                    return None

                # Retrieve purchase order items
                query_items = """
                SELECT product_id, quantity, unit_price
                FROM purchase_order_items
                WHERE purchase_order_id = %s;
                """
                cursor.execute(query_items, (purchase_order_id,))
                items = cursor.fetchall()

                purchase_order = {
                    "purchase_order_id": po[0],
                    "supplier_id": po[1],
                    "order_date": po[2],
                    "expected_date": po[3],
                    "items": [
                        {"product_id": item[0], "quantity": item[1], "unit_price": item[2]} for item in items
                    ]
                }
                logging.info(f"Purchase order retrieved: {purchase_order}")
                return purchase_order
        except Error as e:
            logging.error(f"Error retrieving purchase order with ID {purchase_order_id}: {e}")
            raise
        finally:
            conn.close()

    def update_purchase_order(self, purchase_order_id, expected_date=None, items=None):
        """
        Update an existing purchase order's expected delivery date or its items.
        :param purchase_order_id: ID of the purchase order to update.
        :param expected_date: New expected delivery date (optional).
        :param items: List of tuples (product_id, quantity, unit_price) to update or add (optional).
        :return: Boolean indicating whether the update was successful.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                if expected_date:
                    # Update expected delivery date
                    query_date = """
                    UPDATE purchase_orders
                    SET expected_date = %s
                    WHERE purchase_order_id = %s;
                    """
                    cursor.execute(query_date, (expected_date, purchase_order_id))

                if items:
                    # Update items in the purchase_order_items table
                    query_items = """
                    INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (purchase_order_id, product_id)
                    DO UPDATE SET quantity = EXCLUDED.quantity, unit_price = EXCLUDED.unit_price;
                    """
                    for product_id, quantity, unit_price in items:
                        cursor.execute(query_items, (purchase_order_id, product_id, quantity, unit_price))

                conn.commit()
                logging.info(f"Purchase order updated (ID: {purchase_order_id})")
                return True
        except Error as e:
            logging.error(f"Error updating purchase order with ID {purchase_order_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_purchase_order(self, purchase_order_id):
        """
        Delete a purchase order and its items by ID.
        :param purchase_order_id: ID of the purchase order to delete.
        :return: Boolean indicating whether the deletion was successful.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Delete items first due to foreign key constraint
                query_items = """
                DELETE FROM purchase_order_items
                WHERE purchase_order_id = %s;
                """
                cursor.execute(query_items, (purchase_order_id,))

                # Delete the purchase order
                query_po = """
                DELETE FROM purchase_orders
                WHERE purchase_order_id = %s;
                """
                cursor.execute(query_po, (purchase_order_id,))

                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Purchase order deleted (ID: {purchase_order_id})")
                    return True
                else:
                    logging.warning(f"No purchase order found with ID {purchase_order_id}. Deletion failed.")
                    return False
        except Error as e:
            logging.error(f"Error deleting purchase order with ID {purchase_order_id}: {e}")
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

    po_manager = PurchaseOrder(db_config)

    # Create a new purchase order
    po_id = po_manager.create_purchase_order(
        supplier_id=1,
        items=[(1, 10, 20.5), (2, 5, 15.0)],
        expected_date="2025-01-20"
    )

    # Retrieve the purchase order
    purchase_order = po_manager.get_purchase_order_by_id(po_id)
    print(purchase_order)

    # Update the purchase order
    po_manager.update_purchase_order(po_id, expected_date="2025-01-25", items=[(1, 15, 21.0)])

    # Delete the purchase order
    po_manager.delete_purchase_order(po_id)
