import psutil
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename="system_monitoring.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class SystemMonitoringManagement:
    """
    A class to monitor and track the health, performance, and activity of the system,
    including CPU, memory, disk usage, and network metrics.
    """

    def __init__(self):
        """
        Initialize the SystemMonitoringManagement class.
        """
        logging.info("SystemMonitoringManagement initialized.")

    def get_cpu_usage(self):
        """
        Get the current CPU usage percentage.
        :return: Current CPU usage as a percentage.
        """
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            logging.info(f"CPU usage retrieved: {cpu_usage}%")
            return cpu_usage
        except Exception as e:
            logging.error(f"Error retrieving CPU usage: {e}")
            raise

    def get_memory_usage(self):
        """
        Get the current memory usage details.
        :return: A dictionary containing total, available, used, and percentage of memory usage.
        """
        try:
            memory_info = psutil.virtual_memory()
            memory_usage = {
                "total": memory_info.total,
                "available": memory_info.available,
                "used": memory_info.used,
                "percentage": memory_info.percent
            }
            logging.info(f"Memory usage retrieved: {memory_usage}")
            return memory_usage
        except Exception as e:
            logging.error(f"Error retrieving memory usage: {e}")
            raise

    def get_disk_usage(self, path="/"):
        """
        Get the current disk usage details for the specified path.
        :param path: The path to check disk usage for (default is the root path).
        :return: A dictionary containing total, used, free, and percentage of disk usage.
        """
        try:
            disk_info = psutil.disk_usage(path)
            disk_usage = {
                "total": disk_info.total,
                "used": disk_info.used,
                "free": disk_info.free,
                "percentage": disk_info.percent
            }
            logging.info(f"Disk usage for path '{path}' retrieved: {disk_usage}")
            return disk_usage
        except Exception as e:
            logging.error(f"Error retrieving disk usage for path '{path}': {e}")
            raise

    def get_network_stats(self):
        """
        Get the current network I/O statistics.
        :return: A dictionary containing bytes sent and received.
        """
        try:
            net_io = psutil.net_io_counters()
            network_stats = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_received": net_io.bytes_recv
            }
            logging.info(f"Network stats retrieved: {network_stats}")
            return network_stats
        except Exception as e:
            logging.error(f"Error retrieving network statistics: {e}")
            raise

    def log_system_metrics(self):
        """
        Log a snapshot of current system metrics to the monitoring log.
        :return: None
        """
        try:
            cpu = self.get_cpu_usage()
            memory = self.get_memory_usage()
            disk = self.get_disk_usage()
            network = self.get_network_stats()

            logging.info("System metrics snapshot:")
            logging.info(f"CPU Usage: {cpu}%")
            logging.info(f"Memory Usage: {memory}")
            logging.info(f"Disk Usage: {disk}")
            logging.info(f"Network Stats: {network}")
        except Exception as e:
            logging.error(f"Error logging system metrics: {e}")
            raise

    def monitor_system_health(self):
        """
        Monitor and report on the system's overall health based on metrics.
        :return: A dictionary summarizing system health status.
        """
        try:
            health_status = {
                "cpu_usage": self.get_cpu_usage(),
                "memory_usage": self.get_memory_usage(),
                "disk_usage": self.get_disk_usage(),
                "network_stats": self.get_network_stats(),
                "timestamp": datetime.now().isoformat()
            }
            logging.info(f"System health status: {health_status}")
            return health_status
        except Exception as e:
            logging.error(f"Error monitoring system health: {e}")
            raise


# Example Usage
if __name__ == "__main__":
    monitor = SystemMonitoringManagement()

    # Retrieve and log individual metrics
    print("CPU Usage:", monitor.get_cpu_usage())
    print("Memory Usage:", monitor.get_memory_usage())
    print("Disk Usage:", monitor.get_disk_usage())
    print("Network Stats:", monitor.get_network_stats())

    # Log a snapshot of system metrics
    monitor.log_system_metrics()

    # Monitor and display overall system health
    health_status = monitor.monitor_system_health()
    print("System Health Status:", health_status)
