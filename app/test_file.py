import socket

def send_ping():
    s = socket.create_connection(("localhost", 6379))
    s.sendall(b"*1\r\n$4\r\nPING\r\n")
    response = s.recv(1024)
    print("got response:", response)
    s.close()

send_ping()

