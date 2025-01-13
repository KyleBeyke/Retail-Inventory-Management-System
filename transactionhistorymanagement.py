import psycopg2
from psycopg2 import sql, Error
import logging
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="transaction_history_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)


class TransactionHistoryManagement:
    """
    A class to manage the transaction history, including logging sales, purchases, and stock movements.
    """

    def __init__(self, db_config):
        """
        Initialize the TransactionHistoryManagement class with database connection configuration.
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

    def log_transaction(self, transaction_type, details, location_type=None, location_id=None, user_id=None):
        """
        Log a transaction in the database.
        :param transaction_type: Type of transaction ('sale', 'purchase', 'stock_transfer').
        :param details: A list of dictionaries with keys: product_id, quantity, unit_price.
        :param location_type: Location type ('store' or 'warehouse').
        :param location_id: ID of the location where the transaction occurred.
        :param user_id: ID of the user performing the transaction (optional).
        :return: The transaction ID.
        """
        # Validate inputs
        DataValidationManagement.validate_transaction_type(transaction_type, ["sale", "purchase", "stock_transfer"])
        if location_type:
            DataValidationManagement.validate_location_type(location_type, ["store", "warehouse"])
        if location_id:
            DataValidationManagement.validate_positive_integer(location_id, f"{location_type.capitalize()} ID")
        DataValidationManagement.validate_non_empty_list(details, "Transaction Details")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Insert the transaction header
                query = """
                INSERT INTO transactions (transaction_type, location_type, location_id, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING transaction_id;
                """
                cursor.execute(query, (transaction_type, location_type, location_id, user_id))
                transaction_id = cursor.fetchone()[0]

                # Insert transaction details
                detail_query = """
                INSERT INTO transaction_details (transaction_id, product_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s);
                """
                for detail in details:
                    DataValidationManagement.validate_positive_integer(detail["product_id"], "Product ID")
                    DataValidationManagement.validate_non_negative_integer(detail["quantity"], "Quantity")
                    DataValidationManagement.validate_non_negative_float(detail["unit_price"], "Unit Price")
                    cursor.execute(
                        detail_query,
                        (transaction_id, detail["product_id"], detail["quantity"], detail["unit_price"])
                    )

                conn.commit()
                logging.info(f"Logged transaction with ID: {transaction_id}, Type: {transaction_type}.")
                return transaction_id
        except Error as e:
            logging.error(f"Error logging transaction of type {transaction_type}: {e}")
            raise
        finally:
            conn.close()

    def get_transaction(self, transaction_id):
        """
        Retrieve details of a specific transaction.
        :param transaction_id: ID of the transaction to retrieve.
        :return: A dictionary containing transaction details.
        """
        # Validate input
        DataValidationManagement.validate_positive_integer(transaction_id, "Transaction ID")

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Get transaction header
                header_query = """
                SELECT transaction_id, transaction_type, location_type, location_id, user_id, transaction_date
                FROM transactions
                WHERE transaction_id = %s;
                """
                cursor.execute(header_query, (transaction_id,))
                header = cursor.fetchone()

                if not header:
                    logging.warning(f"No transaction found with ID: {transaction_id}.")
                    return None

                transaction = {
                    "transaction_id": header[0],
                    "transaction_type": header[1],
                    "location_type": header[2],
                    "location_id": header[3],
                    "user_id": header[4],
                    "transaction_date": header[5],
                    "details": []
                }

                # Get transaction details
                detail_query = """
                SELECT product_id, quantity, unit_price
                FROM transaction_details
                WHERE transaction_id = %s;
                """
                cursor.execute(detail_query, (transaction_id,))
                details = cursor.fetchall()
                for detail in details:
                    transaction["details"].append({
                        "product_id": detail[0],
                        "quantity": detail[1],
                        "unit_price": detail[2]
                    })

                logging.info(f"Retrieved transaction with ID: {transaction_id}.")
                return transaction
        except Error as e:
            logging.error(f"Error retrieving transaction with ID {transaction_id}: {e}")
            raise
        finally:
            conn.close()

    def get_transactions_by_type(self, transaction_type, start_date=None, end_date=None):
        """
        Retrieve all transactions of a specific type within an optional date range.
        :param transaction_type: Type of transaction ('sale', 'purchase', 'stock_transfer').
        :param start_date: Start date for filtering transactions (optional).
        :param end_date: End date for filtering transactions (optional).
        :return: A list of dictionaries containing transaction details.
        """
        # Validate inputs
        DataValidationManagement.validate_transaction_type(transaction_type, ["sale", "purchase", "stock_transfer"])

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT transaction_id, transaction_type, location_type, location_id, user_id, transaction_date
                FROM transactions
                WHERE transaction_type = %s
                  AND (%s IS NULL OR transaction_date >= %s)
                  AND (%s IS NULL OR transaction_date <= %s);
                """
                cursor.execute(query, (transaction_type, start_date, start_date, end_date, end_date))
                results = cursor.fetchall()
                transactions = [
                    {
                        "transaction_id": row[0],
                        "transaction_type": row[1],
                        "location_type": row[2],
                        "location_id": row[3],
                        "user_id": row[4],
                        "transaction_date": row[5]
                    }
                    for row in results
                ]
                logging.info(f"Retrieved {len(transactions)} transactions of type: {transaction_type}.")
                return transactions
        except Error as e:
            logging.error(f"Error retrieving transactions of type {transaction_type}: {e}")
            raise
        finally:
            conn.close()
