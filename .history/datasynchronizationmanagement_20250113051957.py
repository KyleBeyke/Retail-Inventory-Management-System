import logging
import psycopg2
from psycopg2 import sql
import requests
from datetime import datetime, timedelta
from datavalidationmanagement import DataValidationManagement

# Configure logging
logging.basicConfig(
    filename="data_synchronization_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataSynchronizationManagement:
    """
    Handles synchronization of data between the local PostgreSQL database and external systems.
    """

    def __init__(self, db_config, external_api_config):
        """
        Initialize the DataSynchronizationManagement class.
        :param db_config: Dictionary containing 'dbname', 'user', 'password', 'host', and 'port'.
        :param external_api_config: Dictionary containing API configuration details (e.g., base_url, auth_token).
        """
        self.db_config = db_config
        self.api_config = external_api_config
        self.validator = DataValidationManagement()

    def _connect(self):
        """
        Establish a connection to the PostgreSQL database.
        :return: A psycopg2 connection object.
        """
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except psycopg2.Error as e:
            logging.error(f"Database connection error: {e}")
            raise

    def fetch_external_data(self, endpoint):
        """
        Fetch data from an external system using an API.
        :param endpoint: API endpoint to fetch data from.
        :return: JSON data retrieved from the external system.
        """
        try:
            url = f"{self.api_config['base_url']}/{endpoint}"
            headers = {"Authorization": f"Bearer {self.api_config['auth_token']}"}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            logging.info(f"Fetched data from endpoint: {endpoint}")
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching data from endpoint {endpoint}: {e}")
            raise

    def sync_data_to_db(self, table_name, data):
        """
        Synchronize data from an external system to the local database.
        :param table_name: Name of the database table to update.
        :param data: List of dictionaries representing the data to sync.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                for record in data:
                    # Validate record
                    if not self.validator.validate_record(table_name, record):
                        logging.warning(f"Invalid record skipped for table {table_name}: {record}")
                        continue

                    # Generate SQL query for UPSERT (insert or update)
                    columns = record.keys()
                    values = [record[column] for column in columns]
                    query = sql.SQL(
                        """
                        INSERT INTO {table} ({fields})
                        VALUES ({values})
                        ON CONFLICT (id) DO UPDATE
                        SET {updates}
                        """
                    ).format(
                        table=sql.Identifier(table_name),
                        fields=sql.SQL(", ").join(map(sql.Identifier, columns)),
                        values=sql.SQL(", ").join(sql.Placeholder() * len(values)),
                        updates=sql.SQL(", ").join(
                            [
                                sql.SQL("{field} = EXCLUDED.{field}").format(field=sql.Identifier(col))
                                for col in columns
                            ]
                        )
                    )

                    # Execute query
                    cursor.execute(query, values)

                conn.commit()
                logging.info(f"Synchronized data to table {table_name}")
        except (Exception, psycopg2.Error) as e:
            logging.error(f"Error syncing data to table {table_name}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def sync_data_to_external(self, endpoint, table_name):
        """
        Synchronize data from the local database to an external system.
        :param endpoint: API endpoint to send data to.
        :param table_name: Name of the database table to retrieve data from.
        :return: None
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                # Fetch data from the local database
                cursor.execute(sql.SQL("SELECT * FROM {table}").format(
                    table=sql.Identifier(table_name)
                ))
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

                # Convert rows to list of dictionaries
                data = [dict(zip(columns, row)) for row in rows]

                # Send data to the external system
                url = f"{self.api_config['base_url']}/{endpoint}"
                headers = {"Authorization": f"Bearer {self.api_config['auth_token']}", "Content-Type": "application/json"}
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()

                logging.info(f"Synchronized data from table {table_name} to endpoint {endpoint}")
        except (requests.RequestException, Exception, psycopg2.Error) as e:
            logging.error(f"Error syncing data to external endpoint {endpoint} from table {table_name}: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def schedule_periodic_sync(self, interval_minutes):
        """
        Schedule periodic synchronization of data.
        :param interval_minutes: Interval in minutes for periodic synchronization.
        :return: None
        """
        try:
            next_run = datetime.now()
            while True:
                current_time = datetime.now()
                if current_time >= next_run:
                    # Perform synchronization
                    logging.info("Starting periodic data synchronization.")
                    # Example usage (adjust as needed):
                    # self.sync_data_to_db("products", self.fetch_external_data("products"))
                    # self.sync_data_to_external("update_inventory", "inventory")

                    next_run = current_time + timedelta(minutes=interval_minutes)
        except Exception as e:
            logging.error(f"Error during periodic synchronization: {e}")
            raise

# Example Usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    external_api_config = {
        "base_url": "https://api.example.com",
        "auth_token": "your_api_token_here"
    }

    sync_manager = DataSynchronizationManagement(db_config, external_api_config)

    # Example: Synchronize data from external system to local database
    products_data = sync_manager.fetch_external_data("products")
    sync_manager.sync_data_to_db("products", products_data)

    # Example: Synchronize data from local database to external system
    sync_manager.sync_data_to_external("update_inventory", "inventory")
