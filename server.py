import socket
import threading
import struct
import os
from rag_pipeline import RAGPipeline

HOST = '127.0.0.1' 
PORT = 65432
UPLOAD_DIR = 'uploads'

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

rag = RAGPipeline(UPLOAD_DIR)

BASE_THREADS = threading.active_count()

def recvAll(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def handleClientConnection(conn, addr):
    print(f"New connection from {addr} connected.")
    try:
        activeFile = None
        while True:
            header = recvAll(conn, 4)
            if not header:
                break
            
            payload_len = struct.unpack('!I', header)[0]
            
            payload = recvAll(conn, payload_len)
            if not payload:
                break
            
            commandID = payload[0]
            data = payload[1:]
            
            if commandID == 0x01:
                message = data.decode('utf-8')
                print(f"{addr} Received Echo: {message}")
                conn.sendall(header + payload)
                
            elif commandID == 0x02:
                filename = data.decode('utf-8')
                print(f"{addr} Starting upload of: {filename}")
                filePath = os.path.join(UPLOAD_DIR, filename)
                activeFile = open(filePath, 'wb')
                
            elif commandID == 0x03:
                if activeFile:
                    activeFile.write(data)
                else:
                    print(f"Error: Received file data without metadata from {addr}")
            
            elif commandID == 0x04:
                if activeFile:
                    activeFile.close()
                    activeFile = None
                    print(f"File upload complete from {addr}")
                    
                    # Trigger re-indexing for the vectorization layer
                    print("Updating AI Vectorization Layer...")
                    rag.reload_documents()
                    
                    messageAck = "File upload successful and indexed".encode('utf-8')
                    ackHeader = struct.pack('!I', len(messageAck) + 1)
                    conn.sendall(ackHeader + b'\x01' + messageAck)

    except ConnectionResetError:
        print(f"Connection lost with {addr}")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        if activeFile:
            activeFile.close()
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
        print(f"Current active clients: {threading.active_count() - BASE_THREADS}")

if __name__ == "__main__":
    runServer()