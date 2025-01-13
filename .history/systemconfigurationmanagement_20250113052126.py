import json
import os
import logging

# Configure logging
logging.basicConfig(
    filename="system_configuration.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SystemConfigurationManagement:
    """
    Handles system-wide configuration management and preferences for the application.
    """

    def __init__(self, config_file="system_config.json"):
        """
        Initialize the SystemConfigurationManagement class.

        :param config_file: Path to the configuration file (default: 'system_config.json').
        """
        self.config_file = config_file
        self.config = {}

        # Load existing configuration if the file exists
        if os.path.exists(self.config_file):
            self.load_configuration()
        else:
            self.initialize_default_configuration()

    def initialize_default_configuration(self):
        """
        Initialize the configuration file with default values.
        """
        self.config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "dbname": "inventory_db",
                "user": "inventory_user",
                "password": "inventory_pass"
            },
            "logging": {
                "level": "INFO",
                "file": "application.log"
            },
            "synchronization": {
                "external_system_url": "https://example.com/api",
                "sync_interval": 60  # in minutes
            },
            "ui_preferences": {
                "theme": "light",
                "language": "en-US"
            }
        }
        self.save_configuration()
        logging.info("Initialized default configuration.")

    def load_configuration(self):
        """
        Load configuration from the configuration file.
        """
        try:
            with open(self.config_file, "r") as file:
                self.config = json.load(file)
            logging.info("Loaded configuration from file.")
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Failed to load configuration file: {e}")
            raise

    def save_configuration(self):
        """
        Save the current configuration to the configuration file.
        """
        try:
            with open(self.config_file, "w") as file:
                json.dump(self.config, file, indent=4)
            logging.info("Saved configuration to file.")
        except IOError as e:
            logging.error(f"Failed to save configuration file: {e}")
            raise

    def get_setting(self, section, key):
        """
        Retrieve a specific configuration setting.

        :param section: The configuration section (e.g., 'database').
        :param key: The configuration key (e.g., 'host').
        :return: The value of the configuration setting.
        """
        try:
            value = self.config[section][key]
            logging.info(f"Retrieved setting: {section}.{key} = {value}")
            return value
        except KeyError:
            logging.error(f"Configuration setting {section}.{key} not found.")
            raise

    def set_setting(self, section, key, value):
        """
        Update a specific configuration setting.

        :param section: The configuration section (e.g., 'database').
        :param key: The configuration key (e.g., 'host').
        :param value: The new value for the configuration setting.
        :return: None
        """
        try:
            if section not in self.config:
                self.config[section] = {}

            self.config[section][key] = value
            self.save_configuration()
            logging.info(f"Updated setting: {section}.{key} = {value}")
        except Exception as e:
            logging.error(f"Failed to update setting {section}.{key}: {e}")
            raise

    def reset_to_defaults(self):
        """
        Reset the configuration to default values.
        """
        self.initialize_default_configuration()
        logging.info("Configuration reset to default values.")

# Example usage
if __name__ == "__main__":
    config_manager = SystemConfigurationManagement()

    # Retrieve a setting
    db_host = config_manager.get_setting("database", "host")
    print(f"Database Host: {db_host}")

    # Update a setting
    config_manager.set_setting("ui_preferences", "theme", "dark")

    # Reset to defaults
    config_manager.reset_to_defaults()
