import socket
import time

def send_command(*parts):
    resp = f"*{len(parts)}\r\n" + "".join(f"${len(p)}\r\n{p}\r\n" for p in parts)
    s = socket.create_connection(("localhost", 6379))
    s.sendall(resp.encode())
    response = s.recv(1024)
    print("Sent:", parts, "-> Got:", response)
    s.close()

send_command("SET", "foo", "bar", "PX", "100")
send_command("GET", "foo")          

print("Sleeping 200ms...")
time.sleep(0.2)

send_command("GET", "foo") # nil

