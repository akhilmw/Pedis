
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

