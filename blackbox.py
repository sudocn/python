

bx = open(r"e:\blackbox", "rb")
bx.seek(0)
buf = bx.read()
bar = bytearray(buf)
bx.close()

def peek():
  with open(r"e:\poke.csv", "r") as peek:
    for line in peek:
        addr_str, data_str = line.strip().split(',', 1)
        #data_str = data_str.strip(' []')

        data = int(data_str, 16)
        addr = int(addr_str, 16)
        addr = addr - 0x8000
        #print data_str, addr_str, addr

        c1 = bar[addr]
        c2 = bar[addr + 1]
        c3 = bar[addr + 2]
        c4 = bar[addr + 3]

        #print "%x %x %x %x" % (c4, c3, c2, c1)
        value = c1 + (c2 << 8) + (c3 << 16) + (c4 << 24)
        if data != value:
              print line.strip(), hex(value)
        
        #break

def poke():
  with open(r"e:\poke.csv", "r") as peek:
    for line in peek:
        addr_str, data_str = line.split(',', 1)
        #data_str = data_str.strip(' []')

        data = int(data_str, 16)
        addr = int(addr_str, 16)
        addr = addr - 0x8000
        #print data_str, addr_str, addr

        c1 = data & 0xff
        c2 = (data >> 8) & 0xff
        c3 = (data >> 16) & 0xff
        c4 = (data >> 24) & 0xff

        bar[addr] = c1
        bar[addr + 1] = c2
        bar[addr + 2] = c3
        bar[addr + 3] = c4

        #print "%x %x %x %x" % (c4, c3, c2, c1)
        #if data != value:
        #print line, hex(data)
        
        #break

peek()
#poke()

print 'done'
