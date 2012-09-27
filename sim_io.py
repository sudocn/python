import sys

def trans_sim_o(line):
    line = line[line.find('SIM_IO'):]
    line = line[line.find('(')+1:]
    arr = line.split(',')
# cmd=0xC0 efid=0x6F40 path=3F007F10
    print arr[0][4:], arr[1][5:], arr[2][5:],

def trans_sim_i(line):
    line = line[line.find('SIM_IO'):]
    start = line.find('{')
    if start < 0:
        print " "*12, 'FAIL'
    else:
        line = line[start+1:]
        arr = line.split(',')
#{sw1=0x90,sw2=0x0,0000000a2fe204000bffbb2102000000}
        print " "*12, arr[0][4:], arr[1][4:], arr[2][:-2]

with open(r"d:\cpeng\sim_io.log", "r") as f:
    for line in f:
        if line.find('> SIM_IO') > 0:
            trans_sim_o(line)
        elif line.find('< SIM_IO') > 0:
            trans_sim_i(line)
        elif line.find('Fatal') > 0:
            print line
