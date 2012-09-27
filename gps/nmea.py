#
# Parse GPS NMEA Messages
#

import sys
# strip off heading time stamp characters created by SecureCRT
def nmea_strip_left(line):
    pos = line.find('$')
    return line[pos:] if pos > 0 else line

# get field in NMEA sentance start from 0
def get_field(line, index):
    arr_line = line.split(",")
    if index < len(arr_line):
        return arr_line[index]
    else:
        return ""    

def print_gpgsv(line):
    line = nmea_strip_left(line)
    if not line.startswith("$GPGSV"):
        return
    i = 4
    for m in range(1,5):
        for i in range(i, i+4):
            print get_field(line, i),
        print
        i += 1
    
    
def print_at_point(f, index):
    count = 0
    for line in f:
        line = nmea_strip_left(line)
        if line.startswith("$GPGGA"):
            count += 1

        if count == index:
            print line.strip()
            if line.startswith("$GPGSV"):
                print_gpgsv(line)

    
# get TTFF (Time To First Fix)
def fix_time(f):
    start = 0
    ttff_2d = 0
    ttff = 0
    for line in f:
        line = nmea_strip_left(line)
        #if line.find("gps_start") >= 0:
        #    print line
        if line.startswith("========="):
            start = 1
            #print line
            continue
        if start == 1:
            if line.startswith("$GPGSA"):
                ttff += 1
            if line.startswith("$GPGSA,A,2") and ttff_2d == 0:
                ttff_2d = ttff - 1
                print ttff - 1,            
            #if line.startswith("$GPGSA,A,2") or line.startswith("$GPGSA,A,3"):
            if line.startswith("$GPGSA,A,3"):
                print ttff - 1
                start = ttff = ttff_2d = 0
                continue

def time2str(t):
    return "%02d%02d%02d" % (t/3600, (t%3600)/60, t%60)    

def str2time(s):
    hh,mm,ss = map(int, (s[:2], s[2:4], s[4:6]))
    return hh*3600 + mm*60 + ss
    
# find place where fix is lost
def lost_fix(f):
    fixed, count, lost_time = 0, 0, 0
    time, prev_time = 0, 0
    previous = ""
    for line in f:
        line = nmea_strip_left(line)
        if line.startswith("======"):
            # ommit duplicated line
            if previous.startswith("======"): continue
            print line
            fixed, count, lost_time = 0, 0, 0

        if line.startswith("$GPGGA"):
            count += 1
            timestr = get_field(line, 1)[:6]
            time = str2time(timestr)
            if prev_time != 0 and abs(time - prev_time) > 2:
                print "time leap @", count,
                print time2str(prev_time), " -> ", time2str(time)
                print line
            prev_time = time
                
        if line.startswith("$GPGSA"):
            state = int(get_field(line, 2))
            if state < 1 or state > 3:
                print "error in nmea message"
                print line
            if state != fixed:
                if fixed == 0: #the fixed variable not initialized
                    fixed = state
                    continue
                if state == 1: #lost fix
                    lost_time = count
                    print "lostfix @", count
                elif (state == 2) or (state == 3):
                    print "fix   %dd  @ %d"%(state, count),
                    if lost_time > 0:
                        print "cost", count - lost_time
                    else:
                        print ""
                print previous, line
                fixed = state
        previous = line

##############################################################################
#    NEW IMPLEMENT
##############################################################################
from gpx import Gpx

class InvalidSentence(Exception):
    pass

Position = {}

# Fix Position Data
#$GPGGA,111440.673,3959.2102,N,11619.6722,E,1,08,1.6,92.4,M,-7.2,M,,0000*7F
#0      1          2         3 4          5 6 7  8   9   10 11  1213 14 
def gpgga(nmea, pos):
    if len(nmea) < 14:
        raise InvalidSentence("gpgga")
    time, latitude, longitude, elevation, geoid = \
        nmea[1], nmea[2], nmea[4], nmea[9], nmea[11]
    pos['time'] = time
    pos['lon']  = longitude
    pos['lat']  = latitude
    pos['ele']  = elevation
    pos['geoid']= geoid
    ns, we = nmea[3], nmea[5]
    if ns == 'S': pos['lon'] = '-'+longitude
    if we == 'W': pos['lat'] = '-'+latitude
        

# Satellite in Active
#$GPGSA,A,3,13,24,21,06,03,07,16,08,,,,,2.3,1.6,1.6*39
#0      1 2 3  4  5  6  7  8  9  10     15  16  17
def gpgsa(nmea, pos):
    if len(nmea) < 18:
        raise InvalidSentence("gpgsa")
    fix, satellites, (pdop, hdop, vdop) = \
          nmea[2], nmea[3:15], nmea[15:]
    satellites = map(int, filter(lambda(x): x, satellites))
    satellites.sort()
    pos['fix']  = fix
    pos['pdop'] = pdop
    pos['hdop'] = hdop
    pos['vdop'] = vdop
    pos['sat_active'] = satellites
#    print fix, satellites, pdop, hdop, vdop

# Satellite in View
#$GPGSV,3,1,12,03,76,056,29,19,71,199,15,06,60,054,34,07,41,313,38*77
#$GPGSV,3,2,12,13,40,245,21,16,32,073,30,25,30,077,,23,28,217,19*7F
#$GPGSV,3,3,12,24,26,067,30,21,09,039,33,08,06,314,30,01,02,086,08*74
#0      1 2 3  4         7  8         11 12        15 16        19        
def gpgsv(nmea, pos):
    (total_line, line_seq, total_sat) = map(int, nmea[1:4])
    if (total_line != line_seq):
        max_len  = 20
    else:
        max_len = 4 + (total_sat - (line_seq - 1)*4)*4
    if len(nmea) < max_len: raise InvalidSentence("gpgsv")
    sat = []
    for i in range(4,19,4):
        sat.append(nmea[i:i+4])
    #sat.sort()
    pos['sat_view'] = pos.get('sat_view', []) + sat
    '''
    for s in sat:
        print s
    '''

# Recommended Minimum Specific
#$GPRMC,111440.673,A,3959.2102,N,11619.6722,E,000.0,006.6,310510,,,A*63
def gprmc(nmea, pos):
    if len(nmea) < 13:
        raise InvalidSentence("gprmc")
    pass

# Course over Ground and Ground Speed
#$GPVTG,006.6,T,,M,000.0,N,000.0,K,A*0D
# 0     1     23 4 5     6 7     8 9
def gpvtg(nmea, pos):
    if len(nmea) < 10:
        raise InvalidSentence("gpvtg")
    course, speed_knots, speed_kmh = nmea[1], nmea[5], nmea[7]
    pos['course'] = course
    pos['speed']  = speed_knots
    try:
        speed = float(speed_kmh)
    except:
        print "err:", nmea
        speed = 0.0                
    if speed > 120.0:
        print speed
        print nmea

# Time and Date
#$GPZDA,111440.673,31,05,2010,00,00*51
#0      1          2  3  4    5  6
def gpzda(nmea, pos):
    if len(nmea) < 7:
        raise InvalidSentence("gpzda")
    time, day, month, year = nmea[1], nmea[2], nmea[3], nmea[4]
    pos['date'] = year + month + day
    
# process one NMEA block, 1 second burst of messages
Dispatch = {
    '$GPGGA' : gpgga,
    '$GPGSA' : gpgsa,
    '$GPGSV' : gpgsv,
    '$GPRMC' : gprmc,
    '$GPVTG' : gpvtg,
    '$GPZDA' : gpzda,
    }
def process_block(block):
    global Position
    pos = {}
    for line in block:
        #print line
        nmeastr, checksum = line.strip().split('*')
        nmea = nmeastr.split(',')
        handler = Dispatch.get(nmea[0], None)
        if handler:
            handler(nmea, pos)
    Position = pos
    return pos
    #print block
'''
def output(pos, func):
    out = []
    #try:
    fix = int(pos['fix'])
    if fix == 1: out.append('')
    elif fix == 2: out.append('2d')
    elif fix == 3: out.append('3d')
    else: out.append('error')
        
    out.append(pos['time'])
    out.append(str(len(pos['sat_active'])))
    out.append(pos['lon'])
    out.append(pos['lat'])
    #except Exception:
    #    pass
    out.append(pos['sat_active'])
    func(*out)
'''

def output(pos, func):
    print pos
    f = sys.stderr
    gpx.write_wpt(f, "aaa", pos)
    gpx.open_trk(f,"bb")
    gpx.write_trkpt(f,pos)
    gpx.close_trk(f)
    
def main(f):
    gpx = Gpx(f.name[:-4]+'.gpx')

    NO_FIX, FIX_2D, FIX_3D = 1, 2, 3
    points = []
    block = []
    count, fix, lost = 0, 0, 0
    accum = 0
    for line in f:
        line = strip_timestamp(line)
        if line.startswith("=====") and count > 0:
            accum += 1
            if accum > 2: # only if encounter 2 consequential '=====' lines
                print "%d sentence block(s), time duration %d:%d:%d" % (count, count/3600, (count%3600)/60, count%60)
                count, fix, lost = 0, 0, 0
                print line
        else:
            accum = 0
        if not line.startswith("$GP"):
            continue
        
        if line.startswith("$GPZDA"):
            block.append(line)
            count += 1
            #if (count > 200):
            #    break
            try:
                pos = process_block(block)
                #print pos['time'], len(pos.get('sat_view',[]))
                cur_fix = int(pos['fix'])
                lat,lon = pos['lat'], pos['lon']
            except (ValueError, KeyError, InvalidSentence) as e:
                print "\n***** Exception %s @ block %d *****"%(repr(e), count)
                for s in block: print s,
                print pos
                block = []
                pos = {}
                continue
            
            if cur_fix <= NO_FIX: # no fix
                if fix > NO_FIX:
                    print "[%s] lostfix %d " % (pos['time'][:6],count)
                    lost = count
                    pos['tag'] = 'lost'
                    points.append(pos)
            elif cur_fix > NO_FIX: # fixed
                if fix <= NO_FIX:
                    if lost > 0:
                        print "[%s] refix %d cost %d" % (pos['time'][:6],count, count - lost)
                        pos['cost'] = count-lost
                        pos['tag'] = 'fix'
                        points.append(pos)
                        gpx.open_trk("trk%d"%count)
                    else:
                        print "[%s] first fix %d " % (pos['time'][:6],count)
                        pos['cost'] = count
                        pos['tag'] = 'firstfix'
                        points.append(pos)
                        #gpx.write_wpt("firstfix(%d sec)[%s]"%(count,pos['time']),pos)
                        gpx.open_trk("trk%d"%count)
                gpx.write_trkpt(pos)
            fix = cur_fix
            block = []
        else:
            block.append(line)
    if count > 0:
        print "%d sentence block(s), time duration %d:%d:%d" % (count, count/3600, (count%3600)/60, count%60)
    '''                
    fix_time(f)
    f.seek(0)
    #gpvtg(f)
    #f.seek(0)
    lost_fix(f)
    '''
    for i,v in enumerate(points):
        t = v['time'][:6]
        if v['tag'] == 'fix':
            gpx.write_wpt("%d.[%s]fix(%d sec)"%(i,t,v['cost']), v)
        elif v['tag'] == 'lost':
            gpx.write_wpt("%d.[%s]lost"%(i,t), v)
        elif v['tag'] == 'firstfix':
            gpx.write_wpt("%d.[%s]firstfix(%d sec)"%(i,t,v['cost']),v)
        else:
            pass
    #gpx.close_gpx()
    f.close()
    gpx.close()

def for_file_in_dir(path, func, arg=0):
    import os
    print path
    for fname in os.listdir(path):
        if fname.endswith(".txt"):
            print fname
            print "=================="
            with open(os.path.join(path, fname), "r") as f:
                if arg:
                    func(f, arg)
                else:
                    func(f)
            print
        
if __name__ == "__main__":
    #path = r"C:\Documents and Settings\cpeng\Desktop\gps\Log\0706_Shenzhen"
    path = r"C:\Documents and Settings\cpeng\Desktop\gps\7700B0_gps_test_log"
    #main(os.path.join(path, "CM20_No_92_gps0705.log"))
    for_file_in_dir(path, lost_fix)
    for_file_in_dir(path, print_at_point, 180)
    #main()
    print "done."
