import socket
import threading

HOST = '127.0.0.1' 
PORT = 65432

def handleClientConnection(conn, addr):
    print(f"New connection from {addr} connected.")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"{addr} Received: {message}")
            
            conn.sendall(data)
    except ConnectionResetError:
        print(f"Connection lost with {addr}")
    finally:
        conn.close()
        print(f"{addr} closed.")

def runServer():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server is starting on {HOST} on port {PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handleClientConnection, args=(conn, addr))
        thread.start()
        print(f"Current active clients: {threading.active_count() - 1}")

if __name__ == "__main__":
    runServer()