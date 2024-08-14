import json
import subprocess
import threading

from flask import Flask, jsonify

app = Flask(__name__)

# Declare constants
FLASK_PORT = 2128

def backup_container(container_name, source_folder, destination_folder, retention_days):
    try:
        command = [
            'python',
            'backup_container.py',
            container_name,
            source_folder,
            destination_folder,
            str(retention_days)
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)  # Optional: Print the output for debugging
    except Exception as e:
        print(f"Error backing up container {container_name}: {str(e)}")

# Load container data from JSON file
with open('containers.json') as f:
    containers = json.load(f)

# Create endpoints dynamically for each container
for container in containers:
    container_name = container["container_name"]
    source_folder = container["source_folder"]
    destination_folder = container["destination_folder"]
    retention_days = container["retention_days"]

    def create_backup_endpoint(container_name, source_folder, destination_folder, retention_days):
        def backup():
            threading.Thread(target=backup_container, args=(container_name, source_folder, destination_folder, retention_days)).start()
            return jsonify({'status': 'Backup started', 'container': container_name}), 202
        return backup

    endpoint = f'/backup/{container_name}'
    app.add_url_rule(endpoint, endpoint, create_backup_endpoint(container_name, source_folder, destination_folder, retention_days), methods=['POST'])

# Endpoint to backup all containers
@app.route('/backup', methods=['POST'])
def backup_all():
    threads = []
    for container in containers:
        container_name = container["container_name"]
        source_folder = container["source_folder"]
        destination_folder = container["destination_folder"]
        retention_days = container["retention_days"]
        thread = threading.Thread(target=backup_container, args=(container_name, source_folder, destination_folder, retention_days))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return jsonify({'status': 'All backups started'}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT)
