# analyze CMA allocat/free log, get the allocat/free
# pattern for simulation

import os, sys

peak = 0
mem = 0
distribution = {}
alloc_log =[]
usage_pattern = []

fout = open("d:\\mem_alloc.log", "w")

def log_alloc(log, line, action):
    #print(line)
    global peak, mem
    allocate = False
    if (action[0] == 'a'):
        allocate = True
        
    i = line.find("phy ")
    if i == -1: return
    addr = int(line[i+4: i+4+8], 16)
    if addr == 0xffffffff:
        print(line)
        return

    i = line.find("size ")
    j = line.find(",", i)
    if i == -1: return
    size = int(line[i+5: j], 16)
    page = size >> 12

    if allocate:
        mem += page
        if mem > peak: peak = mem
    else:
        mem -= page
        
    #print("%s %08x %x" % (action, addr, page))
    if (addr > 0x9e000000):
        fout.write("="*8)
    fout.write("%s:%d,%08x\n"%(action, page, addr))
    alloc_log.append((action, page, addr))
    if page in distribution:
        distribution[page] += 1
    else:
        distribution[page] = 1

def parse_alloc_log():
    seq = 0
    for l in alloc_log:
        action, page, addr = l
        if action == 'a':   # allocate
            seq += 1
            usage_pattern.append([action, page, addr, seq])
        else: # free, find correspond allocate
            found = False
            for i in range(len(usage_pattern)-1, -1 , -1):
                if usage_pattern[i][0] == 'a' and \
                    usage_pattern[i][1] == page and \
                    usage_pattern[i][2] == addr:
                    usage_pattern[i][0] = 'A'
                    usage_pattern.append(['F', page, addr, usage_pattern[i][3]])
                    found = True
                    break

            if not found:
                usage_pattern.append(['f', page, addr, 0])
                print("not found",seq, l)
    return seq
                
    
log_file=r'C:\Documents and Settings\cpeng\Desktop\QALog\memory 8\log1.mem.txt'
log = []
with open(log_file, 'r') as f:
   for line in f:
        i = line.find('dma_alloc_coherent:')
        if i != -1:
            log_alloc(log, line[i+20:], 'a')

        i = line.find('dma_free:')
        if i != -1:
            log_alloc(log, line[i+10:], 'f')

fout.close()
print("peak %d pages(%.1fM), mem %d(%.1fM)" % (peak, peak/256.0, mem, mem/256.0))
#print("=========usage=============")
#for l in alloc_log:
#    print(l)
print("======distribution=========")
keys = list(distribution.keys())
keys.sort()

for k in keys:
    print("%d\t%d"%(k, distribution[k]))

count = parse_alloc_log()
with open("d:\\mem_alloc.pat","w") as f:
    f.write("%d\n" % count)
    for l in usage_pattern:
        f.write("%s:%d,%x,%d\n" % (l[0], l[1], l[2], l[3]))
