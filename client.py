import socket
import struct
import os

HOST = '127.0.0.1'
PORT = 65432
CHUNK_SIZE = 4096

def recvAll(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def sendPacket(sock, command_id, payload):
    header = struct.pack('!I', len(payload) + 1)
    sock.sendall(header + bytes([command_id]) + payload)

def handleResponse(sock):
    header = recvAll(sock, 4)
    if not header:
        print("Server closed connection.")
        return False
    
    payload_len = struct.unpack('!I', header)[0]
    payload = recvAll(sock, payload_len)
    if not payload:
        print("Error receiving payload from server.")
        return False
    
    command_id = payload[0]
    data = payload[1:]
    
    if command_id == 0x01:
        print(f"Server: {data.decode('utf-8')}")
    return True

def upload_file(sock, file_path):
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    filename = os.path.basename(file_path)
    
    sendPacket(sock, 0x02, filename.encode('utf-8'))
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            sendPacket(sock, 0x03, chunk)
    
    sendPacket(sock, 0x04, b'')
    print(f"Finished sending '{filename}'. Waiting for server confirmation...")
    handleResponse(sock)

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            print(f"Connected to Server at {HOST} on Port {PORT}")
            print("Commands:")
            print("  - Type a message to echo")
            print("  - 'upload <filename>' to upload a file")
            print("  - 'quit' to exit")

            while True:
                userInput = input("You: ")
                if not userInput.strip():
                    continue
                
                if userInput.lower() == 'quit':
                    break
                
                if userInput.lower().startswith('upload '):
                    parts = userInput.split(' ', 1)
                    if len(parts) > 1:
                        upload_file(client_socket, parts[1])
                    else:
                        print("Usage: upload <filename>")
                else:
                    sendPacket(client_socket, 0x01, userInput.encode('utf-8'))
                    if not handleResponse(client_socket):
                        break
                
        except ConnectionRefusedError:
            print("Could not connect to the server.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_client()