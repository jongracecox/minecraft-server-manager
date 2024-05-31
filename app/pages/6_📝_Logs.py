import streamlit as st

from server import ServerManager

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

    st.code(server.log_contents, line_numbers=True)
    st.button("Refresh logs")

    with st.expander("Show tabular logs"):
        log_data = server.log_reader.to_pandas()
        st.dataframe(log_data)
