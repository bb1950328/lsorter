import socket, pickle
si = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    si.bind(("192.168.178.21", 56789))
    file = open("./captured/captured.db", "a")
    while True:
        print("sent request.")
        row = self.si.recv(1024)
        print("Received: ", row)
        file.write(row.encode() + "\n")
finally:
    file.close()