"""Contains functionality related to Weather"""
import logging

logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        """Handles incoming weather data"""
        message_dict = message.value()
        self.temperature = message_dict.get('temperature')
        self.status = message_dict.get('status')

        logger.info("weather process_message is complete")

