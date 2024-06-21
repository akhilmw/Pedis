
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

