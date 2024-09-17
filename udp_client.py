import socket

def udp_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('10.0.0.2', 12345)

    for i in range(5):
        message = f"Mensaje {i+1}"
        client_socket.sendto(message.encode(), server_address)
        print(f"Mensaje enviado: {message}")

if __name__ == "__main__":
    udp_client()
