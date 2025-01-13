import logging
from accesscontrolmanagement import AccessControlManagement
from datavalidationmanagement import DataValidationManagement

class UserManagement:
    """
    Manages user data, including creation, updates, deletions, and role assignments.
    """

    def __init__(self, database_connection):
        """
        Initialize UserManagement.

        :param database_connection: Database connection instance.
        """
        self.database_connection = database_connection
        self.access_control = AccessControlManagement(database_connection)
        self.data_validation = DataValidationManagement()

    def create_user(self, username, password, role):
        """
        Create a new user in the system.

        :param username: The username of the new user.
        :param password: The password of the new user.
        :param role: The role to assign to the user.
        :return: None
        """
        if not self.data_validation.validate_username(username):
            logging.error("Invalid username format.")
            raise ValueError("Invalid username format.")

        if not self.data_validation.validate_password(password):
            logging.error("Invalid password format.")
            raise ValueError("Invalid password format.")

        if not self.access_control.validate_role(role):
            logging.error(f"Invalid role: {role}")
            raise ValueError(f"Invalid role: {role}")

        try:
            cursor = self.database_connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;
                """,
                (username, password),
            )
            user_id = cursor.fetchone()[0]

            # Assign role using AccessControlManagement
            self.access_control.assign_role(user_id, role)

            self.database_connection.commit()
            logging.info(f"User {username} created with role {role}.")
        except Exception as e:
            self.database_connection.rollback()
            logging.error(f"Failed to create user {username}: {e}")
            raise

    def update_user_role(self, username, new_role):
        """
        Update the role of an existing user.

        :param username: The username of the user to update.
        :param new_role: The new role to assign.
        :return: None
        """
        if not self.access_control.validate_role(new_role):
            logging.error(f"Invalid role: {new_role}")
            raise ValueError(f"Invalid role: {new_role}")

        try:
            cursor = self.database_connection.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s;",
                (username,)
            )
            result = cursor.fetchone()
            if not result:
                logging.error(f"User {username} not found.")
                raise ValueError(f"User {username} not found.")

            user_id = result[0]
            self.access_control.assign_role(user_id, new_role)

            self.database_connection.commit()
            logging.info(f"Updated role for user {username} to {new_role}.")
        except Exception as e:
            self.database_connection.rollback()
            logging.error(f"Failed to update role for user {username}: {e}")
            raise

    def delete_user(self, username):
        """
        Delete a user from the system.

        :param username: The username of the user to delete.
        :return: None
        """
        try:
            cursor = self.database_connection.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s;",
                (username,)
            )
            result = cursor.fetchone()
            if not result:
                logging.error(f"User {username} not found.")
                raise ValueError(f"User {username} not found.")

            user_id = result[0]

            # Remove role assignment
            self.access_control.remove_role(user_id)

            # Delete user
            cursor.execute("DELETE FROM users WHERE id = %s;", (user_id,))
            self.database_connection.commit()

            logging.info(f"User {username} deleted.")
        except Exception as e:
            self.database_connection.rollback()
            logging.error(f"Failed to delete user {username}: {e}")
            raise

    def get_user_role(self, username):
        """
        Retrieve the role of a user.

        :param username: The username to query.
        :return: The role of the user.
        """
        try:
            cursor = self.database_connection.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = %s;",
                (username,)
            )
            result = cursor.fetchone()
            if not result:
                logging.error(f"User {username} not found.")
                raise ValueError(f"User {username} not found.")

            user_id = result[0]
            role = self.access_control.get_role(user_id)
            logging.info(f"Retrieved role for user {username}: {role}")
            return role
        except Exception as e:
            logging.error(f"Failed to retrieve role for user {username}: {e}")
            raise

# Example usage
if __name__ == "__main__":
    from databaseconnection import DatabaseConnection

    db_connection = DatabaseConnection().connect()
    user_manager = UserManagement(db_connection)

    # Create a user
    user_manager.create_user("admin", "securepassword", "admin")

    # Update user role
    user_manager.update_user_role("admin", "superadmin")

    # Delete user
    user_manager.delete_user("admin")
