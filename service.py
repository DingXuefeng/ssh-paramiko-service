#!/usr/bin/env python3
import os
import queue
import threading
import paramiko
from flask import Flask, jsonify, request
import yaml
import time
default_config = {
    "max_connections": 1,
    "num_workers": 1,
}
service_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(service_dir, 'external', 'config.yaml')
if os.path.isfile(config_path):
    print('file: ',config_path)
    time.sleep(10)
    with open(config_path, 'r') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)
else:
    config = default_config

ssh_connections = queue.Queue()
task_queue = queue.Queue()
workers = []

app = Flask(__name__)

def init_ssh_resources():
    print('collecting ssh resources')
    max_connections = int(config["max_connections"])
    private_key = paramiko.RSAKey.from_private_key_file(config["server"]["pkey"])

    for _ in range(max_connections):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(config["server"]["host"], username=config["server"]["user"], pkey=private_key)
        ssh_connections.put(ssh_client)

def init_worker_resources():
    print('starting worker threads')
    num_workers = int(config["num_workers"])

    for _ in range(num_workers):
        worker = threading.Thread(target=ssh_worker)
        worker.start()
        workers.append(worker)

def release_resources():
    print('releasing resource')

    # Stop worker threads
    num_workers = int(config["num_workers"])
    for _ in range(num_workers):
        task_queue.put(None)
    for worker in workers:
        worker.join()

    # Close SSH connections
    while not ssh_connections.empty():
        ssh_client = ssh_connections.get()
        ssh_client.close()

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

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    command = data.get('command')
    if not command:
        response = {
            'error': 'Command key is missing or empty in the request payload'
        }
        return jsonify(response), 400
    response = {}
    task_queue.put((command, response))
    task_queue.join()
    return jsonify(response)

if __name__ == '__main__':
    init_ssh_resources()
    init_worker_resources()

    try:
        app.run()
    finally:
        print("shutting down")
        release_resources()