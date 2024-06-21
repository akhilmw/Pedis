import socket
import concurrent.futures

def handleClient(client_socket):
    with client_socket:

        while True:

            request : bytes = client_socket.recv(1024)
            data : str = request.decode()
            
            if "ping" in data.lower():
                response = b"+PONG\r\n"
                client_socket.sendall(response)


def main():

    server_socket = socket.create_server(("localhost", 6379), reuse_port= True)
    pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

    try:
        while True:
            client_socket, addr = server_socket.accept()
            pool.submit(handleClient, client_socket)
    except KeyboardInterrupt:
        print("Server is shutting down...")
    finally:
        pool.shutdown(wait=True)
        server_socket.close()



if __name__  == "__main__":

    main()