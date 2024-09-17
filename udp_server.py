import socket

def udp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('10.0.0.2', 12345))
    print("Servidor UDP listo para recibir mensajes")

    while True:
        message, address = server_socket.recvfrom(1024)
        print(f"Mensaje recibido de {address}: {message.decode()}")

if __name__ == "__main__":
    udp_server()
