f = open("NMEA.txt")
gf = open("GGA.txt", "w")
for line in f:
    if line.startswith("$GPGGA"):
        gf.write(line)


f.close()
