import json
import logging
import logging.config

from config import Config
from src.messages.network_message import NetworkMessage
from src.network_buffer import NetworkBuffer
from src.server import Server


def main():
    server_config = Config("config/config.json")

    # Make a message_buffer to hold incoming messages.
    message_buffer = NetworkBuffer(NetworkMessage, server_config.buffer_length)

    # Make the syslog server with the config_data properties.
    syslog_server = Server(server_config, message_buffer)

    syslog_server.start()


def setup_server_logging() -> None:
    """
    Sets up the logging for the server itself.

    Returns:
        None
    """
    with open("config/server_logging_config.json", "r") as logging_config:
        config_data = json.load(logging_config)
        logging.config.dictConfig(config_data)


if __name__ == '__main__':
    info_logger = logging.getLogger("info_logger")
    setup_server_logging()
    try:
        main()
    except ValueError as e:
        info_logger.critical(e)
    except TypeError as e:
        info_logger.critical(e)
