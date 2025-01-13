import logging
from datetime import datetime
from psycopg2 import sql, connect
from DataValidationManagement import DataValidationManagement

class AuditLogManagement:
    """
    Manages logging of system events and user actions to the audit log in the database.
    """

    def __init__(self, db_connection):
        """
        Initialize the AuditLogManagement class.

        :param db_connection: A psycopg2 database connection object.
        """
        self.db_connection = db_connection
        self.data_validator = DataValidationManagement()

    def log_event(self, event_type, event_details, user_id=None):
        """
        Log a system event or user action.

        :param event_type: The type of event (e.g., 'USER_LOGIN', 'DATA_EXPORT').
        :param event_details: A detailed description of the event.
        :param user_id: (Optional) The ID of the user associated with the event.
        :return: None
        """
        try:
            # Validate inputs
            self.data_validator.validate_non_empty_string(event_type, "event_type")
            self.data_validator.validate_non_empty_string(event_details, "event_details")
            if user_id is not None:
                self.data_validator.validate_positive_integer(user_id, "user_id")

            # Insert the log into the database
            query = sql.SQL(
                """
                INSERT INTO audit_log (event_type, event_details, user_id, timestamp)
                VALUES (%s, %s, %s, %s)
                """
            )
            timestamp = datetime.now()
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (event_type, event_details, user_id, timestamp))
                self.db_connection.commit()

            logging.info(f"Logged event: {event_type} - {event_details} (User ID: {user_id})")
        except Exception as e:
            logging.error(f"Failed to log event: {e}")
            raise

    def retrieve_logs(self, event_type=None, start_date=None, end_date=None, user_id=None, limit=None, offset=None):
        """
        Retrieve logs based on filters.

        :param event_type: (Optional) Filter by event type.
        :param start_date: (Optional) Filter by start date.
        :param end_date: (Optional) Filter by end date.
        :param user_id: (Optional) Filter by user ID.
        :param limit: (Optional) Maximum number of logs to retrieve.
        :param offset: (Optional) Number of logs to skip.
        :return: A list of logs matching the filters.
        """
        try:
            query = sql.SQL(
                """
                SELECT * FROM audit_log
                WHERE (%s IS NULL OR event_type = %s)
                AND (%s IS NULL OR timestamp >= %s)
                AND (%s IS NULL OR timestamp <= %s)
                AND (%s IS NULL OR user_id = %s)
                ORDER BY timestamp DESC
                LIMIT %s OFFSET %s
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(
                    query,
                    (event_type, event_type, start_date, start_date, end_date, end_date, user_id, user_id, limit, offset)
                )
                logs = cursor.fetchall()

            logging.info("Retrieved logs from audit log.")
            return logs
        except Exception as e:
            logging.error(f"Failed to retrieve logs: {e}")
            raise

    def delete_old_logs(self, retention_period_days):
        """
        Delete logs older than a specified retention period.

        :param retention_period_days: The number of days to retain logs.
        :return: The number of logs deleted.
        """
        try:
            self.data_validator.validate_positive_integer(retention_period_days, "retention_period_days")

            query = sql.SQL(
                """
                DELETE FROM audit_log
                WHERE timestamp < NOW() - INTERVAL %s
                RETURNING *
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (f"{retention_period_days} days",))
                deleted_logs = cursor.rowcount
                self.db_connection.commit()

            logging.info(f"Deleted {deleted_logs} old logs from audit log.")
            return deleted_logs
        except Exception as e:
            logging.error(f"Failed to delete old logs: {e}")
            raise

    def count_logs(self, event_type=None, user_id=None):
        """
        Count the number of logs based on filters.

        :param event_type: (Optional) Filter by event type.
        :param user_id: (Optional) Filter by user ID.
        :return: The count of logs matching the filters.
        """
        try:
            query = sql.SQL(
                """
                SELECT COUNT(*) FROM audit_log
                WHERE (%s IS NULL OR event_type = %s)
                AND (%s IS NULL OR user_id = %s)
                """
            )
            with self.db_connection.cursor() as cursor:
                cursor.execute(query, (event_type, event_type, user_id, user_id))
                count = cursor.fetchone()[0]

            logging.info(f"Counted {count} logs from audit log.")
            return count
        except Exception as e:
            logging.error(f"Failed to count logs: {e}")
            raise

# Example usage (to be removed in production):
if __name__ == "__main__":
    try:
        # Example database connection setup
        connection = connect(
            dbname="inventory_db",
            user="inventory_user",
            password="inventory_pass",
            host="localhost",
            port=5432
        )

        audit_log_manager = AuditLogManagement(connection)

        # Log an event
        audit_log_manager.log_event("USER_LOGIN", "User logged in successfully.", user_id=1)

        # Retrieve logs
        logs = audit_log_manager.retrieve_logs(limit=10, offset=0)
        for log in logs:
            print(log)

        # Count logs
        total_logs = audit_log_manager.count_logs()
        print(f"Total logs: {total_logs}")

        # Delete old logs
        deleted_count = audit_log_manager.delete_old_logs(90)
        print(f"Deleted {deleted_count} logs.")

    except Exception as e:
        logging.error(f"Error in AuditLogManagement example usage: {e}")
