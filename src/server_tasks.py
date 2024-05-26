import logging
import socket
import threading
import time

from src.buffer import Buffer
from src.messages.udp_message import UDPMessage


def monitor_buffer_age(message_buffer: Buffer, max_buffer_age: int,
                       write_lock: threading.Lock,
                       logger: logging.Logger) -> None:
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

def run_udp_server(server: socket.socket, message_buffer: Buffer,
                   max_message_size: int, write_lock: threading.Lock,
                   logger: logging.Logger) -> None:
    is_running = True
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

def run_tcp_server():
    raise NotImplemented("The tcp server has not been added yet.")


def write_to_disk(buffer: Buffer, logger: logging.Logger) -> None:
    with open("./syslog.log", "a") as syslog_file:
        for message in buffer:
            formated_message = f"{message.message.decode()}\n"
            syslog_file.write(formated_message)
            logger.debug(f"Wrote message to disk: {message.message}")
            message.is_written = True