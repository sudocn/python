import struct

def print_pkt_hdr(pkt_hdr):
    #pkt_hdr = fin.read(0x20)
    #(index, capture_len, )
    hdr1 = struct.unpack("HHi", pkt_hdr[8:16])
    hdr2 = struct.unpack("16B", pkt_hdr[16:])
    print hdr1
    #print hdr2

def print_pkt_data(data):
    data_hex = struct.unpack(str(len(data))+"B", data)
    #print data_hex 
    for i in range(len(data_hex)):
        print '%02X'%data_hex[i],
    print

def read_pkt(fin):
    pad_len = 68
    # packet header, 0x20 bytes
    pkt_hdr = fin.read(0x20)
    (index, data_len) = struct.unpack("II", pkt_hdr[:8])
    print "index:", index, "data", data_len,
    print_pkt_hdr(pkt_hdr)
    # packet data contents, variable length
    print "offset 0x%x" % fin.tell()
    data = fin.read(data_len)
    print_pkt_data(data)
    # padding (or somthing we don't know), 68 bytes
    padding = fin.read(pad_len)

infile = "ps loop mode A.tol"
fin = open(infile, 'rb')
file_hdr = fin.read(0xb0)
#fout = open("loopA.log", 'w')

for i in range(235):
#for i in range(5):
    read_pkt(fin)

#read_pkt(fin)

fin.close()
