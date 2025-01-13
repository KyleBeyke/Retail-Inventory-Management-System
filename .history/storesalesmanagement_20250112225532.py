import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="store_sales_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class StoreSalesManagement:
    """
    A class to manage store sales data, including recording transactions,
    retrieving sales summaries, and managing detailed sales information.
    """

    def __init__(self, db_config):
        """
        Initialize the StoreSalesManagement class with database connection configuration.
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

    def record_transaction(self, store_id, transaction_details):
        """
        Record a new sales transaction for a specific store.
        :param store_id: ID of the store where the transaction occurred.
        :param transaction_details: List of dictionaries containing product_id, quantity, price, and discount.
        :return: The ID of the newly recorded transaction.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Insert transaction header
                query_header = """
                INSERT INTO store_sales (store_id, transaction_date)
                VALUES (%s, CURRENT_TIMESTAMP)
                RETURNING transaction_id;
                """
                cursor.execute(query_header, (store_id,))
                transaction_id = cursor.fetchone()[0]

                # Insert transaction details
                query_details = """
                INSERT INTO store_sales_details (transaction_id, product_id, quantity, price, discount)
                VALUES (%s, %s, %s, %s, %s);
                """
                for detail in transaction_details:
                    cursor.execute(
                        query_details,
                        (
                            transaction_id,
                            detail['product_id'],
                            detail['quantity'],
                            detail['price'],
                            detail['discount']
                        )
                    )
                conn.commit()
                logging.info(f"Recorded transaction ID: {transaction_id} for store ID: {store_id}.")
                return transaction_id
        except Error as e:
            logging.error(f"Error recording transaction for store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_sales_summary(self, store_id, start_date, end_date):
        """
        Retrieve a summary of sales for a specific store within a date range.
        :param store_id: ID of the store.
        :param start_date: Start date for the summary (YYYY-MM-DD).
        :param end_date: End date for the summary (YYYY-MM-DD).
        :return: A dictionary containing total sales, total quantity, and total discounts.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT
                    SUM(sd.quantity * sd.price) AS total_sales,
                    SUM(sd.quantity) AS total_quantity,
                    SUM(sd.discount) AS total_discounts
                FROM store_sales s
                JOIN store_sales_details sd ON s.transaction_id = sd.transaction_id
                WHERE s.store_id = %s AND s.transaction_date BETWEEN %s AND %s;
                """
                cursor.execute(query, (store_id, start_date, end_date))
                result = cursor.fetchone()
                if result:
                    sales_summary = {
                        "total_sales": result[0] or 0,
                        "total_quantity": result[1] or 0,
                        "total_discounts": result[2] or 0
                    }
                    logging.info(f"Retrieved sales summary for store ID {store_id} from {start_date} to {end_date}.")
                    return sales_summary
                else:
                    logging.warning(f"No sales data found for store ID {store_id} in the given date range.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving sales summary for store ID {store_id}: {e}")
            raise
        finally:
            conn.close()

    def get_transaction_details(self, transaction_id):
        """
        Retrieve detailed information about a specific transaction.
        :param transaction_id: ID of the transaction to retrieve.
        :return: A dictionary containing transaction header and details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Fetch transaction header
                query_header = """
                SELECT transaction_id, store_id, transaction_date
                FROM store_sales
                WHERE transaction_id = %s;
                """
                cursor.execute(query_header, (transaction_id,))
                header = cursor.fetchone()

                if not header:
                    logging.warning(f"No transaction found with ID: {transaction_id}.")
                    return None

                # Fetch transaction details
                query_details = """
                SELECT product_id, quantity, price, discount
                FROM store_sales_details
                WHERE transaction_id = %s;
                """
                cursor.execute(query_details, (transaction_id,))
                details = cursor.fetchall()

                transaction_details = {
                    "transaction_id": header[0],
                    "store_id": header[1],
                    "transaction_date": header[2],
                    "items": [
                        {
                            "product_id": row[0],
                            "quantity": row[1],
                            "price": row[2],
                            "discount": row[3]
                        } for row in details
                    ]
                }
                logging.info(f"Retrieved details for transaction ID: {transaction_id}.")
                return transaction_details
        except Error as e:
            logging.error(f"Error retrieving transaction details for transaction ID {transaction_id}: {e}")
            raise
        finally:
            conn.close()

# Example Usage
if __name__ == "__main__":
    # Database configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    sales_manager = StoreSalesManagement(db_config)

    # Record a transaction
    transaction_id = sales_manager.record_transaction(
        store_id=1,
        transaction_details=[
            {"product_id": 101, "quantity": 2, "price": 10.0, "discount": 1.0},
            {"product_id": 102, "quantity": 1, "price": 20.0, "discount": 0.0}
        ]
    )
    print(f"Transaction ID: {transaction_id}")

    # Get sales summary
    summary = sales_manager.get_sales_summary(store_id=1, start_date="2025-01-01", end_date="2025-12-31")
    print(f"Sales Summary: {summary}")

    # Get transaction details
    details = sales_manager.get_transaction_details(transaction_id=transaction_id)
    print(f"Transaction Details: {details}")
