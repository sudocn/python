from __future__ import print_function
import os, sys

UNIT = 83   # 83us, one bit
HALF_UNIT = 42

USB_PID = [
[[0,0,1,1,1,1,0,0], "PRE   "],
[[0,1,0,0,1,0,1,1], "ACK   "],
[[0,1,0,1,1,0,1,0], "NAK   "],
[[0,1,1,1,1,0,0,0], "STALL "],
[[1,0,0,0,0,1,1,1], "OUT   "],
[[1,0,0,1,0,1,1,0], "IN    "],
[[1,0,1,0,0,1,0,1], "SOF   "],
[[1,0,1,1,0,1,0,0], "SETUP "],
[[1,1,0,0,0,0,1,1], "DATA0 "],
[[1,1,0,1,0,0,1,0], "DATA1 "]]

#filename=r'C:\Documents and Settings\cpeng\Desktop\python\usb_capture.csv'
#filename=r'C:\Documents and Settings\cpeng\Desktop\python\usb.csv'
filename = r'C:\Documents and Settings\cpeng\Desktop\USB\LA Caputre\enumerate_fail_1'
#filename = r'/home/cpeng/prog/enum'
global out

class ParseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def nrzi_decode(pkt):
    NRZI_SEQUNCE = [0,1,1,1,1,1,1]
    decoded = []
    dec_dbg = []
    dbg = False
    stuffing_bit = 0
    #for pulse in pkt[1:]: #zhiyuan
    for pulse in pkt:
        count = pulse[2] / UNIT
        if pulse[2] % UNIT > HALF_UNIT:
            count += 1
        if dbg: print ("nrzi:", count, pulse)
        if count > 7: continue
            #raise ParseError("Wrong NRZI code: core than 7 continous 1s")
        if count == 7: stuffing_bit = 2  # next loop's first zero should remove

        # append decoded bits
        if stuffing_bit == 1:
            print ("stuffing bit removed")
            stuffing_bit = 0
            decoded.extend(NRZI_SEQUNCE[1:count])
            if dbg: dec_dbg.append(NRZI_SEQUNCE[1:count])
        else:
            decoded.extend(NRZI_SEQUNCE[:count])
            if dbg: dec_dbg.append(NRZI_SEQUNCE[:count])

        if stuffing_bit:
            stuffing_bit -= 1

    if dbg: print (dec_dbg)
    return decoded

# print a packet that in csv mode
def print_csv_pkt(pkt):
    for u in pkt:
        print (u)

# parse USB PID to string
def parse_pid(pid):
    for t in USB_PID:
        if t[0] == pid:
            return t[1]
    return "UNDEF "

# print a NRZI decoded usb packet
def print_usb_pkt(pkt, output):
    if len(pkt) < 16:
        print ("incomplete usb packet:", pkt, file=output)
        return
    
    # find SYNC BYTE
    if pkt[:8] != [0,0,0,0,0,0,0,1]:
        for i in range(1,len(pkt)-8):
            if pkt[i:i+8] == [0,0,0,0,0,0,0,1]:
                break
        print ("! SKIP ", pkt[:i], file=output)
        pkt = pkt[i:]
        #print ("! SYNC BYTE ERROR", end='', file=output)
        if (len(pkt)) < 16:
            print ("incomplete usb packet:", pkt, file=output)
            return

    print (len(pkt), ": ", end='', file=output)

    print (parse_pid(pkt[8:16]), end='', file=output)
    
    for i in range(8,len(pkt)):
        print(pkt[i],end='', file=output)
        if i%8==7:
            print(" ", end='', file=output)
            
    print(file=output)
    
# parse a cvs format packet
# input: pkt in csv raw data format
# return: NRZI decoded, stuffing bit removed packet data 
def parse_csv_packet(pkt):
    global out
    #print_csv_pkt(pkt)
    dec = nrzi_decode(pkt)
    print_usb_pkt(dec, out)#sys.stdout)


#
# Zhiyuan LA capture file
#

#list all files in the same dir, and sort it
#for zhiyuan LA multiple csv files
def list_all_files(fname):
    path = os.path.dirname(fname)
    files = os.listdir(path)
    prefix = files[0]
    rindex = prefix.rindex('_') + 1
    prefix = prefix[:rindex]
    numbers = map(lambda x: int(x[rindex:-4]), files)
    numbers.sort()

    files_sorted = []
    for num in numbers:
        files_sorted.append(os.path.join(path, prefix+str(num)+'.csv'))
    return files_sorted

def filter_jitters(pkt):
    return filter(lambda x: x[1] != 0, pkt)

# split and parse one cvs line
def parse_csv_line(line):
    items = line.split(",")
    if len(items) != 2:
        raise ParseError("length > 2")

    time,value = items
    if time[-1] != 's':
        raise ParseError("Not time value")
    else:
        if time[-2:] == 'ns':
            time = int(time[:-2])
        elif time[-2:] == 'us':
            time = int(float(time[:-2])*1000)
        elif time[-2:] == 'ms':
            time = int(float(time[:-2])*1000*1000)
        else: # s
            time = int(float(time[:-1])*1000*1000*1000)
    value = int(value)
    return (time,value)
  
def parse_csv_file(fname):
    pt,pv = 0,0  # previous_time & previous_value
    packet = []
    with open(fname, "r") as f:
        f.readline() # skip the first line
        for line in f:
            try:
                t,v = parse_csv_line(line)
                #print pt,pv,t-pt
                packet.append((pt,pv,t-pt))
                if pv == 0 and t-pt > UNIT + HALF_UNIT:
                    packet = filter_jitters(packet)
                    parse_csv_packet(packet)
                    print (line)
                    #print "> EOP <"
                    packet = []
                
                pt,pv = t,v
            except ParseError as e:
                print (e.__str__, line)


#
# HP LA capture files
#

def parse_hp_line(line):
    #print (line)
    sp = line.split()
    if len(sp) < 4: return (0,0,0)
    dur = float(sp[2])
    if sp[3] == 'us':
        dur *= 1000
    dur = int(dur)
    return (sp[0], sp[1], dur)



def parse_hp_file(fname):
    packet = []
    with open(fname, "r") as f:
        for line in f:
            if not line[0] in {'-', '0'}: continue
            try:
                t,v,d = parse_hp_line(line)
                packet.append((t,v,d))
                #print(t,v,d)
                if d > 10*UNIT:
                    parse_csv_packet(packet[:-1])
                    packet = []
            except ParseError as e:
                print (e, line)

def main(fname):
    global out
    out = open(r'c:\usb.txt', 'w')

    #parse_csv_file(fname)
    parse_hp_file(fname)
    out.close()
    
if __name__ == "__main__":
    main(filename)
    
