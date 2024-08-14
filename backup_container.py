import argparse
import datetime
import os
import shutil
import tarfile
from pathlib import Path

import docker

# Initialize Docker client
client = docker.from_env()

# Function to stop a Docker container
def stop_container(container_name):
    try:
        container = client.containers.get(container_name)
        container.stop()
    except Exception as e:
        print(f"Error stopping container {container_name}: {str(e)}")

# Function to start a Docker container
def start_container(container_name):
    try:
        container = client.containers.get(container_name)
        container.start()
    except Exception as e:
        print(f"Error starting container {container_name}: {str(e)}")

def create_archive(container_name, source_folder, destination_folder):
    # Get today's date in YYYY-MM-DD format
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Define paths for temporary and final archive locations
    archive_name = f"{container_name}_backup_{today}.tar.gz"
    temp_archive_path = f"/app/{archive_name}"
    final_archive_path = os.path.join(destination_folder, archive_name)

    try:
        # Create a tar.gz archive in /app
        with tarfile.open(temp_archive_path, "w:gz") as tar:
            tar.add(source_folder, arcname=os.path.basename(source_folder))

        # Print the temporary archive name
        print(f"Temporary archive created at: {temp_archive_path}")

        # Copy the archive to the final destination
        shutil.copy(temp_archive_path, final_archive_path)

        # Print the final archive name
        print(f"Archive copied to: {final_archive_path}")

        # Remove the temporary archive
        os.remove(temp_archive_path)
        print(f"Temporary archive removed: {temp_archive_path}")

    except Exception as e:
        print(f"Error creating or copying archive: {str(e)}")

    return final_archive_path

# Function to delete archives older than retention_days
def clean_old_archives(destination_folder, retention_days):
    now = datetime.datetime.now()
    for file in Path(destination_folder).glob('*_backup_*.tar.gz'):
        file_creation_time = datetime.datetime.fromtimestamp(file.stat().st_ctime)
        file_age = (now - file_creation_time).days
        if file_age > retention_days:
            os.remove(file)

# Main script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup Docker container data.")
    parser.add_argument('container_name', help="Name of the Docker container to stop and start")
    parser.add_argument('source_folder', help="Path to the source folder to back up")
    parser.add_argument('destination_folder', help="Path to the backup storage")
    parser.add_argument('retention_days', type=int, help="Number of days to retain backups")
    args = parser.parse_args()

    container_name = args.container_name
    source_folder = args.source_folder
    destination_folder = args.destination_folder
    retention_days = args.retention_days

    # Stop the container
    stop_container(container_name)

    try:
        # Create the archive
        archive_path = create_archive(container_name, source_folder, destination_folder)
        print(f"Archive created at {archive_path}")
    finally:
        # Ensure the container is started again
        start_container(container_name)

    # Clean up old archives
    clean_old_archives(destination_folder, retention_days)
    print(f"Old archives cleaned up from {destination_folder}")
