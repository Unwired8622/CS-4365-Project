import socket

HOST = '127.0.0.1'
PORT = 65432

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            print(f"Connected to Server at {HOST} on Port {PORT}")
            print("Type a message to echo (or 'quit' to exit):")

            while True:
                msg = input("You: ")
                if msg.lower() == 'quit':
                    break
                
                client_socket.sendall(msg.encode('utf-8'))
                
                response = client_socket.recv(1024)
                print(f"Server Echo: {response.decode('utf-8')}")
                
        except ConnectionRefusedError:
            print("Could not connect to the server.")

if __name__ == "__main__":
    start_client()