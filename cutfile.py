
fname = r"C:\Documents and Settings\cpeng\My Documents\Log\0721.log"

f = open(fname, "rb")
fout = open(r"C:\wifi.log", "w")
output = 0
count = 0
for line in f:
    count += 1
    if output:
        pass
        print >>fout, line.rstrip()
    else:
        if line.startswith("[0721-23-50-00]"):
            output = 1
            print line

print count, output, line
f.close()
fout.close()
