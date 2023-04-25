#!/usr/bin/env python3
import queue
import threading
import paramiko
from flask import Flask, jsonify, request
import yaml
import time

with open("external/config.yaml", 'r') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

app = Flask(__name__)

# Set up the SSH connection pool
max_connections = int(config["max_connections"])
ssh_connections = queue.Queue(max_connections)

# Load your private key
private_key = paramiko.RSAKey.from_private_key_file(config["server"]["pkey"])

for _ in range(max_connections):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(config["server"]["host"], username=config["server"]["user"], pkey=private_key)
    ssh_connections.put(ssh_client)

# Task queue
task_queue = queue.Queue()

def execute_ssh_task(ssh_client, command):
    channel = ssh_client.get_transport().open_session()
    print('start!')
    channel.exec_command(command)
    print('wating for command to finish')
    while not channel.exit_status_ready():
        time.sleep(1)

    stdout = channel.makefile('rb', -1)
    stderr = channel.makefile_stderr('rb', -1)
    output = stdout.read().decode()
    error = stderr.read().decode()
    print('output:', output)
    print('error:',error)
    return output,error

def ssh_worker():
    while True:
        task = task_queue.get()
        if task is None:
            break

        command, response = task
        ssh_client = ssh_connections.get()
        try:
            output,error = execute_ssh_task(ssh_client,command)
            response['output'] = output
            response['error'] = error
        finally:
            ssh_connections.put(ssh_client)
            task_queue.task_done()

# Start worker threads
num_workers = int(config["num_workers"])
workers = []
for _ in range(num_workers):
    worker = threading.Thread(target=ssh_worker)
    worker.start()
    workers.append(worker)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    command = data.get('command')
    response = {}
    task_queue.put((command, response))
    task_queue.join()
    return jsonify(response)

if __name__ == '__main__':
    try:
        app.run()
    finally:
        # Stop worker threads
        for _ in range(num_workers):
            task_queue.put(None)
        for worker in workers:
            worker.join()

        # Close SSH connections
        while not ssh_connections.empty():
            ssh_client = ssh_connections.get()
            ssh_client.close()
