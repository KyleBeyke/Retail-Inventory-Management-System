import psycopg2
from psycopg2 import Error
import logging

# Configure logging
logging.basicConfig(
    filename="audit_log_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AuditLogManagement:
    """
    A class to manage audit logs for tracking changes and actions within the inventory system.
    """

    def __init__(self, db_config):
        """
        Initialize the AuditLogManagement class with database connection configuration.
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

    def log_action(self, user_id, action_type, description, affected_table=None, affected_id=None):
        """
        Log an action to the audit log.
        :param user_id: The ID of the user performing the action.
        :param action_type: Type of action performed (e.g., 'CREATE', 'UPDATE', 'DELETE').
        :param description: A detailed description of the action performed.
        :param affected_table: The name of the table affected (optional).
        :param affected_id: The ID of the record affected (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO audit_logs (user_id, action_type, description, affected_table, affected_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, NOW());
                """
                cursor.execute(query, (user_id, action_type, description, affected_table, affected_id))
                conn.commit()
                logging.info(f"Logged action: User {user_id} performed {action_type} on {affected_table} (ID: {affected_id}).")
        except Error as e:
            logging.error(f"Error logging action for user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def get_logs(self, user_id=None, action_type=None, start_date=None, end_date=None):
        """
        Retrieve logs based on filters.
        :param user_id: Filter by user ID (optional).
        :param action_type: Filter by action type (optional).
        :param start_date: Filter by start date (optional).
        :param end_date: Filter by end date (optional).
        :return: A list of logs matching the criteria.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = "SELECT * FROM audit_logs WHERE TRUE"
                params = []

                if user_id:
                    query += " AND user_id = %s"
                    params.append(user_id)
                if action_type:
                    query += " AND action_type = %s"
                    params.append(action_type)
                if start_date:
                    query += " AND timestamp >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND timestamp <= %s"
                    params.append(end_date)

                query += " ORDER BY timestamp DESC;"
                cursor.execute(query, tuple(params))
                logs = cursor.fetchall()
                logging.info("Retrieved audit logs based on filters.")
                return logs
        except Error as e:
            logging.error(f"Error retrieving logs: {e}")
            raise
        finally:
            conn.close()

    def delete_old_logs(self, retention_days):
        """
        Delete logs older than the specified retention period.
        :param retention_days: Number of days to retain logs.
        :return: The number of logs deleted.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM audit_logs
                WHERE timestamp < NOW() - INTERVAL '%s days'
                RETURNING *;
                """
                cursor.execute(query, (retention_days,))
                deleted_logs = cursor.rowcount
                conn.commit()
                logging.info(f"Deleted {deleted_logs} old logs older than {retention_days} days.")
                return deleted_logs
        except Error as e:
            logging.error(f"Error deleting old logs: {e}")
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

    audit_manager = AuditLogManagement(db_config)

    # Log an action
    audit_manager.log_action(user_id=1, action_type="CREATE", description="Added a new product", affected_table="products", affected_id=101)

    # Retrieve logs
    logs = audit_manager.get_logs(start_date="2025-01-01", end_date="2025-01-31")
    for log in logs:
        print(log)

    # Delete old logs
    deleted_count = audit_manager.delete_old_logs(retention_days=90)
    print(f"Deleted {deleted_count} old logs.")
