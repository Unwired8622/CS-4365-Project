# Client/Server Context Searching (CS 4365/6365)

This project implements a secure TCP client-server system featuring advanced AI-powered semantic search. Users can upload text documents to a central server, which automatically indexes them using a custom RAG (Retrieval-Augmented Generation) pipeline and enables natural language querying via Grok AI.

## Project Status: Final Delivery (Checkpoint 6 Complete)

### Features
- **Binary File Transfer**: Robust protocol for uploading `.txt` files.
- **AI Vectorization Layer**: Semantic indexing using `SentenceTransformers`.
- **Reasoning Engine**: Natural language answering powered by **Grok 3 (via OpenRouter)**.
- **Dynamic Re-indexing**: The server automatically updates its brain whenever a new file is uploaded.

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Unwired8622/CS-4365-Project.git
   cd CS-4365-Project
   ```

2. **Setup Virtual Environment & Dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the root directory (using `.env.template` as a guide):
   ```env
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_MODEL=x-ai/grok-3-beta
   ```

---

## Execution

### 1. Start the Server
The server manages the RAG pipeline and handles client requests.
```bash
python3 server.py
```

### 2. Start the Client
Launch the interactive CLI in a new terminal window:
```bash
python3 client.py
```

---

## Client Commands

| Command | Description |
|---------|-------------|
| `upload <filename>` | Upload and index a text file (e.g., `upload lore.txt`) |
| `search <query>` | Ask a natural language question (e.g., `search Who is Frodo?`) |
| `list` | Show all documents currently indexed on the server |
| `echo <message>` | Verify the TCP connection with a simple echo |
| `quit` | Safely disconnect and exit the application |

---

## Technical Details
- **Natural Language Search**: Uses `all-MiniLM-L6-v2` for local embeddings and `Grok AI` for context-aware reasoning.
- **Protocol**: Custom framing with 4-byte length headers and command ID bytes.
- **Concurrency**: Multi-threaded server supporting multiple simultaneous client connections.
