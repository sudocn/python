import sys

# strip off heading time stamp characters created by SecureCRT
def strip_timestamp(line):
    pos = line.find('$')
    return line[pos:] if pos > 0 else line

def gpgga_time(line):
    try:
        t = int(line[7:13])
    except ValueError:
        t = 0
    return t

'''    
files = [\
    (r"GPS_cayman32_0609_1635.log", r"GPS32"),\
    (r"gps-6-9-2010-2-cayman20-54.log", r"GPS20"),\
    (r"20100609_124841_2_phone22_2.log", r"GPS22"),\
    (r"20100609_162744_#34_2.log", r"GPS34")\
    ]

files = [\
    (r"gps0622_Cayman27(1.1).log", r"GPS27(1.1)"),\
    (r"gps0622_Cayman60.log", r"GPS60"),\
    (r"gps0622_Cayman32.log", r"GPS32"),\
    ]
files = [\
    (r"gps0623_cayman2B.log", r"GPS2B"),\
    (r"gps0623_cayman94.log", r"GPS94"),\
    ]
'''
files = [\
    (r"CM20_No3_gps0622_Fail.log", r"GPS3"),\
    (r"CM20_No92_gps0622_Fail.log", r"GPS92"),\
    (r"CM20_No86_gps0622_OK.log", r"GPS86"),\
    ]

#time_range = [(103630,103900), (104045,104500)]
#time_range = [(85620,85800)]
#time_range = [(34955,35430)]
time_range = [(64010,64300)]
#path  = r"C:\Documents and Settings\cpeng\Desktop\gps\Log\0609_RoadTest\\"
#path  = r"C:\Documents and Settings\cpeng\Desktop\gps\Log\0622_RoadTest\\"
#path = r"C:\Documents and Settings\cpeng\Desktop\gps\Log\0623_Shenzhen\\"
path = r"C:\Documents and Settings\cpeng\Desktop\gps\Log\0622_Taiwan\\"

import os
def main(inf, outf):
    #oname = r"GPS32"
    
    fin = open(path+inf)
    for i in range(len(time_range)):
        oname = "%s_site%d.txt"%(outf, i+1)
        fout = open(path+oname, "w")
        start, end = time_range[i]
        lost = strip_section(fin,fout,start,end)
        fout.close()
        print "lost", lost
        print "rename file %s to %s_lost%ds.txt"%(oname, oname[:-4],lost)
        os.chdir(path)
        os.rename(oname, "%s_lost%ds.txt"%(oname[:-4],lost))
    fin.close()
        
def strip_section(fin, fout, start, end):
    output = 0
    lost = 0
    for line in fin:
        line = strip_timestamp(line)
        if not line.startswith("$GP"):
            continue
        if line.startswith("$GPGGA,"):
            time = gpgga_time(line)
            if time >= start and time < end:
                if time == start: print "section start", time
                output = 1
            if time >= end:
                if output:
                    output = 0
                    print "section end", time
                    break
        if output:
            fout.write(line)
            if line.startswith("$GPGSA,A,1"): lost += 1
    return lost

if __name__ == "__main__":
    for iname, oname in files:
        print iname, oname    
        main(iname, oname)
    print "done."
                
                
            
            
    
