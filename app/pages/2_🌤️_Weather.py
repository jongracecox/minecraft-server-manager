import time

import streamlit as st

from server import ServerManager
from enums import ServerStatus, GameRule

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

    st.code(server.log_tail(lines=5), line_numbers=True)

    st.header("Weather")

    options = ["clear", "rain", "thunder"]
    for col, weather in zip(st.columns(len(options)), options):
        with col:
            st.button(weather.capitalize(), on_click=server.set_weather, args=(weather,))
