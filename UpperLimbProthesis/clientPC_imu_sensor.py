import socket

host = '192.168.1.10'                                       #raspberry pi (server) ip address for home wifi
host2 = '10.154.56.46'                                      #ip address for ncsu wifi
port = 5560                                                 #arbitrary, must match between client and server

while True:
    location = input("HOME or NCSU: ")
    if location == 'HOME' or location == 'NCSU':
        break

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)        #creates socket

if location == 'HOME':
    s.connect((host,port))                                      #creates a connection with the server
elif location == 'NCSU':
    s.connect((host2,port))

while True:
    command = input("Enter your command: ")
    if command == 's':                                      #single reading from force sensor
        s.send(str.encode(command))
        reply = s.recv(1024)
        print(reply.decode('utf-8'))
    elif command == 'c':                                    #continous readings from force sensor
        try:
            while True:                                     #repeatedly sends the same command to server
                s.send(str.encode(command))     
                reply = s.recv(1024)
                print(reply.decode('utf-8'))
        except:                                             #Keyboard interrupt to end continous mode                                            
            continue
    elif command == 'q':                                    #closes the server and the connection
        s.send(str.encode(command))
        break
    else:
        print("Invalid command")
        continue

s.close()
