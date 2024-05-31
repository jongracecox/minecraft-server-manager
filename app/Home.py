import time

import streamlit as st

from server import ServerManager
from enums import ServerStatus

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

if server_selection != "Choose an option":
    logger.info(f"Selected server: {server_selection}")

    server = server_manager.get_server(server_selection)

    st.session_state.server = server_selection

    logger.info(f"Server status: {server.status}")

    if server.status == ServerStatus.RUNNING:
        st.success(f"Server is running on port {server.port_number}!")

        st.button("Stop", on_click=server.stop)
        st.button("Restart", on_click=server.restart)

        st.code(server.log_tail(lines=10), line_numbers=True)

        def clear_command_text():
            st.session_state.command_text = st.session_state.command
            st.session_state.command = ""

        command = st.text_input("Command", key="command", on_change=clear_command_text)
        command_text = st.session_state.get('command_text', '')

        if command_text:
            logger.info(f"Running command: {command_text}")
            server.run_command(command_text)
            command_text = ""
            st.session_state.command_text = ""

        st.button("Refresh")

    elif server.status == ServerStatus.STOPPED:
        st.error("Server is stopped")
        st.button("Start", on_click=server.start)

    else:
        st.error("Server status is unknown")
        st.button("Start", on_click=server.start)

