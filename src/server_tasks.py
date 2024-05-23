import socket
import threading
import time

from src.buffer import Buffer


def monitor_buffer_age(message_buffer: Buffer, max_buffer_age: int,
                       write_lock: threading.Lock) -> None:
    do_monitor = True
    while do_monitor:
        current_time = time.time()
        buffer_append_time = message_buffer.last_append_time
        time_from_last_append = current_time - buffer_append_time
        buffer_length = len(message_buffer)
        if time_from_last_append > max_buffer_age and buffer_length >= 1:
            print("\nDumped the messages due to the message_buffer age.")
            # TODO: Add the syslog message dump.
            write_lock.acquire()
            write_to_disk(message_buffer)
            message_buffer.flush()
            write_lock.release()
            # Rests append time due to the message_buffer being cleared.
            message_buffer.last_append_time = time.time()

def run_udp_server(server: socket.socket, message_buffer: Buffer,
                   max_message_size: int, write_lock: threading.Lock) -> None:
    is_running = True
    while is_running:
        message, address = server.recvfrom(max_message_size)
        if len(message_buffer) < message_buffer.max_size:
            message_buffer.append(message)
        elif len(message_buffer) == message_buffer.max_size:
            write_lock.acquire()
            write_to_disk(message_buffer)
            message_buffer.flush()
            write_lock.release()
        # TODO: Remove this message.
        print(f"\n\tConnection from: {address}\n\tMessage: {message}")

def run_tcp_server():
    raise NotImplemented("The tcp server has not been added yet.")

def write_to_disk(buffer: Buffer) -> None:
    with open("./syslog.log", "a") as syslog_file:
        for message in buffer:
            print(f"Wrote the message to disk: {message}")
            syslog_file.write(f"{message.decode()}\n")
