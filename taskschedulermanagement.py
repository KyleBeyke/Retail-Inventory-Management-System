import schedule
import time
import threading
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename="task_scheduler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TaskSchedulerManagement:
    """
    A class to manage task scheduling for the inventory management system.
    Provides functionality for scheduling, canceling, and executing periodic tasks.
    """

    def __init__(self):
        """
        Initialize the TaskSchedulerManagement class with a task registry.
        """
        self.task_registry = {}
        self.scheduler_thread = None
        self.stop_thread = threading.Event()

    def add_task(self, task_name, task_function, schedule_time, interval_type="daily"):
        """
        Add a new task to the scheduler.
        :param task_name: Name of the task.
        :param task_function: The function to execute for the task.
        :param schedule_time: The time for scheduling the task (e.g., "14:00").
        :param interval_type: Interval type for the task ("daily", "hourly", etc.).
        :return: None
        """
        if task_name in self.task_registry:
            logging.warning(f"Task '{task_name}' already exists. Skipping addition.")
            return

        try:
            if interval_type == "daily":
                schedule.every().day.at(schedule_time).do(task_function)
            elif interval_type == "hourly":
                schedule.every().hour.at(schedule_time).do(task_function)
            elif interval_type == "weekly":
                schedule.every().week.at(schedule_time).do(task_function)
            else:
                logging.error(f"Unsupported interval type '{interval_type}' for task '{task_name}'.")
                return

            self.task_registry[task_name] = {
                "task_function": task_function,
                "schedule_time": schedule_time,
                "interval_type": interval_type,
            }

            logging.info(f"Task '{task_name}' added to the scheduler at {schedule_time} ({interval_type}).")
        except Exception as e:
            logging.error(f"Error adding task '{task_name}': {e}")

    def remove_task(self, task_name):
        """
        Remove a task from the scheduler.
        :param task_name: Name of the task to remove.
        :return: None
        """
        if task_name not in self.task_registry:
            logging.warning(f"Task '{task_name}' not found. Cannot remove.")
            return

        try:
            # Cancel the scheduled task
            schedule.clear(task_name)
            del self.task_registry[task_name]
            logging.info(f"Task '{task_name}' removed from the scheduler.")
        except Exception as e:
            logging.error(f"Error removing task '{task_name}': {e}")

    def list_tasks(self):
        """
        List all scheduled tasks.
        :return: A list of task names and their details.
        """
        return [
            {"task_name": task_name, **details}
            for task_name, details in self.task_registry.items()
        ]

    def start_scheduler(self):
        """
        Start the scheduler in a separate thread.
        :return: None
        """
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            logging.warning("Scheduler is already running.")
            return

        self.stop_thread.clear()

        def run_scheduler():
            logging.info("Scheduler started.")
            while not self.stop_thread.is_set():
                schedule.run_pending()
                time.sleep(1)
            logging.info("Scheduler stopped.")

        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()

    def stop_scheduler(self):
        """
        Stop the scheduler thread.
        :return: None
        """
        if not self.scheduler_thread or not self.scheduler_thread.is_alive():
            logging.warning("Scheduler is not running.")
            return

        self.stop_thread.set()
        self.scheduler_thread.join()

    def execute_task_now(self, task_name):
        """
        Execute a scheduled task immediately.
        :param task_name: Name of the task to execute.
        :return: None
        """
        if task_name not in self.task_registry:
            logging.warning(f"Task '{task_name}' not found. Cannot execute.")
            return

        try:
            task_function = self.task_registry[task_name]["task_function"]
            task_function()
            logging.info(f"Executed task '{task_name}' immediately.")
        except Exception as e:
            logging.error(f"Error executing task '{task_name}': {e}")

# Example Usage
if __name__ == "__main__":
    def example_task():
        print(f"Example task executed at {datetime.now()}")

    task_manager = TaskSchedulerManagement()

    # Add a daily task
    task_manager.add_task("daily_backup", example_task, "14:00", "daily")

    # List tasks
    print(task_manager.list_tasks())

    # Start the scheduler
    task_manager.start_scheduler()

    # Execute a task immediately
    task_manager.execute_task_now("daily_backup")

    # Stop the scheduler after some time (for demonstration purposes)
    time.sleep(5)
    task_manager.stop_scheduler()
