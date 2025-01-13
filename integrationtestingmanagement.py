import logging
import psycopg2
from psycopg2 import sql, Error
import requests

# Configure logging
logging.basicConfig(
    filename="integration_testing.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class IntegrationTestingManagement:
    """
    A class to perform integration tests for various system components,
    including database, third-party APIs, and external services.
    """

    def __init__(self, db_config=None, api_endpoints=None):
        """
        Initialize the IntegrationTestingManagement class.
        :param db_config: Dictionary containing database connection details.
        :param api_endpoints: Dictionary containing API endpoints for testing.
        """
        self.db_config = db_config
        self.api_endpoints = api_endpoints or {}

    def test_database_connection(self):
        """
        Test the database connection by executing a simple query.
        :return: True if the connection is successful, False otherwise.
        """
        if not self.db_config:
            logging.error("Database configuration is not provided.")
            return False

        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                if result and result[0] == 1:
                    logging.info("Database connection test successful.")
                    return True
                else:
                    logging.error("Database connection test failed.")
                    return False
        except Error as e:
            logging.error(f"Error testing database connection: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def test_api_endpoint(self, name, url, method="GET", payload=None, headers=None):
        """
        Test a single API endpoint.
        :param name: Name of the API for logging purposes.
        :param url: URL of the API endpoint.
        :param method: HTTP method to use (default is GET).
        :param payload: Data to send in the request body (for POST/PUT requests).
        :param headers: Dictionary of request headers.
        :return: Response status and success flag.
        """
        try:
            response = None
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=payload, headers=headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=payload, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                logging.error(f"Unsupported HTTP method: {method}")
                return False

            if response.status_code == 200:
                logging.info(f"API test successful for {name} ({url}). Status code: {response.status_code}.")
                return True
            else:
                logging.error(f"API test failed for {name} ({url}). Status code: {response.status_code}.")
                return False
        except Exception as e:
            logging.error(f"Error testing API endpoint {name} ({url}): {e}")
            return False

    def test_all_api_endpoints(self):
        """
        Test all API endpoints configured in the class.
        :return: Dictionary with API names as keys and success flags as values.
        """
        results = {}
        for name, details in self.api_endpoints.items():
            url = details.get("url")
            method = details.get("method", "GET")
            payload = details.get("payload", None)
            headers = details.get("headers", None)
            results[name] = self.test_api_endpoint(name, url, method, payload, headers)
        return results

    def test_third_party_pos_integration(self, pos_url, auth_token=None):
        """
        Test the integration with a third-party POS system.
        :param pos_url: URL of the POS API.
        :param auth_token: Authentication token if required.
        :return: True if the integration is successful, False otherwise.
        """
        try:
            headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
            response = requests.get(pos_url, headers=headers)
            if response.status_code == 200:
                logging.info("Third-party POS integration test successful.")
                return True
            else:
                logging.error(f"Third-party POS integration test failed. Status code: {response.status_code}.")
                return False
        except Exception as e:
            logging.error(f"Error testing third-party POS integration: {e}")
            return False

    def perform_full_integration_tests(self):
        """
        Perform a full suite of integration tests, including database and APIs.
        :return: Summary dictionary of all test results.
        """
        logging.info("Starting full integration testing.")
        results = {}

        # Test database connection
        results["Database Connection"] = self.test_database_connection()

        # Test all API endpoints
        api_results = self.test_all_api_endpoints()
        results.update(api_results)

        # Log final results
        logging.info("Integration testing completed. Results:")
        for key, success in results.items():
            status = "PASS" if success else "FAIL"
            logging.info(f"{key}: {status}")

        return results

# Example Usage
if __name__ == "__main__":
    # Example configuration
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    api_endpoints = {
        "WooCommerce API": {"url": "https://example.com/wp-json/wc/v3", "method": "GET"},
        "Payment Gateway API": {"url": "https://api.paymentgateway.com/v1/transactions", "method": "POST"},
    }

    integration_manager = IntegrationTestingManagement(db_config=db_config, api_endpoints=api_endpoints)

    # Perform full integration tests
    test_results = integration_manager.perform_full_integration_tests()
    print("Integration Test Results:", test_results)
