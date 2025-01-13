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

class PurchaseOrderManagement:
    """
    A class to manage purchase orders (POs), including creation, updating,
    retrieval, and tracking of purchase orders and their statuses.
    """

    def __init__(self, db_config):
        """
        Initialize the PurchaseOrderManagement class with database connection configuration.
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

    def create_purchase_order(self, supplier_id, order_date, expected_delivery_date, items):
        """
        Create a new purchase order and add items to it.
        :param supplier_id: ID of the supplier for the PO.
        :param order_date: Date when the PO was created.
        :param expected_delivery_date: Expected delivery date for the PO.
        :param items: List of dictionaries containing 'product_id' and 'quantity'.
        :return: The ID of the newly created purchase order.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Insert into purchase_orders table
                query_po = """
                INSERT INTO purchase_orders (supplier_id, order_date, expected_delivery_date, status)
                VALUES (%s, %s, %s, %s)
                RETURNING po_id;
                """
                cursor.execute(query_po, (supplier_id, order_date, expected_delivery_date, 'Pending'))
                po_id = cursor.fetchone()[0]

                # Insert items into purchase_order_items table
                query_items = """
                INSERT INTO purchase_order_items (po_id, product_id, quantity)
                VALUES (%s, %s, %s);
                """
                for item in items:
                    cursor.execute(query_items, (po_id, item['product_id'], item['quantity']))

                conn.commit()
                logging.info(f"Created purchase order {po_id} for supplier ID {supplier_id}.")
                return po_id
        except Error as e:
            logging.error(f"Error creating purchase order: {e}")
            raise
        finally:
            conn.close()

    def get_purchase_order(self, po_id):
        """
        Retrieve details of a purchase order and its items.
        :param po_id: ID of the purchase order.
        :return: Dictionary containing purchase order details and items.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Retrieve PO details
                query_po = """
                SELECT po_id, supplier_id, order_date, expected_delivery_date, status
                FROM purchase_orders
                WHERE po_id = %s;
                """
                cursor.execute(query_po, (po_id,))
                po_details = cursor.fetchone()
                if not po_details:
                    logging.warning(f"No purchase order found with ID {po_id}.")
                    return None

                # Retrieve PO items
                query_items = """
                SELECT product_id, quantity
                FROM purchase_order_items
                WHERE po_id = %s;
                """
                cursor.execute(query_items, (po_id,))
                items = cursor.fetchall()

                purchase_order = {
                    "po_id": po_details[0],
                    "supplier_id": po_details[1],
                    "order_date": po_details[2],
                    "expected_delivery_date": po_details[3],
                    "status": po_details[4],
                    "items": [{"product_id": item[0], "quantity": item[1]} for item in items]
                }
                logging.info(f"Retrieved details for purchase order ID {po_id}.")
                return purchase_order
        except Error as e:
            logging.error(f"Error retrieving purchase order {po_id}: {e}")
            raise
        finally:
            conn.close()

    def update_purchase_order_status(self, po_id, new_status):
        """
        Update the status of a purchase order.
        :param po_id: ID of the purchase order to update.
        :param new_status: New status of the purchase order (e.g., 'Pending', 'Completed', 'Cancelled').
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE purchase_orders
                SET status = %s
                WHERE po_id = %s;
                """
                cursor.execute(query, (new_status, po_id))
                if cursor.rowcount == 0:
                    logging.warning(f"No purchase order found with ID {po_id} to update.")
                else:
                    conn.commit()
                    logging.info(f"Updated status for purchase order ID {po_id} to '{new_status}'.")
        except Error as e:
            logging.error(f"Error updating status for purchase order {po_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_purchase_order(self, po_id):
        """
        Delete a purchase order and its items from the database.
        :param po_id: ID of the purchase order to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Delete PO items
                query_items = """
                DELETE FROM purchase_order_items
                WHERE po_id = %s;
                """
                cursor.execute(query_items, (po_id,))

                # Delete PO
                query_po = """
                DELETE FROM purchase_orders
                WHERE po_id = %s;
                """
                cursor.execute(query_po, (po_id,))

                if cursor.rowcount == 0:
                    logging.warning(f"No purchase order found with ID {po_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted purchase order ID {po_id}.")
        except Error as e:
            logging.error(f"Error deleting purchase order {po_id}: {e}")
            raise
        finally:
            conn.close()

# Example Usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    po_manager = PurchaseOrderManagement(db_config)

    # Create a new purchase order
    po_id = po_manager.create_purchase_order(
        supplier_id=1,
        order_date=datetime.now(),
        expected_delivery_date=datetime(2025, 1, 31),
        items=[{"product_id": 101, "quantity": 50}, {"product_id": 102, "quantity": 30}]
    )

    # Retrieve purchase order details
    details = po_manager.get_purchase_order(po_id)
    print(details)

    # Update purchase order status
    po_manager.update_purchase_order_status(po_id, "Completed")

    # Delete the purchase order
    po_manager.delete_purchase_order(po_id)
