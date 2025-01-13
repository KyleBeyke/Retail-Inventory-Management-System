import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="access_control_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class AccessControlManagement:
    """
    A class to manage access control within the system, including user roles,
    permissions, and access to various system features.
    """

    def __init__(self, db_config):
        """
        Initialize the AccessControlManagement class with database connection configuration.
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

    def add_role(self, role_name, description):
        """
        Add a new role to the system.
        :param role_name: Name of the role.
        :param description: Description of the role.
        :return: The ID of the newly added role.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO roles (role_name, description)
                VALUES (%s, %s)
                RETURNING role_id;
                """
                cursor.execute(query, (role_name, description))
                role_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added role: {role_name} with ID: {role_id}.")
                return role_id
        except Error as e:
            logging.error(f"Error adding role {role_name}: {e}")
            raise
        finally:
            conn.close()

    def assign_role_to_user(self, user_id, role_id):
        """
        Assign a role to a user.
        :param user_id: ID of the user.
        :param role_id: ID of the role to assign.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO user_roles (user_id, role_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
                """
                cursor.execute(query, (user_id, role_id))
                conn.commit()
                logging.info(f"Assigned role ID {role_id} to user ID {user_id}.")
        except Error as e:
            logging.error(f"Error assigning role ID {role_id} to user ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def add_permission(self, permission_name, description):
        """
        Add a new permission to the system.
        :param permission_name: Name of the permission.
        :param description: Description of the permission.
        :return: The ID of the newly added permission.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO permissions (permission_name, description)
                VALUES (%s, %s)
                RETURNING permission_id;
                """
                cursor.execute(query, (permission_name, description))
                permission_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added permission: {permission_name} with ID: {permission_id}.")
                return permission_id
        except Error as e:
            logging.error(f"Error adding permission {permission_name}: {e}")
            raise
        finally:
            conn.close()

    def assign_permission_to_role(self, role_id, permission_id):
        """
        Assign a permission to a role.
        :param role_id: ID of the role.
        :param permission_id: ID of the permission to assign.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING;
                """
                cursor.execute(query, (role_id, permission_id))
                conn.commit()
                logging.info(f"Assigned permission ID {permission_id} to role ID {role_id}.")
        except Error as e:
            logging.error(f"Error assigning permission ID {permission_id} to role ID {role_id}: {e}")
            raise
        finally:
            conn.close()

    def check_user_permission(self, user_id, permission_name):
        """
        Check if a user has a specific permission.
        :param user_id: ID of the user.
        :param permission_name: Name of the permission to check.
        :return: True if the user has the permission, False otherwise.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT COUNT(*)
                FROM user_roles ur
                JOIN role_permissions rp ON ur.role_id = rp.role_id
                JOIN permissions p ON rp.permission_id = p.permission_id
                WHERE ur.user_id = %s AND p.permission_name = %s;
                """
                cursor.execute(query, (user_id, permission_name))
                result = cursor.fetchone()[0]
                if result > 0:
                    logging.info(f"User ID {user_id} has permission: {permission_name}.")
                    return True
                else:
                    logging.warning(f"User ID {user_id} does not have permission: {permission_name}.")
                    return False
        except Error as e:
            logging.error(f"Error checking permission {permission_name} for user ID {user_id}: {e}")
            raise
        finally:
            conn.close()

    def remove_role(self, role_id):
        """
        Remove a role from the system.
        :param role_id: ID of the role to remove.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM roles
                WHERE role_id = %s;
                """
                cursor.execute(query, (role_id,))
                if cursor.rowcount == 0:
                    logging.warning(f"No role found with ID: {role_id} to delete.")
                else:
                    conn.commit()
                    logging.info(f"Deleted role with ID: {role_id}.")
        except Error as e:
            logging.error(f"Error deleting role with ID {role_id}: {e}")
            raise
        finally:
            conn.close()

# Example Usage
if __name__ == "__main__":
    db_config = {
        "dbname": "inventory_db",
        "user": "inventory_user",
        "password": "inventory_pass",
        "host": "localhost",
        "port": 5432
    }

    access_control = AccessControlManagement(db_config)

    # Add a role
    role_id = access_control.add_role("Manager", "Manages inventory and user accounts.")

    # Add a permission
    permission_id = access_control.add_permission("VIEW_REPORTS", "Allows viewing of system reports.")

    # Assign the permission to the role
    access_control.assign_permission_to_role(role_id, permission_id)

    # Assign the role to a user
    access_control.assign_role_to_user(user_id=1, role_id=role_id)

    # Check if a user has a specific permission
    has_permission = access_control.check_user_permission(user_id=1, permission_name="VIEW_REPORTS")
    print(f"User has permission: {has_permission}")
