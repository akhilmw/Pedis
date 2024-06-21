import socket
import asyncio


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Accepted connection from {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            message = data.decode()
            if "ping" in message.lower():
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