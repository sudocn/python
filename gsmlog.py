import traceback, sys

def valid_line(l):
    if l.startswith("Rx CH_") or l.startswith("Tx CH_"):
        return 1
    return 0

def err_msg(err_string):
    print err_string
    g_error.append(err_string)
    
# form wireshark/wiretap/dct3trace.c
# 128: SDCCH
# 112: SACCH
# 176: FACCH
#  96: CCCH
#  97: RACH
#  98: AGCH
#  99: PCH
#  80: BCCH
def parse_logical_ch(ch_name):
    if ch_name.startswith("CH_BCCH"):
        return 80
    elif ch_name.startswith("CH_CCCH"):
        return 96
    elif ch_name.startswith("CH_RACH"):
        return 97
    elif ch_name.startswith("CH_PCH"):
        return 99
    elif ch_name.startswith("CH_AGCH"):
        return 98
    elif ch_name.startswith("CH_FACCH"):
        return 176    
    elif ch_name.startswith("CH_SACCH"):
        return 112    
    elif ch_name.startswith("CH_SDCCH"):
        return 128    
    elif ch_name.startswith("CH_TCH"):
        return 192   
    elif ch_name.startswith("CH_PDTCH"):
        return 1   
    elif ch_name.startswith("CH_PACCH"):
        return 2   
    elif ch_name.startswith("CH_PTCCH"):
        return 4   
    else:
        print "unknown channel type: ", ch_name
        return 0
    
def write_line(out, direction, log_ch, phy_ch, fn, error, data):
    out.append('<l1 direction="%s" logicalchannel="%d" physicalchannel="%d" sequence="%s" error="%d" timeshift="0" bsic="0" data="%s" >' \
    % (direction, log_ch, phy_ch, fn, error, data))
    out.append('</l1>')
    return
        
        
#Tx CH_FACCH_F 211024:01 03 01 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B 2B
def convert_line(out, l):
    log_ch = 0
    phy_ch = 20
    fn = 0
    error = 0
    if l[0] == "T":
        direction = "up"
    else:
        direction = "down"
    
    colon = l.find(":")
    if colon < 0:
        error = 1
        write_line(out, direction, log_ch, phy_ch, fn, error, "")
        err_msg("[%d] Error: Incomplete message :%s" % ( g_count, l))
        return
    else:
        header = l[:colon]
        data = l[colon+1:]

    # left half part
    try:
        spline = header.split(" ");
        log_ch = parse_logical_ch(spline[1])
        fn = spline[2]
    except IndexError, e:
        err_msg("[%d] Error: Incomplete message :%s" % ( g_count, l))
        data = ""
        print e

    # right half part
    data = data.replace(' ', '').strip()
    if len(data) != 46:
        error = 1
        err_msg("[%d] Warnning: Data length != 23 :%s" % (g_count, l))
        if len(data) > 46:
            data = data[:46]

    write_line(out, direction, log_ch, phy_ch, fn, error, data)


######################################################################    
# Main comes here
######################################################################    

g_out = []
g_error = []
g_count = 0
def main():
    global g_out, g_count, g_error
    if len(sys.argv) > 1:
        input_fname = sys.argv[1]
    else:
        #input_fname = '20091117_nas_2.txt'
        input_fname = 'debug_trx_facch_10_28_12_54_a1.log'
    output_fname = input_fname[:input_fname.rindex('.')] + '.xml'
    error_fname = input_fname[:input_fname.rindex('.')] + '.err'
    
    f = open(input_fname, 'r')
    for line in f:
        try:
            if valid_line(line):
                g_count += 1
                convert_line(g_out, line);
                #break
        except Exception, e:
            traceback.print_exc()
            #traceback.print_exception()
            break
    f.close()

    # output xml file
    print output_fname
    with open(output_fname, 'w') as fout:
        fout.write('<?xml version="1.0"?>\n')
        fout.write('<dump>\n')
        for line in g_out:
            fout.write(line + '\n')
        fout.write('</dump>\n')

    # output error message
    if len(g_error) > 0:
        print error_fname
        with open(error_fname, "w") as fout:
            fout.writelines(g_error)    
    

if __name__ == "__main__":
    main()
    print "done."
