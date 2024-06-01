"""Minecraft Server module."""
from typing import List, Tuple
import os
import logging
from pathlib import Path
import time
import json

import jinja2
import sh
from sh import mcwrapper
import streamlit as st
import pandas as pd

from enums import ServerStatus
from log_reader import MinecraftLogReader
from download import MinecraftServerDownloader
import config

logger = st.logger.get_logger(__name__)


class ServerBase:
    
    @property
    def servers_directory(self) -> str:
        return str(Path(__file__).parent.parent / Path("servers").resolve())


class MinecraftServer(ServerBase):

    def __init__(self, name: str):
        self.name = name
        self.log_reader = MinecraftLogReader(log_path=self.log_directory)
        self.server_filename = "minecraft_server.jar"

    @property
    def _version_data(self) -> str:
        """Raw version data from the server jar file."""
        with sh.pushd(self.server_directory):
            return sh.unzip("-p", self.server_filename, "version.json")

    @property
    def version_data(self) -> dict:
        """Version data from the server jar file."""
        return json.loads(self._version_data)

    @property
    def version(self) -> str:
        """Version of the server jar file."""
        return self.version_data["name"]

    @property
    def java_version(self) -> str:
        """Java version of the server jar file."""
        return self.version_data["java_version"]

    def install_server_jar(self, version: str):
        """Install the server jar file for a given version."""
        logger.info(f"Installing server jar for version {version}")

        logger.info(f"Downloading server file for version {version}")
        downloader = MinecraftServerDownloader(version=version)
        new_server_file = downloader.get_server_file()

        # Copy the new server file
        logger.info(f"Copying new server file: {new_server_file}")
        with sh.pushd(self.server_directory):
            sh.cp(new_server_file, self.server_filename)

    def set_version(self, version: str, backup: bool = True, version_check: bool = True):
        """Set the version of the server jar file."""
        logger.info(f"Setting version to {version}")
        
        if version_check and (self.version == version):
            logger.warning(f"Version is already {version}")
            return

        # Stop the server if it is running
        self.stop()
        time.sleep(5)

        if backup:
            self.backup()

        # Remove the old server file
        logger.info(f"Removing old server file: {self.server_filename}")
        with sh.pushd(self.server_directory):
            sh.rm(self.server_filename)

        self.install_server_jar(version=version)

        # Start the server
        self.start()

    @property
    def server_path(self) -> Path:
        """Path to server directory."""
        return Path(self.servers_directory) / Path(self.name)

    @property
    def server_directory(self) -> str:
        """Path to server directory as a string."""
        return str(self.server_path)

    def _mcwrapper(self, *args, **kwargs):
        """Run mcwrapper for server."""
        logger.debug(f"Running mcwrapper command from directory: {self.server_directory}")
        with sh.pushd(self.server_directory):
            logger.debug(f"Running mcwrapper command: {' '.join(args)} {kwargs}")
            return mcwrapper(*args, **kwargs)

    def start(self):
        """Start the server."""
        logger.info("Starting server...")
        command_input = Path(self.server_directory) / "command_input"
        if command_input.exists():
            logger.info("Removing command input...")
            command_input.unlink()
        self._mcwrapper("start")

    def stop(self):
        """Stop the server."""
        logger.info("Stopping server...")
        self._mcwrapper("stop")

    def restart(self):
        """Restart the server."""
        logger.info("Restarting server...")
        self._mcwrapper("restart")

    def backup(self):
        """Backup the server."""
        logger.info("Backing up server...")
        self._mcwrapper("backup")

    @property
    def backup_directory(self) -> str:
        """Path to backup directory."""
        return str(Path(self.server_directory) / Path("backups"))
    
    @property
    def backup_path(self) -> Path:
        """Path to backup directory."""
        return Path(self.backup_directory)
    
    @property
    def backups(self) -> List[Tuple[str, float]]:
        """List of available backups, and the size in Mb."""
        return [(p.name, round(p.stat()[6]/1024/1024, 2)) for p in self.backup_path.glob("*.zip")]

    def run_command(self, command: str):
        """Run a server command."""
        logger.info(f"Running command: {command}")
        self._mcwrapper("command", command)

    def set_game_rule(self, rule: str, value: bool):
        """Set a game rule."""
        logger.info(f"Setting game rule {rule} to {value}")
        self.run_command(f"gamerule {rule} {str(value).lower()}")

    def set_weather(self, weather: str):
        """Set the weather on the server."""
        logger.info(f"Setting weather to {weather}")
        self.run_command(f"weather {weather}")

    def set_weather_cycle(self, enable: bool):
        """Set the weather cycle on the server."""
        logger.info(f"Setting weather cycle to {enable}")
        self.set_game_rule("doWeatherCycle", enable)

    @property
    def status(self) -> ServerStatus:
        status = self._mcwrapper("status", _err_to_out=True, _ok_code=[0,5])

        status_lookup = {
            "Server is NOT running.": ServerStatus.STOPPED,
            "Server is running.": ServerStatus.RUNNING,
        }

        try:
            return status_lookup[status.split('\n')[0]]
        except KeyError:
            return ServerStatus.UNKNOWN

    @property
    def log_directory(self) -> str:
        """Path to log directory."""
        return str(Path(self.server_directory) / Path("logs"))

    @property
    def log_file(self) -> str:
        """Path to latest log file."""
        return str(Path(self.log_directory) / Path("latest.log"))

    @property
    def log_contents(self) -> str:
        """Contents of the log file."""
        with open(self.log_file, "r") as f:
            return f.read()

    def log_tail(self, lines: int = 100, delay: float = 0.25) -> str:
        """Tail the log file."""
        time.sleep(delay)
        log_lines = self.log_contents.splitlines()
        tail_lines = log_lines[-lines:]
        return '\n'.join(tail_lines)

    @property
    def server_properties_file(self) -> str:
        """Path to server properties file."""
        return str(Path(self.server_directory) / Path("server.properties"))

    @property
    def server_properties_contents(self) -> str:
        """Contents of the server properties file."""
        with open(self.server_properties_file, "r") as f:
            return f.read()

    @property
    def server_properties_data(self) -> dict:
        """Data from the server properties file."""
        data = {}
        with open(self.server_properties_file, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                key, value = line.split("=")
                data[key] = value.strip()
        return data

    @property
    def server_properties_pandas(self) -> pd.DataFrame:
        """Data from the server properties file as a pandas DataFrame."""
        return pd.DataFrame.from_dict(self.server_properties_data, orient="index", columns=["value"])

    def update_server_properties(self, data: pd.DataFrame) -> None:
        """Update the server properties file from a pandas DataFrame."""
        with open(self.server_properties_file, "w") as f:
            for key, value in data.to_dict()["value"].items():
                f.write(f"{key}={value}\n")

    def write_eula(self):
        """Write the eula.txt file."""
        logger.info("Writing eula.txt file...")
        with open(self.server_directory / Path("eula.txt"), "w") as f:
            f.write("eula=true")

    def write_mcwrapper_config(self):
        """Write the mcwrapper config file."""
        logger.info("Writing mcwrapper config file...")

        with open(self.server_directory / Path("mcwrapper.conf"), "w") as f:
            f.write(f"""\
# JAVA_BIN -- the java binary.
# default: 'java' binary in your path.
# change this if you'd like to use a different java binary.
JAVA_BIN='{config.JAVA_BIN}'

# Java VM settings (increasing these never hurts)
# these are suggested settings from minecraft.net
MX_SIZE="2048M"
MS_SIZE="1024M"

# PID_FILE -- where mcwrapper stores the Minecraft server pid.
# default: mcwrapper.pid
PID_FILE="mcwrapper.pid"

# COMMAND_PIPE -- the mcwrapper FIFO
# default: command_input
COMMAND_PIPE="command_input"

# directory to store backups
# can be relative or absolute. if relative, it's relative to mcwrapper
# default: 'backups'
BACKUP_DIRECTORY_PATH="backups"

# How to compress the backup
# leave undefined (commented out) to not use compression
# accepted values are: tgz, zip
COMPRESS_BACKUP='zip'
""")
            
    def create_server_properties(self, **kwargs):
        """Create the server properties file from the jinja2 template."""
        logger.info("Creating server properties file...")

        # Load the template
        template = "server.properties.jinja2"
        template_path = Path(__file__).parent / Path(template)

        # Render the template
        template = jinja2.Template(template_path.read_text())
        rendered_template = template.render(**kwargs)

        with open(self.server_properties_file, "w") as f:
            f.write(rendered_template)

    def set_server_property(self, key: str, value: str):
        """Set a server property."""
        logger.info(f"Setting server property {key} to {value}")
        with open(self.server_properties_file, "r") as f:
            lines = f.readlines()

        with open(self.server_properties_file, "w") as f:
            for line in lines:
                if line.startswith(key):
                    line = f"{key}={value}\n"
                f.write(line)

    @property
    def port_number(self) -> int:
        """Port number of the server."""
        return int(self.server_properties_data["server-port"])

    @port_number.setter
    def port_number(self, value: int):
        """Set the port number of the server."""
        self.set_server_property("server-port", str(value))


def main():
    s = MinecraftServer(directory="test1")
    print(s.status)



class ServerManager(ServerBase):

    def __init__(self):
        logger.info("Created server manager instance.")

    @property
    def servers(self) -> List[str]:
        """List of available servers."""

        for root, dirs, files in os.walk(self.servers_directory):
            return dirs

    @property
    def server_managers(self) -> List[MinecraftServer]:
        """List of MinecraftServer instances."""
        return [self.get_server(name) for name in self.servers]

    @property
    def server_port_numbers(self) -> List[int]:
        """List of server port numbers."""
        def generator():
            for server in self.server_managers:
                try:
                    yield server.port_number
                except FileNotFoundError:
                    continue
        return list(generator())

    @property
    def next_port_number(self) -> int:
        """Next available port number."""
        if self.servers:
            return max(self.server_port_numbers) + 1
        else:
            return 25565

    def get_server(self, name: str) -> MinecraftServer:
        """Get a MinecraftServer instance by name."""
        return MinecraftServer(name=name)

    def create_server(self, name: str, version: str, port: int) -> MinecraftServer:
        """Create a new minecraft server."""
        logger.info(f"Creating server: {name} {version}")
        server = MinecraftServer(name=name)
        server.server_path.mkdir(parents=True, exist_ok=False)
        server.install_server_jar(version=version)
        server.write_eula()
        server.write_mcwrapper_config()
        server.create_server_properties(server_port=port)
        server.start()
        return server

    def get_ui_server_list(self):
        """Get a list of servers for the UI, including pre-selected index."""
        server_list = ["Choose an option"] + self.servers
        if len(self.servers) == 1:
            pre_selected_index = 1
        else:
            pre_selected_index = 0

        session_server = st.session_state.get('server', None)

        if session_server:
            try:
                pre_selected_index = server_list.index(session_server)
            except ValueError:
                pass

        return server_list, pre_selected_index
