import logging
import psycopg2
from psycopg2 import sql, Error

# Configure logging
logging.basicConfig(
    filename="localization_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class LocalizationManagement:
    """
    A class to manage localization settings for the application, such as
    language, date/time format, and region-specific settings.
    """

    def __init__(self, db_config):
        """
        Initialize the LocalizationManagement class.
        :param db_config: Dictionary containing database connection details.
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

    def set_localization(self, language, date_format, time_format, currency):
        """
        Set localization settings in the database.
        :param language: Preferred language (e.g., "en-US").
        :param date_format: Date format string (e.g., "MM/DD/YYYY").
        :param time_format: Time format string (e.g., "HH:mm:ss").
        :param currency: Default currency (e.g., "USD").
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                INSERT INTO localization_settings (language, date_format, time_format, currency)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET language = EXCLUDED.language,
                    date_format = EXCLUDED.date_format,
                    time_format = EXCLUDED.time_format,
                    currency = EXCLUDED.currency;
                """
                cursor.execute(query, (language, date_format, time_format, currency))
                conn.commit()
                logging.info(f"Localization settings updated: Language={language}, Date Format={date_format}, "
                             f"Time Format={time_format}, Currency={currency}.")
        except Error as e:
            logging.error(f"Error updating localization settings: {e}")
            raise
        finally:
            conn.close()

    def get_localization(self):
        """
        Retrieve the current localization settings.
        :return: A dictionary containing localization settings.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                SELECT language, date_format, time_format, currency
                FROM localization_settings
                WHERE id = 1;
                """
                cursor.execute(query)
                result = cursor.fetchone()
                if result:
                    localization = {
                        "language": result[0],
                        "date_format": result[1],
                        "time_format": result[2],
                        "currency": result[3],
                    }
                    logging.info("Retrieved localization settings.")
                    return localization
                else:
                    logging.warning("No localization settings found.")
                    return None
        except Error as e:
            logging.error(f"Error retrieving localization settings: {e}")
            raise
        finally:
            conn.close()

    def update_localization(self, language=None, date_format=None, time_format=None, currency=None):
        """
        Update specific localization settings.
        :param language: New language (optional).
        :param date_format: New date format (optional).
        :param time_format: New time format (optional).
        :param currency: New currency (optional).
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                fields = []
                values = []

                if language:
                    fields.append("language = %s")
                    values.append(language)
                if date_format:
                    fields.append("date_format = %s")
                    values.append(date_format)
                if time_format:
                    fields.append("time_format = %s")
                    values.append(time_format)
                if currency:
                    fields.append("currency = %s")
                    values.append(currency)

                if fields:
                    query = sql.SQL("""
                        UPDATE localization_settings
                        SET {fields}
                        WHERE id = 1;
                    """).format(fields=sql.SQL(", ").join(map(sql.SQL, fields)))
                    cursor.execute(query, values)
                    conn.commit()
                    logging.info("Updated localization settings.")
                else:
                    logging.warning("No fields provided for updating localization settings.")
        except Error as e:
            logging.error(f"Error updating localization settings: {e}")
            raise
        finally:
            conn.close()

    def reset_to_defaults(self):
        """
        Reset localization settings to default values.
        :return: None.
        """
        try:
            conn = self._connect()
            with conn.cursor() as cursor:
                query = """
                UPDATE localization_settings
                SET language = 'en-US',
                    date_format = 'MM/DD/YYYY',
                    time_format = 'HH:mm:ss',
                    currency = 'USD'
                WHERE id = 1;
                """
                cursor.execute(query)
                conn.commit()
                logging.info("Localization settings reset to default values.")
        except Error as e:
            logging.error(f"Error resetting localization settings to default values: {e}")
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

    localization_manager = LocalizationManagement(db_config)

    # Set localization settings
    localization_manager.set_localization(language="en-US", date_format="MM/DD/YYYY", time_format="HH:mm:ss", currency="USD")

    # Get localization settings
    settings = localization_manager.get_localization()
    print("Current Localization Settings:", settings)

    # Update specific localization settings
    localization_manager.update_localization(currency="EUR")

    # Reset localization settings to defaults
    localization_manager.reset_to_defaults()
