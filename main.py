import socket

def main():
    # Dirección IP y puerto del servidor
    host = '127.0.0.1'
    port = 12345

    # Crear un socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Conectar al servidor
        client_socket.connect((host, port))
        print(f"Conectado al servidor {host}:{port}")

        while True:
            # Leer mensaje del usuario
            message = input("Escribe tu mensaje: ")

            if message.lower() == 'salir':
                print("Cerrando conexión...")
                break

            # Enviar mensaje al servidor
            client_socket.sendall(message.encode())

            # Recibir respuesta del servidor
            response = client_socket.recv(1024).decode()
            print(f"Respuesta del servidor: {response}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cerrar el socket
        client_socket.close()

if __name__ == "__main__":
    main()
