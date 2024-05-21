import time

from src.buffer import Buffer


def monitor_buffer_size(buffer: Buffer, message_buffer_length: int):
    do_monitor = True
    while do_monitor:
        if len(buffer) == message_buffer_length:
            print("Dumped messages due to buffer size.")
            # TODO: Add the syslog message dump.
            buffer.flush()

def monitor_buffer_age(buffer: Buffer, max_buffer_age: int):
    do_monitor = True
    while do_monitor:
        current_time = time.time()
        buffer_append_time = buffer.last_append_time
        time_from_last_append = current_time - buffer_append_time
        if time_from_last_append > max_buffer_age:
            print("Dumped the messages due to the buffer age.")
            # TODO: Add the syslog message dump.
            buffer.flush()

def run_udp_server():
    ...

def run_tcp_server():
    ...
