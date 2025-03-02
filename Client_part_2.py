import socket
import json
import os
import threading
import time
import signal
import sys

BUFFER_SIZE = 1024
INPUT_FILE = 'input.txt'
OUTPUT_FOLDER = 'output'
LOG_FILE = 'download_log.txt'

PRIORITY_MAP = {
    'CRITICAL': 10,
    'HIGH': 4,
    'NORMAL': 1
}

class DownloadTask:
    def __init__(self, file_name, priority):
        self.file_name = file_name
        self.priority = PRIORITY_MAP[priority]
        self.downloaded_size = 0
        self.total_size = 0

tasks = []
tasks_lock = threading.Lock()

def read_input_file():
    global tasks
    new_tasks = []
    with open(INPUT_FILE, 'r') as f:
        lines = f.readlines()
        for line in lines:
            file_name, priority = line.strip().split()
            new_tasks.append(DownloadTask(file_name, priority))
    with tasks_lock:
        tasks = new_tasks

def update_file_list():
    while True:
        read_input_file()
        time.sleep(2)

def handle_signal(sig, frame):
    print("\nExiting...")
    sys.exit(0)

def recv_exact(sock, length):
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet
    return data

def log_download_progress(message):
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(message + '\n')

def download_file(task, client_socket):
    chunk_size = BUFFER_SIZE * task.priority

    while task.downloaded_size < task.total_size:
        request_data = json.dumps({
            'file_name': task.file_name,
            'offset': task.downloaded_size,
            'chunk_size': chunk_size
        })

        client_socket.sendall(request_data.encode())
        data = recv_exact(client_socket, min(chunk_size, task.total_size - task.downloaded_size))
        if not data:
            break

        output_path = os.path.join(OUTPUT_FOLDER, task.file_name)
        with open(output_path, 'ab') as f:
            f.write(data)

        task.downloaded_size += len(data)
        percent_complete = int((task.downloaded_size / task.total_size) * 100)
        log_message = f"Downloading {task.file_name} .... {min(percent_complete, 100)}%"
        print(log_message)
        log_download_progress(log_message)

    log_message = f"{task.file_name} has been downloaded successfully."
    print(log_message)
    log_download_progress(log_message)

def download_task(task, file_list, server_host, server_port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    if task.total_size == 0:
        task.total_size = file_list[task.file_name]

    download_file(task, client_socket)
    client_socket.close()

def main():
    server_host = input("Please enter the server's IP address: ")
    server_port = int(input("Please enter the server's port number: "))

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    signal.signal(signal.SIGINT, handle_signal)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    file_data = client_socket.recv(BUFFER_SIZE).decode()
    file_list = json.loads(file_data)
    client_socket.close()

    read_input_file()
    completed_files = set()

    input_thread = threading.Thread(target=update_file_list)
    input_thread.start()

    while True:
        threads = []
        with tasks_lock:
            for task in tasks:
                if task.file_name in completed_files:
                    continue

                if task.total_size == 0:
                    task.total_size = file_list[task.file_name]

                download_thread = threading.Thread(target=download_task, args=(task, file_list, server_host, server_port))
                threads.append(download_thread)
                download_thread.start()

        for thread in threads:
            thread.join()

        with tasks_lock:
            for task in tasks:
                if task.downloaded_size >= task.total_size:
                    completed_files.add(task.file_name)

        time.sleep(2)

if __name__ == "__main__":
    main()
