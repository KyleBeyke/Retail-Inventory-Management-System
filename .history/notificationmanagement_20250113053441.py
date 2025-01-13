import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from DataValidationManagement import DataValidationManagement

class NotificationManagement:
    """
    Handles the sending of notifications via email and other channels.
    """

    def __init__(self, smtp_server, smtp_port, sender_email, sender_password):
        """
        Initialize the NotificationManagement class.

        :param smtp_server: SMTP server address.
        :param smtp_port: SMTP server port.
        :param sender_email: Sender email address.
        :param sender_password: Password for the sender email.
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.data_validator = DataValidationManagement()

    def send_email_notification(self, recipient_email, subject, message):
        """
        Send an email notification to a recipient.

        :param recipient_email: The recipient's email address.
        :param subject: The subject of the email.
        :param message: The body of the email.
        :return: None
        """
        try:
            # Validate inputs
            self.data_validator.validate_email(recipient_email, "recipient_email")
            self.data_validator.validate_non_empty_string(subject, "subject")
            self.data_validator.validate_non_empty_string(message, "message")

            # Set up the email content
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            logging.info(f"Email sent to {recipient_email} with subject '{subject}'.")

        except Exception as e:
            logging.error(f"Failed to send email to {recipient_email}: {e}")
            raise

    def send_bulk_notifications(self, recipients, subject, message):
        """
        Send a bulk email notification to multiple recipients.

        :param recipients: A list of recipient email addresses.
        :param subject: The subject of the email.
        :param message: The body of the email.
        :return: None
        """
        try:
            # Validate inputs
            if not recipients or not isinstance(recipients, list):
                raise ValueError("Recipients must be a non-empty list.")

            for recipient in recipients:
                self.data_validator.validate_email(recipient, "recipient")

            self.data_validator.validate_non_empty_string(subject, "subject")
            self.data_validator.validate_non_empty_string(message, "message")

            for recipient in recipients:
                self.send_email_notification(recipient, subject, message)

            logging.info(f"Bulk notifications sent to {len(recipients)} recipients.")

        except Exception as e:
            logging.error(f"Failed to send bulk notifications: {e}")
            raise

    def log_notification(self, recipient, subject, message, channel="email"):
        """
        Log the notification details for auditing purposes.

        :param recipient: The recipient of the notification.
        :param subject: The subject of the notification.
        :param message: The content of the notification.
        :param channel: The channel used to send the notification (default is 'email').
        :return: None
        """
        try:
            self.data_validator.validate_email(recipient, "recipient")
            self.data_validator.validate_non_empty_string(subject, "subject")
            self.data_validator.validate_non_empty_string(message, "message")
            self.data_validator.validate_non_empty_string(channel, "channel")

            logging.info(f"Notification logged: Recipient: {recipient}, Subject: {subject}, Channel: {channel}")
        except Exception as e:
            logging.error(f"Failed to log notification: {e}")
            raise

# Example usage (to be removed in production):
if __name__ == "__main__":
    try:
        notification_manager = NotificationManagement(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender_email="your_email@example.com",
            sender_password="your_password"
        )

        # Send a single email
        notification_manager.send_email_notification(
            recipient_email="recipient@example.com",
            subject="Test Email",
            message="This is a test notification."
        )

        # Send bulk emails
        notification_manager.send_bulk_notifications(
            recipients=["recipient1@example.com", "recipient2@example.com"],
            subject="Bulk Test Email",
            message="This is a bulk test notification."
        )

    except Exception as e:
        logging.error(f"Error in NotificationManagement example usage: {e}")
