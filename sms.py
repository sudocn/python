#!/opt/local/bin/python

aa=[66, 78, 50, 91, 98, 98, 71, 71, 108, 68, 120, 71, 51, 71, 69, 70, 123, 98, 108, 76, 101, 122, 98, 118, 119, 108, 95, \
	122, 98, 98, 70, 71, 68, 89, 62, 76, 84, 98, 98, 44, 108, 115, 56, 113, 83, 64, 51, 122, 108, 102, 100, 100, 85, 114, \
	59, 44, 103, 81, 98, 117, 55, 98, 50, 77, 79, 98, 122, 70, 72, 72, 98, 98, 70, 98, 63, 122, 98, 38, 48, 98, 98, 98, 80, \
	79, 65, 112, 54, 107, 40, 83, 81, 106, 52, 85, 85, 41, 90, 77, 69, 109, 41, 113, 116, 47, 106, 43, 82, 98, 105, 72, 61]

sms = ""
for c in aa:
	sms += chr(c)

print sms
