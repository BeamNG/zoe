import logging
import os
import subprocess


class EmailSender:
    """
    Class for sending emails 
    """
    def __init__(self):

        self.logger = logging.getLogger(self.__class__.__name__)

    def send_email(self, to_address: str, subject: str, body: str, attachment_path=None):
        """
        Send an email to the specified address
        :param to_address: The email address to send the email to
        :param subject: The subject of the email
        :param body: The body of the email
        :param attachment_path: The path to the attachment file
        """
        # Check if the attachment file exists
        if attachment_path is not None and not os.path.exists(attachment_path):
            self.logger.error(f"Error: {attachment_path} does not exist")
            return
        # Build the command to send the email
        command = f'mail -s "{subject}" {to_address}'
        if attachment_path is not None:
            command += f' -a "{attachment_path}"'
        # Execute the command
        try:
            subprocess.run(command, input=body.encode(), shell=True, check=True)
            self.logger.info(f"Email sent to {to_address}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error: {e}")

#Todo: get a list of emails or email addresses from the commit?

class EmailClient:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.email_sender = EmailSender()

    def send_email(self, to_address, subject, body, attachment_path=None):
        self.email_sender.send_email(to_address, subject, body, attachment_path)
