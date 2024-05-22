import json

from src.buffer import Buffer
from src.server import Server


def main():
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

    address_port = (bind_address, udp_port)

    message_buffer = Buffer(bytes, buffer_length)

    syslog_server = Server(protocol, address_port, tcp_port, udp_port,
                           message_buffer, buffer_length, buffer_lifespan,
                           max_message_size, max_tcp_connections)

    syslog_server.start()

if __name__ == '__main__':
    main()