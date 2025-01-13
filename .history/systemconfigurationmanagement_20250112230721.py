import json
import os
import logging

# Configure logging
logging.basicConfig(
    filename="system_configuration_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SystemConfigurationManagement:
    """
    A class to manage system configurations, such as database settings, API keys,
    user preferences, and other global settings.
    """

    def __init__(self, config_file="system_config.json"):
        """
        Initialize the SystemConfigurationManagement class with a configuration file.
        :param config_file: Path to the configuration file.
        """
        self.config_file = config_file
        self.configurations = {}
        self.load_configurations()

    def load_configurations(self):
        """
        Load configurations from the configuration file.
        If the file does not exist, initialize with an empty configuration.
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as file:
                    self.configurations = json.load(file)
                    logging.info("Loaded system configurations successfully.")
            except Exception as e:
                logging.error(f"Error loading configurations: {e}")
                raise
        else:
            self.configurations = {}
            logging.warning(f"Configuration file {self.config_file} does not exist. Using default settings.")

    def save_configurations(self):
        """
        Save the current configurations to the configuration file.
        """
        try:
            with open(self.config_file, "w") as file:
                json.dump(self.configurations, file, indent=4)
                logging.info("System configurations saved successfully.")
        except Exception as e:
            logging.error(f"Error saving configurations: {e}")
            raise

    def get_configuration(self, key, default=None):
        """
        Retrieve a configuration value by its key.
        :param key: The configuration key.
        :param default: Default value if the key does not exist.
        :return: The value of the configuration key or the default value.
        """
        value = self.configurations.get(key, default)
        if key in self.configurations:
            logging.info(f"Retrieved configuration for key: {key}.")
        else:
            logging.warning(f"Configuration key {key} not found. Returning default value.")
        return value

    def set_configuration(self, key, value):
        """
        Set a configuration value for a given key.
        :param key: The configuration key.
        :param value: The configuration value.
        :return: None.
        """
        self.configurations[key] = value
        logging.info(f"Set configuration for key: {key} to value: {value}.")
        self.save_configurations()

    def delete_configuration(self, key):
        """
        Delete a configuration by its key.
        :param key: The configuration key to delete.
        :return: None.
        """
        if key in self.configurations:
            del self.configurations[key]
            logging.info(f"Deleted configuration for key: {key}.")
            self.save_configurations()
        else:
            logging.warning(f"Configuration key {key} does not exist. Cannot delete.")

    def reset_configurations(self):
        """
        Reset all configurations to default (empty) and save to the file.
        """
        self.configurations = {}
        self.save_configurations()
        logging.info("All configurations have been reset to default.")

# Example Usage
if __name__ == "__main__":
    config_manager = SystemConfigurationManagement()

    # Set a new configuration
    config_manager.set_configuration("database_host", "localhost")
    config_manager.set_configuration("database_port", 5432)

    # Get a configuration value
    db_host = config_manager.get_configuration("database_host")
    print(f"Database Host: {db_host}")

    # Delete a configuration
    config_manager.delete_configuration("database_port")

    # Reset all configurations
    config_manager.reset_configurations()
