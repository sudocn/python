import socket

HOST='localhost'
PORT=50007
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print 'send hello'
#s.sendto('', (HOST,PORT))
s.sendto('hello', (HOST,PORT))
while 1:
    data,addr = s.recvfrom(1024)
    if not data: break
    print 'recv:', addr, data
s.sendto('', (HOST,PORT))
s.close()
