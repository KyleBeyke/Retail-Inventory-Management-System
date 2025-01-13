import psycopg2
from psycopg2 import sql, Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="notification_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class NotificationManagement:
    """
    A class to manage notifications for various events, including creating, retrieving,
    and sending notifications to users.
    """

    def __init__(self, db_config):
        """
        Initialize the NotificationManagement class with database connection configuration.
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

    def create_notification(self, user_id, event_type, message, priority="Normal", timestamp=None):
        """
        Create a new notification for a user.
        :param user_id: ID of the user to notify.
        :param event_type: Type of the event triggering the notification.
        :param message: Notification message.
        :param priority: Priority level of the notification (e.g., Normal, High).
        :param timestamp: Optional timestamp for the notification (default is current time).
        :return: The ID of the newly created notification.
        """
        if not timestamp:
            timestamp = datetime.now()

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO notifications (user_id, event_type, message, priority, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING notification_id;
                """
                cursor.execute(query, (user_id, event_type, message, priority, timestamp))
                notification_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Created notification ID {notification_id} for user ID {user_id}.")
                return notification_id
        except Error as e:
            logging.error(f"Error creating notification for user ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def get_notifications(self, user_id=None, event_type=None, priority=None, limit=50):
        """
        Retrieve notifications based on filters.
        :param user_id: Optional user ID to filter notifications.
        :param event_type: Optional event type to filter notifications.
        :param priority: Optional priority level to filter notifications.
        :param limit: Maximum number of notifications to retrieve (default is 50).
        :return: A list of notifications matching the filters.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                conditions = []
                values = []

                if user_id:
                    conditions.append("user_id = %s")
                    values.append(user_id)
                if event_type:
                    conditions.append("event_type = %s")
                    values.append(event_type)
                if priority:
                    conditions.append("priority = %s")
                    values.append(priority)

                query = "SELECT notification_id, user_id, event_type, message, priority, timestamp FROM notifications"
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                query += " ORDER BY timestamp DESC LIMIT %s;"
                values.append(limit)

                cursor.execute(query, values)
                notifications = cursor.fetchall()
                logging.info(f"Retrieved {len(notifications)} notifications.")
                return [
                    {
                        "notification_id": n[0],
                        "user_id": n[1],
                        "event_type": n[2],
                        "message": n[3],
                        "priority": n[4],
                        "timestamp": n[5]
                    } for n in notifications
                ]
        except Error as e:
            logging.error(f"Error retrieving notifications: {e}")
            raise
        finally:
            conn.close()

    def delete_notification(self, notification_id):
        """
        Delete a notification by its ID.
        :param notification_id: ID of the notification to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM notifications
                WHERE notification_id = %s;
                """
                cursor.execute(query, (notification_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No notification found with ID {notification_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted notification ID {notification_id}.")
        except Error as e:
            logging.error(f"Error deleting notification ID {notification_id}: {e}")
            raise
        finally:
            conn.close()

    def send_notification(self, user_id, message):
        """
        Simulate sending a notification to a user.
        :param user_id: ID of the user to send the notification to.
        :param message: Notification message.
        :return: None.
        """
        try:
            logging.info(f"Sending notification to user ID {user_id}: {message}")
            # In a real implementation, integrate with email/SMS/push services here.
            print(f"Notification sent to user {user_id}: {message}")
        except Exception as e:
            logging.error(f"Error sending notification to user ID {user_id}: {e}")
            raise

# Example Usage:
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    notification_manager = NotificationManagement(db_config)

    # Create a notification
    notification_id = notification_manager.create_notification(
        user_id=1,
        event_type="Low Stock Alert",
        message="Product X is running low on stock.",
        priority="High"
    )

    # Retrieve notifications
    notifications = notification_manager.get_notifications(user_id=1, limit=10)
    print(notifications)

    # Send a notification
    notification_manager.send_notification(user_id=1, message="Check your stock levels.")

    # Delete a notification
    notification_manager.delete_notification(notification_id)
