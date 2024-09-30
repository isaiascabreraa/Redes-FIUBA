import os
import sys
import socket
from lib.utils import get_absolute_file_path


NAME_END = "\n"
BUF_SIZE = 2048


# server
def get_filename(header):
    name_end_idx = header.find(NAME_END)
    # print(f"header: {header} - idx: {name_end_idx}")
    return header[:name_end_idx]


def is_upload_header(header):
    if header.startswith("upload.py"):
        return header
    return None


def is_download_header(header):
    if header.startswith("download.py"):
        return header
    return None


# upload.py
def send_file_segment(client_socket, address, port, buffer):
    try:
        client_socket.sendto(buffer, (address, int(port)))
    except socket.error as e:
        print(f"Segment not sended: {e}", file=sys.stderr)
        return


def send_file(file_name, client_socket, address, port, dir_path):
    file_path = get_absolute_file_path(dir_path, file_name)

    if file_path is None:
        print(f"File not found: {file_path}", file=sys.stderr)
        return

    # se abre como binario
    with open(file_path, 'rb') as file:
        buffer = file.read(BUF_SIZE)

        while buffer:
            buffer = b"upload.py" + file_name.encode() + NAME_END.encode() + buffer
            print(f"envio: {buffer}")
            send_file_segment(client_socket, address, port, buffer)
            buffer = file.read(BUF_SIZE)


# download.py
def download_file(client_socket, file_name, download_folder, address, port):
    # client_socket.sendto("download.py".encode(), (SERVER_NAME, SERVER_PORT))
    # download_folder = 'downloaded_files'

    file_path = os.path.join(download_folder, file_name)
    client_socket.sendto(b"download.py" + file_name.encode() + NAME_END.encode(), (address, int(port)))

    with open(file_path, 'wb') as file:
        """
        while True:
            # recibe el archivo
            buffer, client_address = client_socket.recvfrom(BUF_SIZE)
            if buffer == b"EOF":
                break
            file.write(buffer)
        """
        buffer, client_address = client_socket.recvfrom(BUF_SIZE)
        if buffer == b"EOF":
            return
        file.write(buffer)

    print(f"Archivo {file_name} recibido y guardado en {file_path}.")
