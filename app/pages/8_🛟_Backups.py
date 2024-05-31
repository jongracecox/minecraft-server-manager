import streamlit as st
import pandas as pd

from server import ServerManager, ServerStatus

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
    st.session_state.server = server_selection
    server = server_manager.get_server(server_selection)

    backup_files = server.backups
    df = pd.DataFrame(backup_files, columns=["File name", "Size (Mb)"])
    st.dataframe(df, use_container_width=True, hide_index=True)

    if server.status == ServerStatus.RUNNING:

        st.button("Backup", on_click=server.backup)
