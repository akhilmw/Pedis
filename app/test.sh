
# Test for concurrent PING
'''
#!/bin/bash

#Number of concurrent connections to simulate
CONCURRENT_CONNECTIONS=10
HOST="localhost"
PORT=6379

# Function to send ping and read response
send_ping() {
    echo -ne '*1\r\n$4\r\nping\r\n' | nc $HOST $PORT
}

# Loop to simulate concurrent connections
for ((i=1; i<=$CONCURRENT_CONNECTIONS; i++)); do
    send_ping &
done

# Wait for all background processes to finish
wait

'''

# Test for custom Echo

'''
    echo -ne '*2\r\n$4\r\nECHO\r\n$3\r\nhey\r\n' | nc localhost 6379

'''

# Test for Set and Get

''' 
    echo -ne *3\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n | nc localhost 6379

    *2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n

'''

# Test for Set key with expiry px

'''

    *5\r\n$3\r\nSET\r\n$3\r\nfoo\r\n$3\r\nbar\r\n$2\r\nPX\r\n$3\r\n100\r\n
    
'''

# Test for running on a custom port

'''
    python3 main.py --port "port" (give the desired port number)

'''

# To test the INFO replication command:

'''
    echo -ne '*2\r\n$4\r\nINFO\r\n$11\r\nREPLICATION\r\n' | nc localhost <PORT>

'''

# Test The INFO command on a replica:

'''

    eg: python3 main.py --port 6380 --replicaof "localhost 6379" 
    echo -ne '*2\r\n$4\r\nINFO\r\n$11\r\nREPLICATION\r\n' | nc localhost 6380

'''

# TEST for offer and replica ID:

'''
    python3 main.py
    echo -ne '*2\r\n$4\r\nINFO\r\n$11\r\nREPLICATION\r\n' | nc localhost 6379
'''

# TEST for handshake 1

'''
    python3 main.py --port 6379
    python3 main.py --port 6380 --replicaof "localhost 6379"

'''


# TEST for psync

'''
    echo -ne '*3\r\n$5\r\nPSYNC\r\n$1\r\n?\r\n$2\r\n-1\r\n' | nc localhost 6380
    
'''
