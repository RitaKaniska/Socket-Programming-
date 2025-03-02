import socket
import json
import os
import time
import threading

IP = socket.gethostbyname(socket.gethostname())

input_file = 'input.txt'
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

downloaded_files = set()

def download_file(file_name, file_size, client_socket):
    with open(os.path.join(output_dir, file_name), 'wb') as f:
        total_received = 0
        while total_received < file_size * 1024 * 1024:
            data = client_socket.recv(1024 * 1024)
            f.write(data)
            total_received += len(data)
            percent = (total_received / (file_size * 1024 * 1024)) * 100
            print(f"Downloading {file_name} .... {percent:.2f}%")

def client_program():
    server_address = (IP, 5000)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    file_list = json.loads(client_socket.recv(1024).decode())
    print("Danh sách file có thể tải xuống:")
    for file, size in file_list.items():
        print(f"{file} - {size}MB")

    while True:
        if os.path.exists(input_file):
            with open(input_file, 'r') as f:
                files_to_download = [line.strip() for line in f.readlines() if line.strip()]

            new_files = [file for file in files_to_download if file not in downloaded_files]
            for file_name in new_files:
                if file_name in file_list:
                    client_socket.send(file_name.encode())
                    file_size = int(client_socket.recv(1024).decode())
                    download_file(file_name, file_size, client_socket)
                    downloaded_files.add(file_name)
                else:
                    print(f"File {file_name} không tồn tại trên server.")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        client_program()
    except KeyboardInterrupt:
        print("Đóng kết nối đến Server và kết thúc chương trình.")
