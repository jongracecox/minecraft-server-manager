import time

import streamlit as st
import sh

from server import ServerManager
from enums import ServerStatus, GameRule
from download import MinecraftServerDownloader


logger = st.logger.get_logger(__name__)

server_manager = ServerManager()

st.title("Minecraft Server Manager")

logger.info(f"Available servers: {server_manager.servers}")

server_list, pre_selected_index = server_manager.get_ui_server_list()
    
server_selection = st.selectbox(
    "Select a server",
    options=server_list,
    placeholder="Choose an option",
    index=pre_selected_index,
    )

def set_server_version(server: ServerManager, version: str):
    """Set the version of the server jar file."""
    if server.version == version:
        st.write(f"Version is already {version}")
        return
    
    with st.status("Setting version...", expanded=True):
        st.write(f"Downloading server file for version {version}")
        downloader = MinecraftServerDownloader(version=version)
        new_server_file = downloader.get_server_file()
        st.write(f"New server file: {new_server_file}")

        st.write(f"Stopping server...")
        if server.status == ServerStatus.RUNNING:
            server.stop()

        st.write(f"Sleeping for 5s...")
        time.sleep(5)

        st.write(f"Backing up server...")
        server.backup()

        st.write(f"Removing old server file: {server.server_filename}")
        with sh.pushd(server.server_directory):
            sh.rm(server.server_filename)

        st.write(f"Copying new server file: {new_server_file}")
        with sh.pushd(server.server_directory):
            sh.cp(new_server_file, server.server_filename)

        st.write(f"Starting server...")
        server.start()
        st.write("Done.")

    st.snow()


if server_selection != "Choose an option":

    logger.info(f"Selected server: {server_selection}")
    st.session_state.server = server_selection
    server = server_manager.get_server(server_selection)

    st.markdown(f"**Version:** {server.version}")
    st.markdown(f"**Java version:** {server.java_version}")

    version = st.text_input("Enter new version", value="")
    if version:
        st.write(f"Changing version to {version}")
        set_server_version(server, version)
