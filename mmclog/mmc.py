import os
dd512=r"C:\Documents and Settings\cpeng\Desktop\dd4096_3.txt"

# convert 11-08.42.17.8771 to time only take MM:SS.mmmm parts
def convert_time(time_str):
    #print(time_str)
    arr=time_str.split(".")
    time = int(arr[1])
    time = time*60 + int(arr[2])
    time = time*10000 + int(arr[3])
    return time

def convert_time2(time_str):
    tstart = time_str.index('[')
    tend = time_str.index(']')
    tstr = time_str[tstart+1:tend]    
    return int(tstr)

issue = []
start =[]
done = []
    
with open(dd512, "r", encoding="utf8") as f:
    for line in f:
        #if "mmc0: starting CMD18" in line:
        if "cpeng: mmc_blk_issue_rw_rq" in line:    
            t = convert_time2(line)
            #print(t)
            issue.append(t)
            #print(line[:18])
        if "mmc0: starting CMD18" in line:
            t = convert_time2(line)
            start.append(t)
        if "mmc0: req done (CMD18)" in line:
            t = convert_time2(line)
            done.append(t)
            
print(len(issue), len(start), len(done))

print("issue    start    done    i-s s-d d-i i-i")
for x in range(len(issue)):
    print(issue[x], start[x], done[x], end=" ")
    i2s = start[x] - issue[x]
    s2d = done[x] - start[x]
    print(i2s, s2d, end=" ")
    if x > 0:
        d2i = issue[x] - done[x-1]
        i2i = issue[x] - issue[x-1]
        print(d2i, i2i)
    else:
        print()

'''
for x in range(len(start) - 1):
    diff = start[x+1] - start[x]
    print(diff)
'''               
               