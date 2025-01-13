import logging
import re

# Configure logging
logging.basicConfig(
    filename="data_validation_management.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class DataValidationManagement:
    """
    A class to manage and enforce data validation throughout the system,
    ensuring data integrity and consistency.
    """

    def __init__(self):
        """
        Initialize the DataValidationManagement class.
        """
        logging.info("DataValidationManagement initialized.")

    def validate_email(self, email):
        """
        Validate an email address.
        :param email: The email address to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = re.match(pattern, email) is not None
        if is_valid:
            logging.info(f"Email validation passed: {email}")
        else:
            logging.warning(f"Email validation failed: {email}")
        return is_valid

    def validate_phone_number(self, phone_number):
        """
        Validate a phone number (basic format check).
        :param phone_number: The phone number to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^\+?[0-9]{7,15}$'
        is_valid = re.match(pattern, phone_number) is not None
        if is_valid:
            logging.info(f"Phone number validation passed: {phone_number}")
        else:
            logging.warning(f"Phone number validation failed: {phone_number}")
        return is_valid

    def validate_positive_integer(self, value, field_name="Value"):
        """
        Validate that a value is a positive integer.
        :param value: The value to validate.
        :param field_name: Optional field name for logging.
        :return: True if valid, False otherwise.
        """
        is_valid = isinstance(value, int) and value > 0
        if is_valid:
            logging.info(f"{field_name} validation passed: {value}")
        else:
            logging.warning(f"{field_name} validation failed: {value}")
        return is_valid

    def validate_string_length(self, string, min_length, max_length, field_name="String"):
        """
        Validate that a string's length falls within a specified range.
        :param string: The string to validate.
        :param min_length: Minimum acceptable length.
        :param max_length: Maximum acceptable length.
        :param field_name: Optional field name for logging.
        :return: True if valid, False otherwise.
        """
        if not isinstance(string, str):
            logging.warning(f"{field_name} validation failed: Not a string.")
            return False

        is_valid = min_length <= len(string) <= max_length
        if is_valid:
            logging.info(f"{field_name} length validation passed: {len(string)} characters.")
        else:
            logging.warning(
                f"{field_name} length validation failed: {len(string)} characters "
                f"(expected between {min_length} and {max_length})."
            )
        return is_valid

    def validate_sku(self, sku):
        """
        Validate a product SKU (alphanumeric and optional dashes).
        :param sku: The SKU to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^[a-zA-Z0-9-]+$'
        is_valid = re.match(pattern, sku) is not None
        if is_valid:
            logging.info(f"SKU validation passed: {sku}")
        else:
            logging.warning(f"SKU validation failed: {sku}")
        return is_valid

    def validate_date_format(self, date, date_format="%Y-%m-%d"):
        """
        Validate that a date string matches a specified format.
        :param date: The date string to validate.
        :param date_format: The expected date format (default: '%Y-%m-%d').
        :return: True if valid, False otherwise.
        """
        from datetime import datetime
        try:
            datetime.strptime(date, date_format)
            logging.info(f"Date validation passed: {date}")
            return True
        except ValueError:
            logging.warning(f"Date validation failed: {date} (expected format: {date_format})")
            return False

    def validate_percentage(self, value, field_name="Percentage"):
        """
        Validate that a value is a percentage (0-100 inclusive).
        :param value: The value to validate.
        :param field_name: Optional field name for logging.
        :return: True if valid, False otherwise.
        """
        is_valid = isinstance(value, (int, float)) and 0 <= value <= 100
        if is_valid:
            logging.info(f"{field_name} validation passed: {value}%")
        else:
            logging.warning(f"{field_name} validation failed: {value}% (expected 0-100).")
        return is_valid

    def validate_currency_code(self, currency_code):
        """
        Validate a three-letter ISO currency code.
        :param currency_code: The currency code to validate.
        :return: True if valid, False otherwise.
        """
        pattern = r'^[A-Z]{3}$'
        is_valid = re.match(pattern, currency_code) is not None
        if is_valid:
            logging.info(f"Currency code validation passed: {currency_code}")
        else:
            logging.warning(f"Currency code validation failed: {currency_code}")
        return is_valid

    def validate_json_format(self, json_string):
        """
        Validate that a string is a valid JSON.
        :param json_string: The JSON string to validate.
        :return: True if valid, False otherwise.
        """
        import json
        try:
            json.loads(json_string)
            logging.info("JSON validation passed.")
            return True
        except json.JSONDecodeError:
            logging.warning("JSON validation failed.")
            return False

# Example Usage
if __name__ == "__main__":
    validator = DataValidationManagement()

    # Email validation
    print("Email valid:", validator.validate_email("test@example.com"))

    # Phone number validation
    print("Phone number valid:", validator.validate_phone_number("+1234567890"))

    # Positive integer validation
    print("Positive integer valid:", validator.validate_positive_integer(10))

    # String length validation
    print("String length valid:", validator.validate_string_length("example", 3, 10))

    # SKU validation
    print("SKU valid:", validator.validate_sku("ABC-123"))

    # Date validation
    print("Date valid:", validator.validate_date_format("2025-01-15"))

    # Percentage validation
    print("Percentage valid:", validator.validate_percentage(85))

    # Currency code validation
    print("Currency code valid:", validator.validate_currency_code("USD"))

    # JSON validation
    print("JSON valid:", validator.validate_json_format('{"key": "value"}'))
