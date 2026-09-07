import socket

s = socket.create_connection(("localhost", 6379))
s.sendall(b"*1\r\n$4\r\nPING\r\n")
print("got response:", s.recv(1024))
input("connection held open")
s.close()