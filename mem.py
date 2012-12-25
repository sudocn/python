
file = r'c:\Documents and Settings\cpeng\Desktop\mem.txt'

total = 0
with open(file) as f:
    for line in f:
        fields = line.split()
        if len(fields) < 6:
            continue
        if fields[2] == '10':
            size = int(fields[4][2:], 16)
            print(line, hex(size))
            total += size

print("total: ", hex(total))
