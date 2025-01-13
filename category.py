import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="category_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Category:
    """
    A class to handle operations related to product categories in the inventory management system.
    """

    def __init__(self, db_config):
        """
        Initialize the Category class with database connection configuration.
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

    def create_category(self, name, description=None):
        """
        Create a new category in the database.
        :param name: Name of the category.
        :param description: Optional description of the category.
        :return: ID of the newly created category.
        """
        query = """
        INSERT INTO categories (name, description)
        VALUES (%s, %s)
        RETURNING id;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (name, description))
                category_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Category created: {name} (ID: {category_id})")
                return category_id
        except Error as e:
            logging.error(f"Error creating category '{name}': {e}")
            raise
        finally:
            conn.close()

    def get_category_by_id(self, category_id):
        """
        Retrieve a category by its ID.
        :param category_id: The ID of the category to retrieve.
        :return: A dictionary containing the category details or None if not found.
        """
        query = """
        SELECT id, name, description
        FROM categories
        WHERE id = %s;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (category_id,))
                result = cursor.fetchone()
                if result:
                    category = {"id": result[0], "name": result[1], "description": result[2]}
                    logging.info(f"Category retrieved: {category}")
                    return category
                else:
                    logging.warning(f"Category with ID {category_id} not found.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving category with ID {category_id}: {e}")
            raise
        finally:
            conn.close()

    def update_category(self, category_id, name=None, description=None):
        """
        Update an existing category's name or description.
        :param category_id: ID of the category to update.
        :param name: New name for the category (optional).
        :param description: New description for the category (optional).
        :return: Boolean indicating whether the update was successful.
        """
        updates = []
        values = []

        if name:
            updates.append("name = %s")
            values.append(name)
        if description:
            updates.append("description = %s")
            values.append(description)

        if not updates:
            logging.warning("No fields provided to update.")
            return False

        query = sql.SQL("UPDATE categories SET {fields} WHERE id = %s").format(
            fields=sql.SQL(", ").join(map(sql.SQL, updates))
        )
        values.append(category_id)

        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, values)
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Category updated (ID: {category_id})")
                    return True
                else:
                    logging.warning(f"No category found with ID {category_id}. Update failed.")
                    return False
        except Error as e:
            logging.error(f"Error updating category with ID {category_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_category(self, category_id):
        """
        Delete a category by its ID.
        :param category_id: ID of the category to delete.
        :return: Boolean indicating whether the deletion was successful.
        """
        query = """
        DELETE FROM categories
        WHERE id = %s;
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                cursor.execute(query, (category_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Category deleted (ID: {category_id})")
                    return True
                else:
                    logging.warning(f"No category found with ID {category_id}. Deletion failed.")
                    return False
        except Error as e:
            logging.error(f"Error deleting category with ID {category_id}: {e}")
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

    category_manager = Category(db_config)

    # Create a new category
    new_category_id = category_manager.create_category(name="Electronics", description="Gadgets and devices")

    # Retrieve the newly created category
    category = category_manager.get_category_by_id(new_category_id)
    print(category)

    # Update the category
    category_manager.update_category(new_category_id, name="Updated Electronics", description="Updated description")

    # Delete the category
    category_manager.delete_category(new_category_id)
