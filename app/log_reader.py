from typing import List, Optional
from pathlib import Path
import gzip
from datetime import datetime
import re

import pandas as pd
import streamlit as st


logger = st.logger.get_logger(__name__)


class MinecraftLogReader:
    """Class for reading minecraft logs."""

    def __init__(self, log_path: str):
        self.log_path = Path(log_path).expanduser()
        self.expression = re.compile(r"\[([^]]*)\] \[(.*)/(.*)\]: (.*)")

    def _find_log_files(self) -> List[Path]:
        """Find all .log and .log.gz files."""
        def generator():
            yield from self.log_path.glob("*.log.gz")
            yield from self.log_path.glob("*.log")
        return list(generator())
    
    def get_file_date(self, log_file: Path) -> str:
        """Get the date from a log file."""
        if log_file.name == "latest.log":
            return datetime.now().strftime("%Y-%m-%d")
        
        return "-".join(log_file.name.split(".")[0].split("-")[:-1])

    def format_log_line(self, log_line: str, filename: str, file_date: str) -> Optional[dict]:
        match = self.expression.match(log_line.strip())
        if not match:
            logger.error(f"Could not parse log line: {log_line}")
            return None            
        timestamp, log_level, log_source, log_message = match.groups()
        return {
            "filename": filename,
            "timestamp": datetime.strptime(f"{file_date}T{timestamp}", "%Y-%m-%dT%H:%M:%S"),
            "log_level": log_level,
            "log_source": log_source,
            "log_message": log_message,
        }

    def _read_log_file(self, log_file: Path) -> dict:
        """Read a log file."""
        with open(log_file, "r") as f:
            file_date = self.get_file_date(log_file)
            for log_line in f.readlines():
                formatted = self.format_log_line(log_line, log_file, file_date)
                if formatted:
                    yield formatted

    def _read_gz_log_file(self, log_file: Path) -> dict:
        """Read a gzipped log file."""
        with gzip.open(log_file, "rt") as f:
            file_date = self.get_file_date(log_file)
            for log_line in f.readlines():
                formatted = self.format_log_line(log_line, log_file, file_date)
                if formatted:
                    yield formatted

    def read_log_files(self) -> str:
        """Read all log files."""
        log_files = self._find_log_files()
        for log_file in log_files:
            if log_file.suffix == ".gz":
                yield from self._read_gz_log_file(log_file)
            else:
                yield from self._read_log_file(log_file)

    def to_pandas(self) -> pd.DataFrame:
        """Convert log files to pandas DataFrame."""
        return pd.DataFrame(self.read_log_files()).sort_values("timestamp")

    @property
    def events_by_hour(self) -> pd.DataFrame:
        """Get events by hour over time."""
        df = self.to_pandas()
        # Create a column for the timestamp rounded to the hour
        df["hour"] = df["timestamp"].dt.round("H")

        # Group by the hour column and count the number of events
        return df.groupby("hour").count()["timestamp"].reset_index()

    def get_events_by_time(self, interval: str = "1min") -> pd.DataFrame:
        """Get events by minute over time."""
        df = self.to_pandas()
        df["event time"] = df["timestamp"].dt.round(interval)
        return df.groupby("event time").count()["timestamp"].reset_index().rename(columns={"timestamp": "event count"})

    @property
    def player_sessions(self) -> pd.DataFrame:
        """Return a DataFrame with player sessions, including joined and left times.
        
        This might help: https://stackoverflow.com/questions/51253867/group-pandas-events-by-start-and-end-events
        """
        df = self.to_pandas()
        # Get only the lines that contain "joined the game" or "left the game"
        df = df[df["log_message"].str.contains("joined the game|left the game")]

        # Sort the dataframe by timestamp
        df = df.sort_values("timestamp")

        # Create a dataframe containing player sessions with joined and left times
        sessions = pd.DataFrame(columns=["joined", "left"])

        # Loop through the dataframe and add joined and left times to the sessions dataframe
        for index, row in df.iterrows():
            if row["log_message"].endswith("joined the game"):
                sessions.loc[index, "joined"] = row["timestamp"]
            elif row["log_message"].endswith("left the game"):
                sessions.loc[index, "left"] = row["timestamp"]

        # Drop rows with missing values
        sessions = sessions.dropna()

        # Convert the joined and left columns to datetime
        sessions["joined"] = pd.to_datetime(sessions["joined"])
        sessions["left"] = pd.to_datetime(sessions["left"])

        # Calculate the duration of each session
        sessions["duration"] = sessions["left"] - sessions["joined"]

        return sessions


if __name__ == "__main__":
    reader = MinecraftLogReader("~/git/minecraft-server-manager/servers/test1/logs")
    #print(reader._find_log_files())
    #for line in reader.read_log_files():
    #    print(line)

    # Set pandas options to display all columns and rows
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    # Set pandas options to not truncate columns and rows
    pd.set_option("display.max_colwidth", None)
    pd.set_option("display.width", None)
    # print(reader.to_pandas())
    # print(reader.events_by_hour)
    #print(reader.player_sessions)
    print(reader.get_events_by_time())