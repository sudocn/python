#
# Convert Skytraq's AGPS data (Eph.dat) to C binary array format
#

import os

eph_name = r"C:\Documents and Settings\cpeng\Desktop\gps\eph.dat"
base,ext = os.path.splitext(eph_name)
c_name = base + ".c"

af = open(eph_name, "rb")
ba = bytearray(af.read())
af.close()

af = open(c_name, "w")

print >>af, "static unsigned char _aiding[] = {"
for i in range(0, len(ba)) :
    print >>af, "0x%02x,"%ba[i],
    if i % 16 == 15: print >>af

print >>af, "};"
print >>af, "unsigned char *aiding = _aiding;
af.close()
