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
        print("\n[System] Server closed connection.")
        return False
    
    payload_len = struct.unpack('!I', header)[0]
    payload = recvAll(sock, payload_len)
    if not payload:
        print("\n[Error] receiving payload from server.")
        return False
    
    command_id = payload[0]
    data = payload[1:]
    
    if command_id == 0x01:
        print(f"\n[Echo] {data.decode('utf-8')}")
    elif command_id == 0x05:
        response = data.decode('utf-8')
        if "ANSWER: " in response:
            answer, sources = response.split("\nSOURCES: ")
            print(f"\n{'='*60}")
            print(f"AI SEARCH RESULT:")
            print(f"{'-'*60}")
            print(answer.replace("ANSWER: ", ""))
            print(f"{'-'*60}")
            print(f"Sources: {sources}")
            print(f"{'='*60}")
        else:
            print(f"\n[Search Result] {response}")
    elif command_id == 0x06:
        print(f"\n{data.decode('utf-8')}")
    return True

def upload_file(sock, file_path):
    if not os.path.exists(file_path):
        print(f"\n[Error] File '{file_path}' does not exist.")
        return

    filename = os.path.basename(file_path)
    print(f"\n[Upload] Preparing to send '{filename}'...")
    sendPacket(sock, 0x02, filename.encode('utf-8'))
    
    file_size = os.path.getsize(file_path)
    bytes_sent = 0
    
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            sendPacket(sock, 0x03, chunk)
            bytes_sent += len(chunk)
            # Simple progress log
            if bytes_sent % (CHUNK_SIZE * 10) == 0 or bytes_sent == file_size:
                print(f" Sent {bytes_sent}/{file_size} bytes...", end='\r')
    
    print("\n[Upload] Waiting for indexing...")
    sendPacket(sock, 0x04, b'')
    handleResponse(sock)

def start_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((HOST, PORT))
            print(f"\n{'-'*40}")
            print(f"AI CONTEXT SEARCH CLIENT")
            print(f"Connected to {HOST}:{PORT}")
            print(f"{'-'*40}")
            print("Commands:")
            print("  - 'search <query>' : Semantic AI search")
            print("  - 'upload <file>'  : Index a new text file")
            print("  - 'list'           : Show indexed files")
            print("  - 'quit'           : Exit application")
            print(f"{'-'*40}")

            while True:
                userInput = input("\nQuery/Command > ")
                if not userInput.strip():
                    continue
                
                lowered_input = userInput.lower()
                
                if lowered_input == 'quit':
                    print("Goodbye!")
                    break
                
                elif lowered_input == 'list':
                    sendPacket(client_socket, 0x06, b'')
                    handleResponse(client_socket)

                elif lowered_input.startswith('upload '):
                    parts = userInput.split(' ', 1)
                    if len(parts) > 1:
                        upload_file(client_socket, parts[1])
                    else:
                        print("Usage: upload <filename>")
                
                elif lowered_input.startswith('search '):
                    parts = userInput.split(' ', 1)
                    if len(parts) > 1:
                        print("[System] Quering AI Layer...")
                        sendPacket(client_socket, 0x05, parts[1].encode('utf-8'))
                        handleResponse(client_socket)
                    else:
                        print("Usage: search <query>")
                
                else:
                    # Default to echo if no command recognized
                    sendPacket(client_socket, 0x01, userInput.encode('utf-8'))
                    if not handleResponse(client_socket):
                        break
                
        except ConnectionRefusedError:
            print("[Error] Could not connect to the server. Make sure it is running.")
        except Exception as e:
            print(f"[Error] {e}")

if __name__ == "__main__":
    start_client()