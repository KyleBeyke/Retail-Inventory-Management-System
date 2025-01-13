import psycopg2
from psycopg2 import sql, Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="data_synchronization.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class DataSynchronizationManagement:
    """
    A class to manage data synchronization between the local inventory system
    and external systems, such as WooCommerce or third-party POS systems.
    """

    def __init__(self, db_config, external_api_client):
        """
        Initialize the DataSynchronizationManagement class.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        :param external_api_client: A client object for interacting with external APIs (e.g., WooCommerce API).
        """
        self.db_config = db_config
        self.external_api_client = external_api_client

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

    def synchronize_products_to_external(self):
        """
        Synchronize local product data to an external system (e.g., WooCommerce).
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT product_id, product_name, sku, price, stock_quantity
                FROM products;
                """
                cursor.execute(query)
                products = cursor.fetchall()

                for product in products:
                    product_data = {
                        "id": product[0],
                        "name": product[1],
                        "sku": product[2],
                        "price": product[3],
                        "stock_quantity": product[4],
                    }

                    # Send product data to the external system
                    response = self.external_api_client.send_product_data(product_data)
                    if response.get("success"):
                        logging.info(f"Synchronized product ID {product[0]} to external system.")
                    else:
                        logging.error(
                            f"Failed to synchronize product ID {product[0]}: {response.get('error')}"
                        )
        except Error as e:
            logging.error(f"Error during product synchronization: {e}")
            raise
        finally:
            conn.close()

    def synchronize_stock_to_external(self):
        """
        Synchronize stock levels from local inventory to an external system.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT product_id, stock_quantity
                FROM store_stock;
                """
                cursor.execute(query)
                stock_data = cursor.fetchall()

                for stock in stock_data:
                    stock_update = {
                        "product_id": stock[0],
                        "stock_quantity": stock[1],
                    }

                    # Send stock data to the external system
                    response = self.external_api_client.update_stock(stock_update)
                    if response.get("success"):
                        logging.info(f"Synchronized stock for product ID {stock[0]} to external system.")
                    else:
                        logging.error(
                            f"Failed to synchronize stock for product ID {stock[0]}: {response.get('error')}"
                        )
        except Error as e:
            logging.error(f"Error during stock synchronization: {e}")
            raise
        finally:
            conn.close()

    def synchronize_orders_from_external(self):
        """
        Synchronize orders from an external system to the local database.
        """
        try:
            # Fetch orders from the external system
            orders = self.external_api_client.get_orders()

            if not orders:
                logging.info("No new orders to synchronize.")
                return

            conn = self._connect()
            with conn.cursor() as cursor:
                for order in orders:
                    try:
                        query = """
                        INSERT INTO orders (order_id, customer_name, order_date, total_amount, status)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (order_id) DO NOTHING;
                        """
                        cursor.execute(query, (
                            order["id"],
                            order["customer_name"],
                            datetime.strptime(order["order_date"], "%Y-%m-%dT%H:%M:%S"),
                            order["total_amount"],
                            order["status"],
                        ))

                        # Insert order items
                        for item in order["items"]:
                            item_query = """
                            INSERT INTO order_items (order_id, product_id, quantity, price)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT DO NOTHING;
                            """
                            cursor.execute(item_query, (
                                order["id"],
                                item["product_id"],
                                item["quantity"],
                                item["price"],
                            ))

                        logging.info(f"Synchronized order ID {order['id']} from external system.")
                    except Error as e:
                        logging.error(f"Error synchronizing order ID {order['id']}: {e}")

                conn.commit()
        except Error as e:
            logging.error(f"Error during order synchronization: {e}")
            raise
        finally:
            conn.close()

    def synchronize_suppliers_to_external(self):
        """
        Synchronize supplier data to an external system, if required.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT supplier_id, supplier_name, contact_info, address
                FROM suppliers;
                """
                cursor.execute(query)
                suppliers = cursor.fetchall()

                for supplier in suppliers:
                    supplier_data = {
                        "id": supplier[0],
                        "name": supplier[1],
                        "contact_info": supplier[2],
                        "address": supplier[3],
                    }

                    # Send supplier data to the external system
                    response = self.external_api_client.send_supplier_data(supplier_data)
                    if response.get("success"):
                        logging.info(f"Synchronized supplier ID {supplier[0]} to external system.")
                    else:
                        logging.error(
                            f"Failed to synchronize supplier ID {supplier[0]}: {response.get('error')}"
                        )
        except Error as e:
            logging.error(f"Error during supplier synchronization: {e}")
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

    # Example external API client (a placeholder, replace with actual implementation)
    class MockExternalAPIClient:
        def send_product_data(self, product_data):
            return {"success": True}

        def update_stock(self, stock_update):
            return {"success": True}

        def get_orders(self):
            return []

        def send_supplier_data(self, supplier_data):
            return {"success": True}

    external_api_client = MockExternalAPIClient()

    sync_manager = DataSynchronizationManagement(db_config, external_api_client)
    sync_manager.synchronize_products_to_external()
    sync_manager.synchronize_stock_to_external()
    sync_manager.synchronize_orders_from_external()
    sync_manager.synchronize_suppliers_to_external()
