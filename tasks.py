from pathlib import Path

from invoke import task
from decouple import config


@task
def install_mc_wrapper(c):
    """Install mcwrapper."""
    c.run("gem install mcwrapper")


@task
def run(c):
    """Run streamlit app."""
    streamlit = Path(__file__).parent / Path("venv/bin/streamlit")
    c.run(f"{streamlit} run app/Home.py")


@task
def deploy(c, username = None, ip_address = None):
    """Deploy app to Mac Mini."""
    username = config("DEPLOY_USERNAME")
    ip_address = config("DEPLOY_IP_ADDRESS")
    app_path = config("DEPLOY_REMOTE_PATH")
    file_list = [
        "app",
        "tasks.py",
        "start.sh",
        "stop.sh",
        "status.sh",
        "requirements.txt",
    ]
    command = f"rsync -av --exclude \"__pycache__\" {' '.join(file_list)} {username}@{ip_address}:{app_path}/."
    print("Running rsync command:")
    print(f"  {command}")
    c.run(command)
