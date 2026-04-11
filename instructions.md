# CS-4365-Project

Checkpoint 2 Overview
This checkpoint of the project creates a TCP client/server network that allows clients to send messages to a server and receive an echo back of their message. It also allows clients to upload files to the server, which are then indexed by the server for semantic search.
Installation
Clone the repository:
git clone https://github.com/Unwired8622/CS-4365-Project.git
cd CS-4365-Project


3. Install Dependencies
bash
pip install -r requirements.txt

./venv/bin/python server.py
This starts the TCP server

In a separate terminal, run:
./venv/bin/python client.py
This starts a TCP client
(Note that multiple clients can be created, but each one is created in its own separate terminal)

When prompted in the terminal, a client can send a message to be echoed back by the server using the echo command.
A client can also upload a file to the server by typing upload filename. This file will appear in the 'uploads' folder in the project directory.

Typing 'quit' will end the client's process.

To upload a file to be embedded, type 'upload filename' in the client terminal. The file will be embedded and indexed by the server. To verify this, you can type open a new terminal and enter the command: ./venv/bin/python rag_pipeline.py. This will run the test code in the pipeline and print the results to the terminal.
