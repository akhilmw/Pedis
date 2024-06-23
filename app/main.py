import asyncio
import time
import argparse

storage = {}
expiration_store = {}
slaves = []

def parse_args():
    parser = argparse.ArgumentParser(description='Redis server with custom port and replication support.')
    parser.add_argument('--port', type=int, default=6379, help='Port number to run the server on (default: 6379)')
    parser.add_argument('--replicaof', metavar='<MASTER_HOST> <MASTER_PORT>', type=str, nargs=1, help='Make the server a replica of another Redis server')
    return parser.parse_args()

async def connect_to_master(master_host, master_port, slave_port):
    reader, writer = await asyncio.open_connection(master_host, master_port)
    ping_command = "*1\r\n$4\r\nPING\r\n".encode()
    writer.write(ping_command)
    await writer.drain()
    response = await reader.read(100)
    if response != b"+PONG\r\n":
    #logging.error(f"Unexpected response to PING: {response}")
        return
    # Send REPLCONF listening-port command as RESP array
    replconf_listening_port_message = f"*3\r\n$8\r\nREPLCONF\r\n$14\r\nlistening-port\r\n${len(str(slave_port))}\r\n{slave_port}\r\n"
    writer.write(replconf_listening_port_message.encode("utf-8"))
    await writer.drain()
    # Wait for REPLCONF response
    response = await reader.read(100)
    if response != b"+OK\r\n":
        #logging.error(f"Unexpected response to REPLCONF listening-port: {response}")
        return
    # Send REPLCONF capa psync2 command as RESP array
    replconf_capa_message = "*3\r\n$8\r\nREPLCONF\r\n$4\r\ncapa\r\n$6\r\npsync2\r\n"
    writer.write(replconf_capa_message.encode("utf-8"))
    await writer.drain()
    # Wait for REPLCONF response
    response = await reader.read(100)
    if response != b"+OK\r\n":
        #logging.error(f"Unexpected response to REPLCONF capa: {response}")
        return

    psync_command = "*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n".encode()
    writer.write(psync_command)
    await writer.drain()
    

    
    writer.close()
    await writer.wait_closed()

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Accepted connection from {addr}")

    try:
        while True:
            request = await reader.read(1024)
            if not request:
                break
            data = request.decode().strip()
            print(f"Received data: {data}")
            # RESP protocol handling
            parts = data.split("\r\n")
            if parts[0].startswith("*"):
                array_len = int(parts[0][1:])
                if array_len == 1 and parts[2].upper() == "PING":
                    response = b"+PONG\r\n"
                    writer.write(response)
                    await writer.drain()
                elif array_len >= 3:
                    if parts[2].upper() == "SET" and len(parts) >= 7:
                        key = parts[4]
                        value = parts[6]
                        if len(parts) >= 10 and parts[8].upper() == "PX":
                            expire_time = int(parts[10])
                            expiration_store[key] = time.time() + expire_time / 1000.0
                        storage[key] = value
                        response = b"+OK\r\n"
                        writer.write(response)
                        await writer.drain()
                    elif parts[2].upper() == "REPLCONF":
                        response = b"+OK\r\n"
                        writer.write(response)
                        await writer.drain()
                elif array_len == 2 and parts[2].upper() == "GET":
                    key = parts[4]
                    if key in expiration_store:
                        if time.time() > expiration_store[key]:
                            del storage[key]
                            del expiration_store[key]
                            value = None
                        else:
                            value = storage.get(key, None)
                    else:
                        value = storage.get(key, None)

                    if value is None:
                        response = b"$-1\r\n"
                    else:
                        response = f"${len(value)}\r\n{value}\r\n".encode()
                    writer.write(response)
                    await writer.drain()
                elif array_len == 2 and parts[2].upper() == "ECHO":
                    message = parts[4]
                    response = f"${len(message)}\r\n{message}\r\n".encode()
                    writer.write(response)
                    await writer.drain()
                elif array_len == 2 and parts[2].upper() == "INFO" and parts[4].upper() == "REPLICATION":
                    if not slaves:
                        response = b"$89\r\nrole:master\r\nmaster_replid:8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb\r\nmaster_repl_offset:0\r\n"
                    else:
                        response = b"$10\r\nrole:slave\r\n"
                    writer.write(response)
                    await writer.drain()
            
    except asyncio.CancelledError:
        print(f"Connection with {addr} was cancelled")
    except Exception as e:
        print(f"Exception occurred with {addr}: {e}")

    print(f"Closing connection with {addr}")
    writer.close()


async def main(port, master_host=None, master_port=None):
    if master_host and master_port:
        await connect_to_master(master_host, master_port, port)
    
    server = await asyncio.start_server(handle_client, 'localhost', port)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        print("Server is shutting down...")
    finally:
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    args = parse_args()
    print(args)
    
    if args.replicaof:
        master_host, master_port = args.replicaof[0].split()
        master_port = int(master_port)  # Ensure master_port is an integer
        slaves.append(f"{master_host}:{master_port}")
        try:
            asyncio.run(main(args.port, master_host, master_port))
        except KeyboardInterrupt:
            print("KeyboardInterrupt: shutting down...")
    else:
        try:
            asyncio.run(main(args.port))
        except KeyboardInterrupt:
            print("KeyboardInterrupt: shutting down...")
