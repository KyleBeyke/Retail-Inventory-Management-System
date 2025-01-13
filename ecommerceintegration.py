import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="ecommerce_integration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class EcommerceIntegration:
    """
    A class to manage WooCommerce integration, including synchronization of products,
    inventory, and sales data between the local inventory system and the WooCommerce platform.
    """

    def __init__(self, db_config, woocommerce_api):
        """
        Initialize the EcommerceIntegration class.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        :param woocommerce_api: WooCommerce API client instance for making requests to the store.
        """
        self.db_config = db_config
        self.woocommerce_api = woocommerce_api

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

    def sync_products_to_ecommerce(self):
        """
        Sync local product data to the WooCommerce store.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT product_id, product_name, sku, price, description, stock_quantity
                FROM products;
                """
                cursor.execute(query)
                products = cursor.fetchall()

                for product in products:
                    payload = {
                        "name": product[1],
                        "sku": product[2],
                        "regular_price": str(product[3]),
                        "description": product[4],
                        "stock_quantity": product[5],
                        "manage_stock": True
                    }
                    response = self.woocommerce_api.post("products", payload)
                    if response.status_code == 201:
                        logging.info(f"Product synced: {product[1]} (SKU: {product[2]})")
                    else:
                        logging.error(f"Failed to sync product: {product[1]} (SKU: {product[2]}). Error: {response.text}")
        except Error as e:
            logging.error(f"Error during product synchronization: {e}")
            raise
        finally:
            conn.close()

    def sync_inventory_from_ecommerce(self):
        """
        Sync inventory levels from WooCommerce to the local inventory system.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                response = self.woocommerce_api.get("products")
                if response.status_code == 200:
                    products = response.json()
                    for product in products:
                        query = """
                        UPDATE products
                        SET stock_quantity = %s
                        WHERE sku = %s;
                        """
                        cursor.execute(query, (product["stock_quantity"], product["sku"]))
                        conn.commit()
                        logging.info(f"Inventory updated for SKU: {product['sku']}")
                else:
                    logging.error(f"Failed to fetch products from WooCommerce. Error: {response.text}")
        except Error as e:
            logging.error(f"Error during inventory synchronization: {e}")
            raise
        finally:
            conn.close()

    def sync_sales_data(self):
        """
        Sync sales data from WooCommerce to the local system.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                response = self.woocommerce_api.get("orders")
                if response.status_code == 200:
                    orders = response.json()
                    for order in orders:
                        query = """
                        INSERT INTO sales (order_id, customer_name, total_amount, status, order_date)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (order_id) DO NOTHING;
                        """
                        cursor.execute(query, (
                            order["id"],
                            order["billing"]["first_name"] + " " + order["billing"]["last_name"],
                            order["total"],
                            order["status"],
                            order["date_created"]
                        ))
                        conn.commit()
                        logging.info(f"Order synced: {order['id']} - Total: {order['total']}")
                else:
                    logging.error(f"Failed to fetch orders from WooCommerce. Error: {response.text}")
        except Error as e:
            logging.error(f"Error during sales data synchronization: {e}")
            raise
        finally:
            conn.close()

# Example Usage:
if __name__ == "__main__":
    from woocommerce import API

    # WooCommerce API configuration
    wc_api = API(
        url="https://yourstore.com",
        consumer_key="ck_your_consumer_key",
        consumer_secret="cs_your_consumer_secret",
        version="wc/v3"
    )

    # Database configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    ecommerce_integration = EcommerceIntegration(db_config, wc_api)

    # Sync products to WooCommerce
    ecommerce_integration.sync_products_to_ecommerce()

    # Sync inventory levels from WooCommerce
    ecommerce_integration.sync_inventory_from_ecommerce()

    # Sync sales data from WooCommerce
    ecommerce_integration.sync_sales_data()
