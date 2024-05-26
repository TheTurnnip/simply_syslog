import logging
import logging.config
import socket
import threading

from src.buffer import Buffer
from src.server_tasks import (monitor_buffer_age, run_udp_server,
                              run_tcp_server)


class Server:
    def __init__(self, protocol: str,
                 address: tuple, tcp_port: int,
                 udp_port: int, buffer: Buffer,
                 max_buffer_size: int, max_buffer_age: int,
                 max_message_size: int, max_tcp_connections: int,
                 log_debug_messages: bool) -> None:
        if not isinstance(buffer, Buffer):
            raise TypeError("The provided message_buffer is not of the Buffer type.")
        self.protocol = str(protocol)
        self.address = address
        self.tcp_port = int(tcp_port)
        self.udp_port = int(udp_port)
        self.max_buffer_length = int(max_buffer_size)
        self.max_buffer_age = int(max_buffer_age)
        self.max_message_size = int(max_message_size)
        self.max_tcp_connections = int(max_tcp_connections)
        self.buffer = buffer
        # Ensures files are writen to via tasks in the correct order.
        self.write_lock = threading.Lock()
        self.logger = self.setup_server_logging(log_debug_messages)

    def setup_server_logging(self, log_debug_messages):
        if log_debug_messages == True:
            server_logger = logging.getLogger("debug_logger")
        else:
            server_logger = logging.getLogger("info_logger")
        return server_logger

    def make_udp_server(self) -> socket.socket:
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind(self.address)
        self.logger.info(f"Created UDP socket on port {self.address[1]}")
        return udp_server

    def make_tcp_server(self) -> socket.socket:
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind(self.address)
        tcp_server.listen(self.max_tcp_connections)
        self.logger.info(f"Created TCP socket and started listening on port "
                         f"{self.address[1]}")
        return tcp_server

    def start_buffer_age_monitor(self):
        monitor_buffer_age_args = [self.buffer,
                                   self.max_buffer_age,
                                   self.write_lock,
                                   self.logger]
        monitor_buffer_age_thread = threading.Thread(target=monitor_buffer_age,
                                                     args=monitor_buffer_age_args)

        self.logger.debug("Starting buffer age monitor...")
        monitor_buffer_age_thread.start()

    def start(self):
        # TODO: Add the needed args to the threads.
        match self.protocol.upper().strip():
            case "UDP":
                udp_server = self.make_udp_server()
                self.start_buffer_age_monitor()
                udp_server_args = [udp_server,
                                   self.buffer,
                                   self.max_message_size,
                                   self.write_lock,
                                   self.logger]
                udp_server_thread = threading.Thread(target=run_udp_server,
                                                     args=udp_server_args)
                self.logger.info("Starting UDP server...")
                udp_server_thread.start()
            case "TCP":
                tcp_server = self.make_tcp_server()
                self.start_buffer_age_monitor()
                tcp_server_thread = threading.Thread(target=run_tcp_server,
                                                     args=[])
                self.logger.info("Starting TCP server...")
                tcp_server_thread.start()
            case "BOTH":
                udp_server = self.make_udp_server()
                tcp_server = self.make_tcp_server()
                self.start_buffer_age_monitor()
                udp_server_args = [udp_server,
                                   self.buffer,
                                   self.max_message_size,
                                   self.write_lock]
                udp_server_thread = threading.Thread(target=run_udp_server,
                                                     args=udp_server_args)
                tcp_server_thread = threading.Thread(target=run_tcp_server,
                                                     args=[])
                self.logger.info("Starting UDP/TCP server...")
                udp_server_thread.start()
                tcp_server_thread.start()
            case _:
                raise ValueError("No valid protocol provided.")

    def stop(self):
        raise NotImplemented("The stop function has not been implemented.")
