#
# Convert gps information in .gpx format and output to file
#

gpx_header="""<?xml version="1.0" encoding="UTF-8"?>
<gpx
  version="1.1"
  creator="NMEA Parser - Augustatek, Inc."
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns="http://www.topografix.com/GPX/1/0"
  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">
"""
gpx_end="</gpx>"

class Gpx(file):
    def __init__(self, name, mode="w"):
        file.__init__(self, name, mode)
        self._status = ""
        self._open_gpx()

    def close(self):
        self._close_gpx()
        file.close(self)
        
    def _conv_lat_lon(self, pos):
        lat = float(pos['lat'][:2]) + float(pos['lat'][2:])/60.0
        lon = float(pos['lon'][:3]) + float(pos['lon'][3:])/60.0
        return (lat,lon)

    def _conv_date_time(self, pos):
        date = pos['date']
        time = pos['time']
        dt = "%s-%s-%sT%s:%s:%sZ"%(date[:4],date[4:6],date[6:],time[:2],time[2:4],time[4:])
        return dt

    def _conv_fix(self, pos):
        fix = pos['fix']
        if fix == '3':
            return '3d'
        elif fix == '2':
            return '2d'
        else:
            return 'none'

    def _open_gpx(self):
        self.write(gpx_header)

    def _close_gpx(self):
        self._close_trk()
        self.write(gpx_end)
        
    def write_wpt(self, name, pos):
        self._close_trk()
        self.write('<wpt lat="%f" lon="%f">\n'%self._conv_lat_lon(pos))
        self.write('  <time>%s</time>\n'%self._conv_date_time(pos))
        self.write('  <name>%s</name>\n'%name)
        self.write('</wpt>\n')

    def open_trk(self, name):
        self._close_trk()
        self.write('<trk>\n')
        self.write('  <name>%s</name>\n'%name)
        self.write('  <trkseg>\n')
        self._status = "trk"

    def _close_trk(self):
        if (self._status == "trk"):
            self.write('  </trkseg>\n')
            self.write('</trk>\n')
            self._status = ""

    def write_trkpt(self, pos):
        self.write('  <trkpt lat="%f" lon="%f">\n'%self._conv_lat_lon(pos))
        self.write('    <ele>%s</ele>\n'%pos['ele'])
        self.write('    <time>%s</time>\n'%self._conv_date_time(pos))
        self.write('    <course>%s</course>\n'%pos['course'])
        self.write('    <speed>%s</speed>\n'%pos['speed'])
        self.write('    <fix>%s</fix>\n'%self._conv_fix(pos))
        self.write('    <sat>%d</sat>\n'%len(pos['sat_active']))
        self.write('    <hdop>%f</hdop>\n'%float(pos['hdop']))
        self.write('    <vdop>%f</vdop>\n'%float(pos['vdop']))
        self.write('    <pdop>%f</pdop>\n'%float(pos['pdop']))
        self.write('  </trkpt>\n')
        
