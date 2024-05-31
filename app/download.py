"""Module for downloading Minecraft server files."""
from typing import Union
from pathlib import Path
import requests

from bs4 import BeautifulSoup
import requests_cache

requests_cache.install_cache('mc_server_download_cache')


class MinecraftServerDownloader:

    downloads_directory: Path = Path(__file__).parent.parent / Path("downloads").resolve()

    def __init__(self, version: str):
        super().__init__()
        self.version = version

        # Create downloads directory if it doesn't exist
        if not self.downloads_directory.exists():
            self.downloads_directory.mkdir(parents=True, exist_ok=True)

    @property
    def download_page(self) -> str:
        """URL of the mcversions.net download page."""
        return f"https://mcversions.net/download/{self.version}"

    @property
    def download_url(self) -> str:
        """The download URL for the server file."""
        response = requests.get(self.download_page)
        soup = BeautifulSoup(response.text, "html.parser")

        download_links = soup.find("div", class_="downloads").find_all("a")
        for link in download_links:
            if link["href"].endswith("server.jar"):
                return link["href"]

        raise RuntimeError("Unable to locate server download URL.")

    @property
    def server_filename(self) -> str:
        """Filename portion of the server file."""
        return f"server_{self.version}.jar"

    @property
    def server_file_full_path(self) -> Path:
        """Full path to the server file."""
        return self.downloads_directory / self.server_filename

    def download_server(self) -> Path:
        """Download a Minecraft server file and return the path to the downloaded file."""
        response = requests.get(self.download_url)
        server_file: Path = self.server_file_full_path
        with open(server_file, "wb") as f:
            f.write(response.content)

        return server_file
    
    def get_server_file(self) -> Path:
        """Get the path to the server file.
        
        This will trigger a download if the file does not exist.
        """
        if not self.server_file_full_path.exists():
            self.download_server()
        return self.server_file_full_path
