import json
import logging
import logging.config

from src.messages.udp_message import UDPMessage
from src.network_buffer import NetworkBuffer
from src.server import Server


def main():
    # Read the config file and assign each item to a variable.
    with open("config/config.json", "r") as config:
        config = json.load(config)

    protocol = config["protocol"]
    bind_address = config["bind_address"]
    udp_port = int(config["udp_port"])
    tcp_port = int(config["tcp_port"])
    max_tcp_connections = int(config["max_tcp_connections"])
    buffer_length = int(config["buffer_length"])
    buffer_lifespan = int(config["buffer_lifespan"])
    max_message_size = int(config["max_message_size"])
    address_port_combination = (bind_address, udp_port)
    do_debug_logging = True if config["debug_messages"] == "True" else False


    # Make a message_buffer to hold incoming messages.
    message_buffer = NetworkBuffer(UDPMessage, buffer_length)

    # Make the syslog server with the config properties.
    syslog_server = Server(protocol, address_port_combination, tcp_port,
                           udp_port,
                           message_buffer, buffer_length, buffer_lifespan,
                           max_message_size, max_tcp_connections,
                           do_debug_logging)

    syslog_server.start()


def setup_server_logging() -> None:
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
