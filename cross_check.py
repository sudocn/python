
def process(block):
    global fo
    found = False
#    print block[0]
    if block[0].find("  .text  ") == -1:
        return False
    for l in block:
        if l.find("*../sti_gps_lib.a") >= 0:
            found = False
            break
        elif l.find("sti_gps_lib.a") >= 0:
            found = True        
    if found:
        print block[0]
        for l in block: fo.write(l)
    return found
            
def isheader(l):
    if l.find("MetaWare ") >= 0:
        return True
    if l.startswith("(c) Copyright"):
        return True
    if l.startswith("Fri Dec 12"):
        return True
    return False

f = open("cross.txt")
fo = open("used.txt", "w+")
count = 0
block =[]
for line in f:
    if isheader(line):
        continue
    if len(line.strip()) == 0:
        continue
    if line[0] != ' ':
        if len(block) > 0:
            result = process(block)
            if result: count += 1
            block = []
    block.append(line)

f.close()
fo.close()        
    
    
