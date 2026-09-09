import socket

def send_command(*parts):
    resp = f"*{len(parts)}\r\n" + "".join(f"${len(p)}\r\n{p}\r\n" for p in parts)
    s = socket.create_connection(("localhost", 6379))
    s.sendall(resp.encode())
    print("Sent:", parts, "-> Got:", s.recv(1024))
    s.close()

send_command("PING")
send_command("ECHO", "hey")
send_command("echo", "randomStringHere")  # test case-insensitivity