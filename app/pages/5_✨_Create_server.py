import streamlit as st

from server import ServerManager

logger = st.logger.get_logger(__name__)

server_manager = ServerManager()

st.title("Minecraft Server Manager")

server_name = st.text_input("Server name", key="server_name")
server_version = st.text_input("Version", key="server_version")
server_port_number = st.text_input("Port number", key="server_port_number", value=str(server_manager.next_port_number))

if st.button("Create"):
    logger.info(f"Creating server: {server_name} {server_version}")
    server_manager.create_server(name=server_name, version=server_version, port=int(server_port_number))
    st.success("Server created!")
