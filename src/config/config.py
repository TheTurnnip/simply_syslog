import json
from dataclasses import dataclass


@dataclass
class Config:
    protocol: str
    bind_address: str
    udp_port: int
    tcp_port: int
    max_tcp_connections: int
    buffer_length: int
    buffer_lifespan: int
    max_message_size: int
    syslog_path: str
    debug_messages: bool
    enable_database_writes: bool
    db_connection_string: str

    def __init__(self, config_path: str):
        with open(config_path, "r") as config:
            config_data = json.loads(config.read())
            self.protocol = config_data["protocol"]
            self.bind_address = config_data["bind_address"]
            self.udp_port = int(config_data["udp_port"])
            self.tcp_port = int(config_data["tcp_port"])
            self.max_tcp_connections = int(config_data["max_tcp_connections"])
            self.buffer_length = int(config_data["buffer_length"])
            self.buffer_lifespan = int(config_data["buffer_lifespan"])
            self.max_message_size = int(config_data["max_message_size"])
            self.syslog_path = config_data["syslog_path"]
            self.do_debug_logging = config_data["debug_messages"]
            self.enable_database_writes = config_data["enable_db_writes"]
            self.database_connection_string = config_data[
                "db_connection_string"]
