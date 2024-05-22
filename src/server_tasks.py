import socket
import time

from src.buffer import Buffer


def monitor_buffer_size(buffer: Buffer, message_buffer_length: int) -> None:
    do_monitor = True
    while do_monitor:
        if len(buffer) == message_buffer_length:
            print("\nDumped messages due to buffer size.")
            # TODO: Add the syslog message dump.
            buffer.flush()

def monitor_buffer_age(buffer: Buffer, max_buffer_age: int) -> None:
    do_monitor = True
    while do_monitor:
        current_time = time.time()
        buffer_append_time = buffer.last_append_time
        time_from_last_append = current_time - buffer_append_time
        buffer_length = len(buffer)
        if time_from_last_append > max_buffer_age and buffer_length >= 1:
            print("\nDumped the messages due to the buffer age.")
            # TODO: Add the syslog message dump.
            buffer.flush()
            # Rests append time due to the buffer being cleared.
            buffer.last_append_time = time.time()

def run_udp_server(server: socket.socket, message_buffer: Buffer,
                   max_message_size: int) -> None:
    is_running = True
    while is_running:
        message, address = server.recvfrom(max_message_size)
        # Pauses the thread to give time for the buffer to do overflow checking.
        time.sleep(0.05)
        # TODO: Remove this message.
        print(f"\n\tConnection from: {address}\n\tMessage: {message}")
        message_buffer.append(message)

def run_tcp_server():
    raise NotImplemented("The tcp server has not been added yet.")
