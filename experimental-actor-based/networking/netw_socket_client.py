import json
import socket
import threading


__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator',
    'shutdown_comms'
]

mediators = []
inbound_connections = []


# Returns a flag indicating that this is a client implementation
def get_server_flag() -> int:
    return 0


# Handles receiving data from the server
def handle_server(conn):
    while True:
        data = conn.recv(1024)
        if not data:
            break
        txt_info = data.decode()

        chunks = txt_info.split('~~')
        for ch in chunks:
            if len(ch):
                parts = ch.split('#')
                evtype = parts[0]
                content = json.loads(parts[1])

                for mediator in mediators:
                    mediator.post(evtype, content, False)


# Starts the client communication
def start_comms(host_info, port_info):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host_info, port_info))
    inbound_connections.append(client_socket)
    threading.Thread(target=handle_server, args=(client_socket,)).start()


# Broadcasts an event to the server
def broadcast(event_type, event_content):
    if not inbound_connections:
        print('warning: called .broadcast but no active connections')
        return
    data = f'{event_type}#{json.dumps(event_content)}~~'
    for conn in inbound_connections:
        conn.sendall(data.encode())


# Registers a mediator for handling events
def register_mediator(mediator):
    mediators.append(mediator)


# Shuts down the communication
def shutdown_comms():
    for conn in inbound_connections:
        conn.close()
    inbound_connections.clear()
