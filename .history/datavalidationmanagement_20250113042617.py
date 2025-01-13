import re
from datetime import datetime


class DataValidationManagement:
    """
    A class for validating various types of data to ensure data integrity across the system.
    """

    @staticmethod
    def validate_non_empty_string(value, field_name="Field"):
        """
        Validate that a value is a non-empty string.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, str) and value.strip():
            return True
        raise ValueError(f"{field_name} must be a non-empty string.")

    @staticmethod
    def validate_positive_integer(value, field_name="Field"):
        """
        Validate that a value is a positive integer.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, int) and value > 0:
            return True
        raise ValueError(f"{field_name} must be a positive integer.")

    @staticmethod
    def validate_positive_number(value, field_name="Field"):
        """
        Validate that a value is a positive number (int or float).
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, (int, float)) and value > 0:
            return True
        raise ValueError(f"{field_name} must be a positive number.")

    @staticmethod
    def validate_email(value, field_name="Email"):
        """
        Validate that a value is a valid email address.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if re.match(email_regex, value):
            return True
        raise ValueError(f"{field_name} must be a valid email address.")

    @staticmethod
    def validate_date(value, field_name="Date", date_format="%Y-%m-%d"):
        """
        Validate that a value is a valid date in the given format.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :param date_format: The expected date format (default is '%Y-%m-%d').
        :return: True if valid, raises ValueError if invalid.
        """
        try:
            datetime.strptime(value, date_format)
            return True
        except ValueError:
            raise ValueError(f"{field_name} must be a valid date in the format {date_format}.")

    @staticmethod
    def validate_sku(value, field_name="SKU"):
        """
        Validate that a value is a valid SKU (alphanumeric string).
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        sku_regex = r"^[a-zA-Z0-9-_]+$"
        if re.match(sku_regex, value):
            return True
        raise ValueError(f"{field_name} must be a valid SKU (alphanumeric with dashes or underscores).")

    @staticmethod
    def validate_percentage(value, field_name="Percentage"):
        """
        Validate that a value is a valid percentage (0-100).
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, (int, float)) and 0 <= value <= 100:
            return True
        raise ValueError(f"{field_name} must be a percentage between 0 and 100.")

    @staticmethod
    def validate_phone_number(value, field_name="Phone Number"):
        """
        Validate that a value is a valid phone number (digits, with optional dashes or spaces).
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        phone_regex = r"^\+?[\d\s\-()]+$"
        if re.match(phone_regex, value):
            return True
        raise ValueError(f"{field_name} must be a valid phone number.")

    @staticmethod
    def validate_id(value, field_name="ID"):
        """
        Validate that a value is a valid positive integer ID.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        return DataValidationManagement.validate_positive_integer(value, field_name)

    @staticmethod
    def validate_non_negative_integer(value, field_name="Field"):
        """
        Validate that a value is a non-negative integer.
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, int) and value >= 0:
            return True
        raise ValueError(f"{field_name} must be a non-negative integer.")

    @staticmethod
    def validate_non_negative_number(value, field_name="Field"):
        """
        Validate that a value is a non-negative number (int or float).
        :param value: The value to validate.
        :param field_name: The name of the field for error messages.
        :return: True if valid, raises ValueError if invalid.
        """
        if isinstance(value, (int, float)) and value >= 0:
            return True
        raise ValueError(f"{field_name} must be a non-negative number.")
