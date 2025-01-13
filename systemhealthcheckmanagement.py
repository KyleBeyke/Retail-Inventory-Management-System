import logging
import psutil
import platform
import os
import shutil
import socket

# Configure logging
logging.basicConfig(
    filename="system_health_check.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class SystemHealthCheckManagement:
    """
    A class to monitor and provide system health checks, including CPU usage, memory usage,
    disk space, network connectivity, and service statuses.
    """

    def __init__(self):
        """
        Initialize the SystemHealthCheckManagement class.
        """
        logging.info("SystemHealthCheckManagement initialized.")

    def check_cpu_usage(self, threshold=80):
        """
        Check the current CPU usage and determine if it exceeds the threshold.
        :param threshold: CPU usage percentage threshold to trigger an alert.
        :return: Dictionary with CPU usage information.
        """
        cpu_usage = psutil.cpu_percent(interval=1)
        status = "OK" if cpu_usage < threshold else "High Usage"
        logging.info(f"CPU Usage: {cpu_usage}% - Status: {status}")
        return {"cpu_usage": cpu_usage, "status": status}

    def check_memory_usage(self, threshold=80):
        """
        Check the current memory usage and determine if it exceeds the threshold.
        :param threshold: Memory usage percentage threshold to trigger an alert.
        :return: Dictionary with memory usage information.
        """
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        status = "OK" if memory_usage < threshold else "High Usage"
        logging.info(f"Memory Usage: {memory_usage}% - Status: {status}")
        return {"memory_usage": memory_usage, "status": status}

    def check_disk_space(self, path="/", threshold=80):
        """
        Check the disk space usage for the specified path.
        :param path: Filesystem path to check disk usage.
        :param threshold: Disk usage percentage threshold to trigger an alert.
        :return: Dictionary with disk space usage information.
        """
        disk = shutil.disk_usage(path)
        used_percent = (disk.used / disk.total) * 100
        status = "OK" if used_percent < threshold else "Low Space"
        logging.info(f"Disk Usage for {path}: {used_percent:.2f}% - Status: {status}")
        return {"path": path, "used_percent": used_percent, "status": status}

    def check_network_connectivity(self, host="8.8.8.8", port=53, timeout=3):
        """
        Check network connectivity by attempting to connect to a known host and port.
        :param host: Host to connect to (default is Google's public DNS server).
        :param port: Port to connect to.
        :param timeout: Connection timeout in seconds.
        :return: Dictionary with network connectivity status.
        """
        try:
            socket.create_connection((host, port), timeout=timeout)
            logging.info("Network connectivity check passed.")
            return {"status": "Connected"}
        except Exception as e:
            logging.error(f"Network connectivity check failed: {e}")
            return {"status": "Disconnected", "error": str(e)}

    def get_system_info(self):
        """
        Retrieve basic system information such as OS, architecture, and hostname.
        :return: Dictionary with system information.
        """
        system_info = {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.architecture()[0],
            "hostname": socket.gethostname()
        }
        logging.info(f"System Info: {system_info}")
        return system_info

    def check_services(self, service_names):
        """
        Check the status of specified system services.
        :param service_names: List of service names to check.
        :return: Dictionary with service statuses.
        """
        services_status = {}
        for service_name in service_names:
            try:
                service = psutil.win_service_get(service_name)
                status = service.status()
                services_status[service_name] = status
                logging.info(f"Service '{service_name}' status: {status}")
            except Exception as e:
                services_status[service_name] = "Not Found"
                logging.warning(f"Service '{service_name}' not found: {e}")
        return services_status

    def run_full_health_check(self, disk_path="/", cpu_threshold=80, memory_threshold=80, service_names=None):
        """
        Run a full system health check, including CPU, memory, disk, and optional services.
        :param disk_path: Path to check disk usage (default is root).
        :param cpu_threshold: Threshold for CPU usage.
        :param memory_threshold: Threshold for memory usage.
        :param service_names: List of services to check (optional).
        :return: Dictionary with the full health check report.
        """
        report = {
            "system_info": self.get_system_info(),
            "cpu_usage": self.check_cpu_usage(cpu_threshold),
            "memory_usage": self.check_memory_usage(memory_threshold),
            "disk_usage": self.check_disk_space(disk_path),
            "network_connectivity": self.check_network_connectivity()
        }

        if service_names:
            report["service_statuses"] = self.check_services(service_names)

        logging.info(f"Full health check report: {report}")
        return report


# Example usage
if __name__ == "__main__":
    health_check_manager = SystemHealthCheckManagement()
    health_report = health_check_manager.run_full_health_check(service_names=["postgresql", "nginx"])
    print(health_report)
