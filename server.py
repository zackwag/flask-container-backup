import json
import os
import subprocess
import sys
import threading
from datetime import datetime

import requests
from flask import Flask, jsonify

app = Flask(__name__)

FLASK_PORT = 2128
MODE = os.environ.get('MODE', 'spoke').lower()
CONFIG_DIR = '/app/config'
RESULT_FILE = os.path.join(CONFIG_DIR, 'backup_result.json')
CONTAINERS_FILE = os.path.join(CONFIG_DIR, 'containers.json')
SPOKES_FILE = os.path.join(CONFIG_DIR, 'spokes.json')


def write_result(status, errors=None, containers_backed_up=None):
    result = {
        "status": status,
        "errors": errors or [],
        "containers_backed_up": containers_backed_up or [],
        "timestamp": datetime.now().isoformat()
    }
    with open(RESULT_FILE, 'w') as f:
        json.dump(result, f)


def read_local_result():
    try:
        with open(RESULT_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"status": "no_backup_run", "timestamp": None}


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
        print(result.stdout)
        return True
    except Exception as e:
        print(f"Error backing up container {container_name}: {str(e)}")
        return False


def notify_spoke(spoke_url):
    try:
        response = requests.post(f"{spoke_url}/backup", timeout=10)
        return {"spoke": spoke_url, "status": response.status_code}
    except Exception as e:
        print(f"Error notifying spoke {spoke_url}: {str(e)}")
        return {"spoke": spoke_url, "error": str(e)}


def get_spoke_status(spoke_url):
    try:
        response = requests.get(f"{spoke_url}/status", timeout=10)
        return {"spoke": spoke_url, "result": response.json()}
    except Exception as e:
        return {"spoke": spoke_url, "error": str(e)}


# Load containers
with open(CONTAINERS_FILE) as f:
    containers = json.load(f)

# Load spokes if hub mode
spokes = []
if MODE == 'hub':
    if not os.path.exists(SPOKES_FILE):
        print("FATAL: MODE=hub but spokes.json not found", file=sys.stderr)
        sys.exit(1)
    with open(SPOKES_FILE) as f:
        spokes = json.load(f)
    if not spokes:
        print("FATAL: MODE=hub but spokes.json is empty", file=sys.stderr)
        sys.exit(1)
    print(f"Hub mode enabled with {len(spokes)} spoke(s)")
else:
    print("Spoke mode enabled")

# Per-container endpoints
for container in containers:
    container_name = container["container_name"]
    source_folder = container["source_folder"]
    destination_folder = container["destination_folder"]
    retention_days = container["retention_days"]

    def create_backup_endpoint(container_name, source_folder, destination_folder, retention_days):
        def backup():
            threading.Thread(
                target=backup_container,
                args=(container_name, source_folder, destination_folder, retention_days)
            ).start()
            return jsonify({'status': 'Backup started', 'container': container_name}), 202
        return backup

    endpoint = f'/backup/{container_name}'
    app.add_url_rule(
        endpoint,
        endpoint,
        create_backup_endpoint(container_name, source_folder, destination_folder, retention_days),
        methods=['POST']
    )


@app.route('/backup', methods=['POST'])
def backup_all():
    def run_all():
        errors = []
        backed_up = []
        lock = threading.Lock()
        threads = []

        def run_backup(container):
            success = backup_container(
                container["container_name"],
                container["source_folder"],
                container["destination_folder"],
                container["retention_days"]
            )
            with lock:
                if success:
                    backed_up.append(container["container_name"])
                else:
                    errors.append(container["container_name"])

        for container in containers:
            t = threading.Thread(target=run_backup, args=(container,))
            threads.append(t)
            t.start()

        spoke_threads = []
        if MODE == 'hub':
            for spoke in spokes:
                t = threading.Thread(target=notify_spoke, args=(spoke["url"],))
                spoke_threads.append(t)
                t.start()

        for t in threads + spoke_threads:
            t.join()

        status = "success" if not errors else "failed"
        write_result(status, errors, backed_up)

    threading.Thread(target=run_all).start()
    return jsonify({'status': 'Backup started'}), 202


@app.route('/status', methods=['GET'])
def status():
    local_result = read_local_result()

    if MODE == 'spoke':
        return jsonify({
            "overall_status": local_result.get("status", "unknown"),
            "local": local_result
        }), 200

    # Hub mode -- aggregate all spokes
    spoke_statuses = [get_spoke_status(spoke["url"]) for spoke in spokes]

    all_statuses = [local_result.get("status")]
    for s in spoke_statuses:
        if "result" in s:
            all_statuses.append(s["result"].get("overall_status", "unknown"))
        else:
            all_statuses.append("failed")

    overall = "success" if all(s == "success" for s in all_statuses) else "failed"

    return jsonify({
        "overall_status": overall,
        "local": local_result,
        "spokes": spoke_statuses
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT)
