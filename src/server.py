import logging
import logging.config
import socket
import threading

from src.network_buffer import NetworkBuffer
from src.server_tasks import (monitor_buffer_age, run_udp_server,
                              run_tcp_server)


def setup_server_logging(log_debug_messages: bool) -> logging.Logger:
    """
    Sets up the logging for Server Object.

    Args:
        log_debug_messages (bool): If logging should be set up to log debug
        messages.

    Returns:
        logging.Logger: The logger to use for logging the server.
    """
    if log_debug_messages:
        server_logger = logging.getLogger("debug_logger")
    else:
        server_logger = logging.getLogger("info_logger")
    return server_logger


class Server:
    """
    Represents the syslog server that will receive and log syslog messages from
    other computers.
    """

    def __init__(self, protocol: str,
                 address: tuple[str, int], tcp_port: int,
                 udp_port: int, buffer: NetworkBuffer,
                 max_buffer_size: int, max_buffer_age: int,
                 max_message_size: int, max_tcp_connections: int,
                 syslog_path: str, log_debug_messages: bool) -> None:
        """
        Initializes an instance of the Server class.

        Args:
            protocol (str): The protocol to use for the server. Can be UDP,
            TCP, or BOTH.
            address (tuple[str, int]): A tuple with the ip and port of the
            server.
            tcp_port (int): The TCP port for the server to listen on.
            udp_port (int): The UDP port for the server to listen on.
            buffer (src.NetworkBuffer): The buffer used to store messages the
            server receives.
            max_buffer_size (int): The max size the buffer can be.
            max_buffer_age (int): The max age before the buffer expires.
            max_message_size (int): The max size message the server can
            receive.
            max_tcp_connections (int): The max number of TCP connections.
            log_debug_messages (bool): Whether to print debug messages or not.
            syslog_path (str): The path to where the syslog messages from remote
            hosts should be written to.

        Returns:
            None

        Raises:
            TypeError: Raised if the buffer argument passed is not of the
            src.NetworkBuffer type.

        Notes:
            The TCP functionality of this class is not done. It does not work
            in any capacity. The stop method is the same.
        """
        if not isinstance(buffer, NetworkBuffer):
            raise TypeError(
                "The provided message_buffer is not of the NetworkBuffer "
                "buffer_type.")
        self.protocol = str(protocol)
        self.address = address
        self.tcp_port = int(tcp_port)
        self.udp_port = int(udp_port)
        self.max_buffer_length = int(max_buffer_size)
        self.max_buffer_age = int(max_buffer_age)
        self.max_message_size = int(max_message_size)
        self.max_tcp_connections = int(max_tcp_connections)
        self.syslog_path = syslog_path
        self.buffer = buffer
        # Ensures files are writen to via tasks in the correct order.
        self.write_lock = threading.Lock()
        self.logger = setup_server_logging(log_debug_messages)

    def make_udp_server(self) -> socket.socket:
        """
        Creates and then returns a UDP socket for the server.

        Returns:
            socket.socket: The UDP socket for the server to receive on.
        """
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        address_and_port = (self.address, self.udp_port)
        udp_server.bind(address_and_port)
        self.logger.info(f"Created UDP socket on port {self.tcp_port}.")
        return udp_server

    def make_tcp_server(self) -> socket.socket:
        """
        Creates and then returns a TCP for the server.

        Returns:
            socket.socket: The TCP socket used for communication with the
            server.
        """
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        address_and_port = (self.address, self.tcp_port)
        tcp_server.bind(address_and_port)
        tcp_server.listen(self.max_tcp_connections)
        self.logger.info(f"Created TCP socket and started listening on port "
                         f"{self.tcp_port}.")
        return tcp_server

    def start_buffer_age_monitor(self) -> None:
        """
        Creates and starts a thread that monitors the age of the network buffer.

        Returns:
            None
        """
        monitor_buffer_age_args = [self.buffer,
                                   self.max_buffer_age,
                                   self.write_lock,
                                   self.syslog_path,
                                   self.logger]
        monitor_buffer_age_thread = threading.Thread(target=monitor_buffer_age,
                                                     args=monitor_buffer_age_args)

        self.logger.debug("Starting buffer age monitor...")
        monitor_buffer_age_thread.start()

    def start(self) -> None:
        """
        Starts the server.

        Returns:
            None

        Raises:
            NotImplemented: Raised when a TCP server is attempted to start.
        """
        match self.protocol.upper().strip():
            case "UDP":
                udp_server = self.make_udp_server()
                self.start_buffer_age_monitor()
                udp_server_args = [udp_server,
                                   self.buffer,
                                   self.max_message_size,
                                   self.write_lock,
                                   self.syslog_path,
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
        """
        Not implemented yet.

        Returns:
            None

        Raises:
            NotImplemented: The stop function has not been implemented.
        """
        raise NotImplemented("The stop function has not been implemented.")
