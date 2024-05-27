import logging
import socket
import threading
import time

from src.messages.udp_message import UDPMessage
from src.network_buffer import NetworkBuffer


def monitor_buffer_age(message_buffer: NetworkBuffer, max_buffer_age: int,
                       write_lock: threading.Lock,
                       logger: logging.Logger) -> None:
    """
    Monitors a src.NetworkBuffer object to check if it has expired.

    Args:
        message_buffer (NetworkBuffer): The buffer to monitor.
        max_buffer_age (int): The max age a buffer can be before it is
        written to file.
        write_lock (threading.Lock): The lock that must be acquired to write
        to a file.
        logger (logging.Logger): The logger to used to log debug messages to
        the terminal.

    Returns:
        None

    Notes:
        This function is meant to be run along with the server. When calling
        use a thread to run alongside the server.
    """
    do_monitor = True
    while do_monitor:
        current_time = time.time()
        buffer_append_time = message_buffer.last_append_time
        time_from_last_append = current_time - buffer_append_time
        buffer_length = len(message_buffer)
        buffer_is_expired = time_from_last_append > max_buffer_age
        buffer_has_items = buffer_length >= 1
        if buffer_is_expired and buffer_has_items:
            logger.debug("Dumped messages to file due to buffer age.")
            try:
                write_lock.acquire()
            except OverflowError as e:
                logger.critical(e)
            except TypeError as e:
                logger.critical(e)
            write_to_disk(message_buffer, logger)
            message_buffer.flush()
            write_lock.release()
            # Rests append time due to the message_buffer being cleared.
            message_buffer.last_append_time = time.time()


def run_udp_server(server: socket.socket, message_buffer: NetworkBuffer,
                   max_message_size: int, write_lock: threading.Lock,
                   logger: logging.Logger) -> None:
    """
    Starts the event loop for the UDP server.

    Args:
        server (socket.Socket): The socket the server receives on.
        message_buffer (src.NetworkBuffer): The buffer to hold messages in.
        max_message_size (int): The max size a message can be.
        write_lock (threading.Lock): The lock that must be acquired to write
        to a file.
        logger (logging.Logger): The logger used to log debug messages to
        the terminal.

    Returns:
        None

    Notes:
        This function is intended to be run as a thread, when calling use a
        thread to allow for the server to preform other tasks, such as buffer
        age checking.
    """
    is_running = True
    logger.info("UDP Server has started.")
    start_time = time.perf_counter()
    while is_running:
        message, address = server.recvfrom(max_message_size)
        udp_message = UDPMessage(address, message)
        logger.debug(udp_message)
        if len(message_buffer) < message_buffer.max_size:
            try:
                message_buffer.append(udp_message)
            except OverflowError as e:
                logger.critical(e)
            except TypeError as e:
                logger.critical(e)
        elif len(message_buffer) == message_buffer.max_size:
            logger.debug("Dumped messages due to buffer age.")
            write_lock.acquire()
            write_to_disk(message_buffer, logger)
            message_buffer.flush()
            message_buffer.append(udp_message)
            write_lock.release()
        logger.debug(f"Revived UDP connection from: {address} || Message: "
                     f"{message}")


def run_tcp_server() -> None:
    """
    Not implemented yet.

    Returns:
        None

    Raises:
        NotImplemented: The tcp server has not been added yet.
    """
    raise NotImplemented("The tcp server has not been added yet.")


def write_to_disk(buffer: NetworkBuffer, logger: logging.Logger) -> None:
    """
    Loops over a src.NetworkBuffer object and write all items in the buffer
    to a file.

    Args:
        buffer (src.NetworkBuffer): The NetworkBuffer to write to disk.
        logger (logging.Logger): The logger to use for debug messages.

    Returns:
        None
    """
    with open("./syslog.log", "a") as syslog_file:
        for message in buffer:
            formated_message = f"{message.message.decode()}\n"
            syslog_file.write(formated_message)
            logger.debug(f"Wrote message to disk: {message.message}")
            message.is_written = True
