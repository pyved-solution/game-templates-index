import asyncio
import json
import websockets

__all__ = [
    'get_server_flag',
    'start_comms',
    'broadcast',
    'register_mediator',
    'shutdown_comms'
]

mediators = []
connected_clients = set()

# Returns a flag indicating that this is a server implementation
def get_server_flag() -> int:
    return 1

# Handles incoming messages from clients
async def handle_client(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            evtype, content = message.split('#')
            for mediator in mediators:
                mediator.post(evtype, json.loads(content), False)
    finally:
        connected_clients.remove(websocket)

# Starts the server communication
async def start_server(host_info, port_info):
    server = await websockets.serve(handle_client, host_info, port_info)
    await server.wait_closed()

def start_comms(host_info, port_info):
    asyncio.get_event_loop().run_until_complete(start_server(host_info, port_info))
    asyncio.get_event_loop().run_forever()

# Broadcasts an event to all connected clients
async def _broadcast(event_type, event_content):
    data = f'{event_type}#{json.dumps(event_content)}'
    await asyncio.wait([client.send(data) for client in connected_clients])

def broadcast(event_type, event_content):
    asyncio.run(_broadcast(event_type, event_content))

# Registers a mediator for handling events
def register_mediator(mediator):
    mediators.append(mediator)

# Shuts down the server communication
def shutdown_comms():
    for client in connected_clients:
        asyncio.run(client.close())
    connected_clients.clear()
