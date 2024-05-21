import socket
import threading

from src.buffer import Buffer
from src.server_tasks import (monitor_buffer_size, monitor_buffer_age,
                              run_udp_server, run_tcp_server)


class Server:
    def __init__(self, protocol: str,
                 address: str, tcp_port: int,
                 udp_port: int, buffer: Buffer,
                 max_message_size: int, max_tcp_connections: int) -> None:
        if not isinstance(buffer, Buffer):
            raise TypeError("The provided buffer is not of the Buffer type.")
        self.protocol = str(protocol)
        self.address = str(address)
        self.tcp_port = int(tcp_port)
        self.udp_port = int(udp_port)
        self.max_message_size = int(max_message_size)
        self.max_tcp_connections = int(max_tcp_connections)
        self.buffer = buffer

    def make_udp_server(self) -> socket.socket:
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind(self.address)
        return udp_server

    def make_tcp_server(self) -> socket.socket:
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server.bind(self.address)
        tcp_server.listen(self.max_tcp_connections)
        return tcp_server

    def start_monitors(self):
        # TODO: Add the needed args to the threads.
        monitor_buffer_age_thread = threading.Thread(target=monitor_buffer_age,
                                                     args=[])
        monitor_buffer_size_thread = threading.Thread(target=monitor_buffer_size, args=[])
        monitor_buffer_age_thread.start()
        monitor_buffer_size_thread.start()

    def start(self):
        # TODO: Add the needed args to the threads.
        match self.protocol.upper().strip():
            case "UDP":
                udp_server = self.make_udp_server()
                self.start_monitors()
                udp_server_thread = threading.Thread(target=run_udp_server,
                                                     args=[])
                udp_server_thread.start()
            case "TCP":
                tcp_server = self.make_tcp_server()
                self.start_monitors()
                tcp_server_thread = threading.Thread(target=run_tcp_server,
                                                     args=[])
                tcp_server_thread.start()
            case "BOTH":
                udp_server = self.make_udp_server()
                tcp_server = self.make_tcp_server()
                self.start_monitors()
                udp_server_thread = threading.Thread(target=run_udp_server,
                                                     args=[])
                tcp_server_thread = threading.Thread(target=run_tcp_server,
                                                     args=[])
                udp_server_thread.start()
                tcp_server_thread.start()

            case _:
                raise ValueError("No valid protocol provided.")

    def stop(self):
        raise NotImplemented("The stop function has not been implemented.")