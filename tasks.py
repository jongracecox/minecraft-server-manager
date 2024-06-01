from pathlib import Path

from invoke import task
from decouple import config


@task
def setup(c):
    """Create virtual environment."""
    virtualenv = Path(__file__).parent / Path("venv")
    if virtualenv.exists():
        print("Removing existing virtual environment...")
        c.run("rm -rf venv")

    print("Creating virtual environment...")
    c.run("python3 -m venv venv")

    print("Installing dependencies...")
    c.run("venv/bin/pip install --upgrade pip")
    c.run("venv/bin/pip install -r requirements.txt")

    print("Checking for settings.ini...")
    settings = Path(__file__).parent / Path("settings.ini")
    if not settings.exists():
        c.run("cp settings.ini.template settings.ini")
    
    install_mc_wrapper(c)
    
    print("Setup complete.")


@task
def install_mc_wrapper(c):
    """Install mcwrapper."""
    print("Installing mcwrapper...")
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
