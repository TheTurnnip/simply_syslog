"""
This file is used to start the server in a docker container.
"""
import json
import os
import subprocess


def main():
    # Define the environment variables used to configure the server.
    CONFIG_FILE = {
        "protocol": os.environ["PROTOCOL"],
        "bind_address": os.environ["BIND_ADDRESS"],
        "udp_port": os.environ["UDP_PORT"],
        "tcp_port": os.environ["TCP_PORT"],
        "max_tcp_connections": os.environ["MAX_TCP_CONNECTIONS"],
        "buffer_length": os.environ["BUFFER_LENGTH"],
        "buffer_lifespan": os.environ["BUFFER_LIFESPAN"],
        "max_message_size": os.environ["MAX_MESSAGE_SIZE"],
        "syslog_path": os.environ["SYSLOG_PATH"],
        "debug_messages": os.environ["DEBUG_MESSAGES"]
    }

    # Display the config settings in the terminal.
    print("These are the settings for the config file: ")
    for key, value in CONFIG_FILE.items():
        print(f"{key}: {value}")

    # Delete the config if one is present.
    server_config = "/simply_syslog/config/config.json"
    if os.path.isfile(server_config):
        subprocess.call(["rm", server_config])
    # Write config file to the config file.
    with open(f"./config/config.json", "x") as config_file:
        json.dump(CONFIG_FILE, config_file)
        print("Config has been made...")

    # Create the file to store the syslog messages from remote hosts.
    if not os.path.isfile(f"{CONFIG_FILE["syslog_path"]}/syslog.log"):
        subprocess.call(["touch", f"{CONFIG_FILE["syslog_path"]}/syslog.log"])

    # Start the server.
    subprocess.call(["python3", "./main.py"])


main()
