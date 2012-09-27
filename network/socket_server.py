import socket

HOST=''
PORT=50007

print 'server start'
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((HOST,PORT))
    #s.listen(1)
    #conn,addr=s.accept()
    #print 'Connected by', addr


    while 1:
        data,addr = s.recvfrom(1024)
        print 'recvfrom:', addr, data
        if not data: break
        for i in range(100):
            s.sendto(data+str(i),addr)
        s.sendto('',addr)
except KeyboardInterrupt:
    pass
except Exception as e:
    print e
finally:
    s.close()
    print 'server stop'

                  
