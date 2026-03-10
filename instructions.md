# CS-4365-Project

Overview

This project implements a multi-threaded TCP/IP communication system as the foundational layer for a distributed Knowledge Server.
The system allows multiple clients to connect simultaneously to a central server. In this current stage (Checkpoint 2), the server functions as a high-concurrency echo server, verifying the reliability of the network stack and the threading model before moving to binary file transfers and AI vectorization.
Installation

Clone the repository:
Bash

git clone https://github.com/Unwired8622/CS-4365-Project.git

Environment Setup

Ensure you have Python 3.x installed on your system.

For macOS users:
You can verify your installation by running:
Bash

python3 --version

Project Architecture

The project is split into two primary components to facilitate the TCP handshake and data stream:

    server.py

    client.py

Running the Project

To verify the functional TCP connection, you must run the server and client in separate terminal windows.
1. Start the Server

From the project root directory:
Bash

python3 server.py

The server will bind to 127.0.0.1:65432 and enter the LISTEN state.
2. Start the Client

In a new terminal window:
Bash

python3 client.py

AI Workflow & Testing

When using an LLM to assist with this project, it should follow this operational logic:

    Data Transmission: The program prompts for a natural language string. The server will echo back to the sending client the message it receives.

    Concurrency: You can run multiple instances of client.py. The server will log the active thread count to demonstrate concurrent handling.

    Termination: Typing quit closes a client's socket.