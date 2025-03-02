import socket
import threading
import json

FILE_LIST = "files.json"
SERVER_HOST = socket.gethostbyname(socket.gethostname())
SERVER_PORT = 12345
BUFFER_SIZE = 1024

def load_file_list():
    with open(FILE_LIST, 'r') as f:
        files = json.load(f)
    return files

def handle_client(client_socket):
    files = load_file_list()
    client_socket.sendall(json.dumps(files).encode())

    while True:
        try:
            request = client_socket.recv(BUFFER_SIZE).decode()
            if not request:
                break

            request_data = json.loads(request)
            file_name = request_data['file_name']
            offset = request_data['offset']
            chunk_size = request_data['chunk_size']

            with open(file_name, 'rb') as f:
                f.seek(offset)
                data = f.read(chunk_size)
                client_socket.sendall(data)
        except Exception as e:
            print(f"Exception: {e}")
            break

    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Accepted connection from {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
