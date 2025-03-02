import os
import socket
import threading
import json

IP = socket.gethostbyname(socket.gethostname())

# Định nghĩa danh sách file và kích thước của chúng
file_list = {
    "File1.zip": 5,
    "File2.zip": 10,
    "File3.zip": 20,
    "File4.zip": 50,
    "File5.zip": 100,
    "File6.zip": 200,
    "File7.zip": 512,
    "File8.zip": 1024,
}

# Lưu danh sách file vào file JSON
with open('file_list.json', 'w') as f:
    json.dump(file_list, f)

def handle_client(client_socket):
    with open('file_list.json', 'r') as f:
        file_list = json.load(f)

    # Gửi danh sách file cho client
    client_socket.send(json.dumps(file_list).encode())

    while True:
        # Nhận tên file cần download từ client
        file_name = client_socket.recv(1024).decode()
        if not file_name:
            break
        
        # Kiểm tra file có tồn tại không
        if file_name in file_list:
            file_size = file_list[file_name]
            client_socket.send(str(file_size).encode())

            # Giả lập quá trình gửi file
            for i in range(file_size):
                client_socket.send(b'0' * (1024 * 1024))  # Giả lập gửi 1MB dữ liệu
        else:
            client_socket.send(b'File not found')

    client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, 5000))
    server.listen(5)
    print("Server đang chạy...")

    while True:
        client_socket, addr = server.accept()
        print(f"Kết nối từ {addr}")

        handle_client(client_socket)

if __name__ == "__main__":
    start_server()
