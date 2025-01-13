import logging
import psycopg2
from psycopg2 import sql, Error

# Configure logging
logging.basicConfig(
    filename="user_preferences_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class UserPreferencesManagement:
    """
    A class to manage user-specific preferences, including themes, notifications,
    and default view settings.
    """

    def __init__(self, db_config):
        """
        Initialize the UserPreferencesManagement class.
        :param db_config: Dictionary containing database connection details.
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

    def set_user_preference(self, user_id, preference_key, preference_value):
        """
        Set or update a user-specific preference.
        :param user_id: ID of the user.
        :param preference_key: Key for the preference (e.g., 'theme', 'notification_settings').
        :param preference_value: Value for the preference (e.g., 'dark', '{"email": true, "sms": false}').
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO user_preferences (user_id, preference_key, preference_value)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, preference_key) DO UPDATE
                SET preference_value = EXCLUDED.preference_value;
                """
                cursor.execute(query, (user_id, preference_key, preference_value))
                conn.commit()
                logging.info(f"Set preference for user {user_id}: {preference_key} = {preference_value}.")
        except Error as e:
            logging.error(f"Error setting preference for user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def get_user_preference(self, user_id, preference_key):
        """
        Retrieve a specific user preference.
        :param user_id: ID of the user.
        :param preference_key: Key for the preference to retrieve.
        :return: The value of the preference, or None if not found.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT preference_value
                FROM user_preferences
                WHERE user_id = %s AND preference_key = %s;
                """
                cursor.execute(query, (user_id, preference_key))
                result = cursor.fetchone()
                if result:
                    logging.info(f"Retrieved preference for user {user_id}: {preference_key} = {result[0]}.")
                    return result[0]
                else:
                    logging.warning(f"No preference found for user {user_id} with key: {preference_key}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving preference for user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def get_all_user_preferences(self, user_id):
        """
        Retrieve all preferences for a specific user.
        :param user_id: ID of the user.
        :return: A dictionary of all preferences for the user.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT preference_key, preference_value
                FROM user_preferences
                WHERE user_id = %s;
                """
                cursor.execute(query, (user_id,))
                results = cursor.fetchall()
                if results:
                    preferences = {row[0]: row[1] for row in results}
                    logging.info(f"Retrieved all preferences for user {user_id}.")
                    return preferences
                else:
                    logging.warning(f"No preferences found for user {user_id}.")
                    return {}
        except Error as e:
            logging.error(f"Error retrieving all preferences for user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_user_preference(self, user_id, preference_key):
        """
        Delete a specific user preference.
        :param user_id: ID of the user.
        :param preference_key: Key for the preference to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM user_preferences
                WHERE user_id = %s AND preference_key = %s;
                """
                cursor.execute(query, (user_id, preference_key))
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Deleted preference for user {user_id}: {preference_key}.")
                else:
                    logging.warning(f"No preference found to delete for user {user_id} with key: {preference_key}.")
        except Error as e:
            logging.error(f"Error deleting preference for user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def reset_user_preferences(self, user_id):
        """
        Reset all preferences for a specific user.
        :param user_id: ID of the user.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM user_preferences
                WHERE user_id = %s;
                """
                cursor.execute(query, (user_id,))
                conn.commit()
                logging.info(f"Reset all preferences for user {user_id}.")
        except Error as e:
            logging.error(f"Error resetting preferences for user {user_id}: {e}")
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

    preferences_manager = UserPreferencesManagement(db_config)

    # Set user preferences
    preferences_manager.set_user_preference(user_id=1, preference_key="theme", preference_value="dark")
    preferences_manager.set_user_preference(user_id=1, preference_key="notification_settings", preference_value='{"email": true, "sms": false}')

    # Get a specific user preference
    theme = preferences_manager.get_user_preference(user_id=1, preference_key="theme")
    print("User Theme:", theme)

    # Get all user preferences
    all_preferences = preferences_manager.get_all_user_preferences(user_id=1)
    print("All Preferences:", all_preferences)

    # Delete a specific user preference
    preferences_manager.delete_user_preference(user_id=1, preference_key="theme")

    # Reset all preferences for a user
    preferences_manager.reset_user_preferences(user_id=1)
