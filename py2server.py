#THIS IS FOR PYTHON 2!!!
import socket, sys
_s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_s1.bind(("localhost", 12345))
_s1.listen(1)
while True:
    _komm, _addr = _s1.accept()
    while True:
        _data = _komm.recv(1024)
        if not _data:
            _komm.close()
            sys.exit()
        break
        exec(_data.decode())