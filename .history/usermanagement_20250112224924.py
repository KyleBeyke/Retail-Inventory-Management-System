import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="user_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class UserManagement:
    """
    A class to manage users, their roles, and permissions in the inventory management system.
    """

    def __init__(self, db_config):
        """
        Initialize the UserManagement class with database connection configuration.
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

    def add_user(self, username, password, role):
        """
        Add a new user to the database.
        :param username: Username of the new user.
        :param password: Password of the new user (hashed for security).
        :param role: Role assigned to the new user (e.g., 'admin', 'manager', 'viewer').
        :return: The ID of the newly added user.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO users (username, password, role)
                VALUES (%s, %s, %s)
                RETURNING user_id;
                """
                cursor.execute(query, (username, password, role))
                user_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added user: {username} with ID: {user_id}.")
                return user_id
        except Error as e:
            logging.error(f"Error adding user {username}: {e}")
            raise
        finally:
            conn.close()

    def get_user(self, user_id):
        """
        Retrieve details of a user by their ID.
        :param user_id: ID of the user.
        :return: A dictionary containing user details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT user_id, username, role
                FROM users
                WHERE user_id = %s;
                """
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                if result:
                    user_details = {
                        "user_id": result[0],
                        "username": result[1],
                        "role": result[2]
                    }
                    logging.info(f"Retrieved user details for ID: {user_id}.")
                    return user_details
                else:
                    logging.warning(f"No user found with ID: {user_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving user with ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def update_user(self, user_id, username=None, password=None, role=None):
        """
        Update details of an existing user.
        :param user_id: ID of the user to update.
        :param username: New username (optional).
        :param password: New password (hashed, optional).
        :param role: New role (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if username:
                    fields.append("username = %s")
                    values.append(username)
                if password:
                    fields.append("password = %s")
                    values.append(password)
                if role:
                    fields.append("role = %s")
                    values.append(role)

                if fields:
                    query = sql.SQL("""
                        UPDATE users
                        SET {fields}
                        WHERE user_id = %s;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    values.append(user_id)
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info(f"Updated user with ID: {user_id}.")
                else:
                    logging.warning(f"No fields provided for updating user ID: {user_id}.")
        except Error as e:
            logging.error(f"Error updating user with ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_user(self, user_id):
        """
        Delete a user from the database.
        :param user_id: ID of the user to delete.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM users
                WHERE user_id = %s;
                """
                cursor.execute(query, (user_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No user found with ID: {user_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted user with ID: {user_id}.")
        except Error as e:
            logging.error(f"Error deleting user with ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def list_users(self):
        """
        List all users in the system.
        :return: A list of dictionaries, each containing user details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT user_id, username, role
                FROM users;
                """
                cursor.execute(query)
                results = cursor.fetchall()
                users = [
                    {"user_id": row[0], "username": row[1], "role": row[2]}
                    for row in results
                ]
                logging.info("Retrieved list of all users.")
                return users
        except Error as e:
            logging.error(f"Error listing users: {e}")
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

    user_manager = UserManagement(db_config)

    # Add a user
    user_id = user_manager.add_user("jdoe", "hashed_password", "admin")

    # Get user details
    user_details = user_manager.get_user(user_id)
    print(user_details)

    # Update user details
    user_manager.update_user(user_id, username="johndoe", role="manager")

    # List all users
    users = user_manager.list_users()
    print(users)

    # Delete a user
    user_manager.delete_user(user_id)
