import socket
import threading
import json

__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator',
    'shutdown_comms'
]

mediators = []
inbound_connections = []
ref_threads = []

# Returns a flag indicating that this is a server implementation
def get_server_flag() -> int:
    return 1


# Handles client connections
def handle_client(conn):
    print('*server receiving client connection*')
    with conn:
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


# Starts the server communication
def start_comms(host_info, port_info):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host_info, port_info))
    server_socket.listen()
    print(f'Server listening on {host_info}:{port_info}')
    for _ in range(2):
        thread = threading.Thread(target=accept_clients, args=(server_socket,))
        thread.start()
        ref_threads.append(thread)


def accept_clients(server_socket):
    while True:
        conn, addr = server_socket.accept()
        print('...client detected')
        inbound_connections.append(conn)
        threading.Thread(target=handle_client, args=(conn,)).start()


# Broadcasts an event to all connected clients
def broadcast(event_type, event_content):
    data = f'{event_type}#{json.dumps(event_content)}~~'
    broken_connections = set()
    for conn in inbound_connections:
        try:
            conn.sendall(data.encode())
        except Exception as e:
            print(f'Error: {e}')
            broken_connections.add(conn)
    for conn in broken_connections:
        inbound_connections.remove(conn)

# Registers a mediator for handling events
def register_mediator(mediator):
    mediators.append(mediator)

# Shuts down the server communication
def shutdown_comms():
    for conn in inbound_connections:
        conn.close()
    inbound_connections.clear()
    for thread in ref_threads:
        thread.join()
