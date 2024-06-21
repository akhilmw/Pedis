import socket
import asyncio

storedKeys = {}



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
            if data.startswith("*2"):
                parts = data.split("\r\n")
                if parts[2].upper() == "ECHO" and parts[4]:
                    response_data = parts[4]
                    response = f"${len(response_data)}\r\n{response_data}\r\n".encode()
                    writer.write(response)
                    await writer.drain()
                # FOR GET
                elif parts[2].upper() == "GET":
                    key = parts[4]
                    if key in storedKeys:
                        value = storedKeys[key]
                        response = f"${len(value)}\r\n{value}\r\n".encode()
                    else:
                        response = b"$-1\r\n"
                    writer.write(response)
                    await writer.drain()
            # For SET
            elif data.startswith("*3"):
                parts = data.split("\r\n")
                if parts[2].upper() == "SET":
                    key = parts[4]
                    value = parts[6]
                    if key not in storedKeys:
                        storedKeys[key] = value
                        response = f"OK\r\n".encode()
                        writer.write(response)
                        await writer.drain()
            elif "ping" in data.lower():
                response = b"+PONG\r\n"
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