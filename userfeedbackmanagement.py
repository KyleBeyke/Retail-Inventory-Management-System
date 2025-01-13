import psycopg2
from psycopg2 import sql, Error
import logging

# Configure logging
logging.basicConfig(
    filename="user_feedback_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class UserFeedbackManagement:
    """
    A class to manage user feedback, including submitting, retrieving, and updating
    feedback reports from users for the inventory management system.
    """

    def __init__(self, db_config):
        """
        Initialize the UserFeedbackManagement class with database connection configuration.
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

    def submit_feedback(self, user_id, feedback_text, feedback_type="General"):
        """
        Submit a new feedback report from a user.
        :param user_id: The ID of the user submitting the feedback.
        :param feedback_text: The text of the feedback.
        :param feedback_type: The type of feedback (e.g., 'Bug', 'Feature Request', 'General').
        :return: The ID of the newly submitted feedback.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO user_feedback (user_id, feedback_text, feedback_type, feedback_status)
                VALUES (%s, %s, %s, 'Open')
                RETURNING feedback_id;
                """
                cursor.execute(query, (user_id, feedback_text, feedback_type))
                feedback_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Feedback submitted by user {user_id} with ID: {feedback_id}.")
                return feedback_id
        except Error as e:
            logging.error(f"Error submitting feedback from user {user_id}: {e}")
            raise
        finally:
            conn.close()

    def retrieve_feedback(self, feedback_id):
        """
        Retrieve a specific feedback report by its ID.
        :param feedback_id: The ID of the feedback to retrieve.
        :return: A dictionary containing feedback details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT feedback_id, user_id, feedback_text, feedback_type, feedback_status, created_at
                FROM user_feedback
                WHERE feedback_id = %s;
                """
                cursor.execute(query, (feedback_id,))
                result = cursor.fetchone()
                if result:
                    feedback_details = {
                        "feedback_id": result[0],
                        "user_id": result[1],
                        "feedback_text": result[2],
                        "feedback_type": result[3],
                        "feedback_status": result[4],
                        "created_at": result[5]
                    }
                    logging.info(f"Retrieved feedback with ID: {feedback_id}.")
                    return feedback_details
                else:
                    logging.warning(f"No feedback found with ID: {feedback_id}.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving feedback with ID {feedback_id}: {e}")
            raise
        finally:
            conn.close()

    def update_feedback_status(self, feedback_id, status):
        """
        Update the status of a feedback report.
        :param feedback_id: The ID of the feedback to update.
        :param status: The new status (e.g., 'Open', 'In Progress', 'Resolved').
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE user_feedback
                SET feedback_status = %s
                WHERE feedback_id = %s;
                """
                cursor.execute(query, (status, feedback_id))
                if cursor.rowcount > 0:
                    conn.commit()
                    logging.info(f"Updated feedback ID {feedback_id} to status: {status}.")
                else:
                    logging.warning(f"No feedback found with ID: {feedback_id} to update.")
        except Error as e:
            logging.error(f"Error updating feedback status for ID {feedback_id}: {e}")
            raise
        finally:
            conn.close()

    def list_feedback(self, status_filter=None, feedback_type_filter=None):
        """
        List feedback reports with optional filters.
        :param status_filter: Filter feedback by status (optional).
        :param feedback_type_filter: Filter feedback by type (optional).
        :return: A list of dictionaries containing feedback details.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                filters = []
                values = []

                if status_filter:
                    filters.append("feedback_status = %s")
                    values.append(status_filter)
                if feedback_type_filter:
                    filters.append("feedback_type = %s")
                    values.append(feedback_type_filter)

                filter_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
                query = f"""
                SELECT feedback_id, user_id, feedback_text, feedback_type, feedback_status, created_at
                FROM user_feedback
                {filter_clause}
                ORDER BY created_at DESC;
                """
                cursor.execute(query, values)
                results = cursor.fetchall()
                feedback_list = [
                    {
                        "feedback_id": row[0],
                        "user_id": row[1],
                        "feedback_text": row[2],
                        "feedback_type": row[3],
                        "feedback_status": row[4],
                        "created_at": row[5]
                    }
                    for row in results
                ]
                logging.info("Retrieved list of feedback reports.")
                return feedback_list
        except Error as e:
            logging.error("Error listing feedback reports: {e}")
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

    feedback_manager = UserFeedbackManagement(db_config)

    # Submit feedback
    feedback_id = feedback_manager.submit_feedback(
        user_id=1,
        feedback_text="The inventory search feature is slow.",
        feedback_type="Bug"
    )
    print(f"Submitted feedback ID: {feedback_id}")

    # Retrieve feedback
    feedback = feedback_manager.retrieve_feedback(feedback_id)
    print("Feedback details:", feedback)

    # Update feedback status
    feedback_manager.update_feedback_status(feedback_id, "Resolved")

    # List feedback
    all_feedback = feedback_manager.list_feedback()
    print("All Feedback:", all_feedback)
