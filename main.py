import json

from src.buffer import Buffer
from src.messages.udp_message import UDPMessage
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

    # Make a message_buffer to hold incoming messages.
    message_buffer = Buffer(UDPMessage, buffer_length)

    # Make the syslog server with the config properties.
    syslog_server = Server(protocol, address_port_combination, tcp_port, udp_port,
                           message_buffer, buffer_length, buffer_lifespan,
                           max_message_size, max_tcp_connections)

    syslog_server.start()

if __name__ == '__main__':
    main()
