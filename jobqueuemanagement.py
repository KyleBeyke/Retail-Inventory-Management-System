import psycopg2
from psycopg2 import sql, Error
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="job_queue_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class JobQueueManagement:
    """
    A class to manage background job queues, including adding, retrieving, processing,
    and monitoring scheduled and queued tasks.
    """

    def __init__(self, db_config):
        """
        Initialize the JobQueueManagement class with database connection configuration.
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

    def add_job(self, job_type, job_data, scheduled_time=None, priority=1):
        """
        Add a job to the queue.
        :param job_type: The type of job (e.g., "data_sync", "report_generation").
        :param job_data: Additional data related to the job (e.g., parameters or JSON payload).
        :param scheduled_time: When the job should be executed (optional).
        :param priority: Priority of the job (lower number indicates higher priority, default is 1).
        :return: The ID of the newly added job.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO job_queue (job_type, job_data, scheduled_time, priority, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING job_id;
                """
                cursor.execute(query, (job_type, job_data, scheduled_time, priority, "pending", datetime.now()))
                job_id = cursor.fetchone()[0]
                conn.commit()
                logging.info(f"Added job ID {job_id} of type '{job_type}' to the queue.")
                return job_id
        except Error as e:
            logging.error(f"Error adding job to the queue: {e}")
            raise
        finally:
            conn.close()

    def get_pending_jobs(self, limit=10):
        """
        Retrieve pending jobs from the queue.
        :param limit: The maximum number of jobs to retrieve.
        :return: A list of pending jobs.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT job_id, job_type, job_data, scheduled_time, priority, status, created_at
                FROM job_queue
                WHERE status = 'pending'
                ORDER BY priority ASC, scheduled_time ASC NULLS LAST
                LIMIT %s;
                """
                cursor.execute(query, (limit,))
                jobs = cursor.fetchall()
                job_list = [
                    {
                        "job_id": job[0],
                        "job_type": job[1],
                        "job_data": job[2],
                        "scheduled_time": job[3],
                        "priority": job[4],
                        "status": job[5],
                        "created_at": job[6],
                    }
                    for job in jobs
                ]
                logging.info(f"Retrieved {len(job_list)} pending jobs.")
                return job_list
        except Error as e:
            logging.error(f"Error retrieving pending jobs: {e}")
            raise
        finally:
            conn.close()

    def update_job_status(self, job_id, status):
        """
        Update the status of a job.
        :param job_id: The ID of the job to update.
        :param status: The new status of the job (e.g., "in_progress", "completed", "failed").
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE job_queue
                SET status = %s, updated_at = %s
                WHERE job_id = %s;
                """
                cursor.execute(query, (status, datetime.now(), job_id))
                conn.commit()
                logging.info(f"Updated job ID {job_id} to status '{status}'.")
        except Error as e:
            logging.error(f"Error updating status for job ID {job_id}: {e}")
            raise
        finally:
            conn.close()

    def delete_completed_jobs(self):
        """
        Delete jobs that have been completed from the queue.
        :return: The number of jobs deleted.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                DELETE FROM job_queue
                WHERE status = 'completed';
                """
                cursor.execute(query)
                deleted_count = cursor.rowcount
                conn.commit()
                logging.info(f"Deleted {deleted_count} completed jobs from the queue.")
                return deleted_count
        except Error as e:
            logging.error(f"Error deleting completed jobs: {e}")
            raise
        finally:
            conn.close()

    def retry_failed_jobs(self, limit=10):
        """
        Retry failed jobs by setting their status back to 'pending'.
        :param limit: The maximum number of failed jobs to retry.
        :return: The number of jobs retried.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE job_queue
                SET status = 'pending', updated_at = %s
                WHERE status = 'failed'
                ORDER BY updated_at ASC
                LIMIT %s;
                """
                cursor.execute(query, (datetime.now(), limit))
                retried_count = cursor.rowcount
                conn.commit()
                logging.info(f"Retried {retried_count} failed jobs.")
                return retried_count
        except Error as e:
            logging.error(f"Error retrying failed jobs: {e}")
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

    job_manager = JobQueueManagement(db_config)

    # Add a job
    job_id = job_manager.add_job("data_sync", '{"target": "supplier_data"}')

    # Get pending jobs
    pending_jobs = job_manager.get_pending_jobs()
    print(pending_jobs)

    # Update job status
    job_manager.update_job_status(job_id, "in_progress")

    # Retry failed jobs
    retried_jobs = job_manager.retry_failed_jobs()

    # Delete completed jobs
    deleted_jobs = job_manager.delete_completed_jobs()
