import socket
import asyncio
import time

storage = {}
expiration_store = {}


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Accepted connection from {addr}")

    try:
        while True:
            request = await reader.read(1024)
            if not request:
                break
            data = request.decode().strip()
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
                
    except asyncio.CancelledError:
        print(f"Connection with {addr} was cancelled")
    except Exception as e:
        print(f"Exception occurred with {addr}: {e}")

    print(f"Closing connection with {addr}")
    writer.close()


async def main():

    server = await asyncio.start_server(handle_client, 'localhost', 6379)
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



if __name__  == "__main__":

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("KeyboardInterrupt: shutting down...")