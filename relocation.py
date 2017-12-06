#!/usr/bin/python

def relocate(fname):
	got = []
	with open(fname, "r") as f:
		for l in f:
			arr = l.split()
			r_type = arr[1]
			r_addr = arr[2]
			r_value = arr[4]
			r_sym_name = ''
			if r_type in ["JMP_SLOT", "GLOB_DAT", "ABS"]:
				r_sym_name = arr[5]

			got.append([int(r_addr,16), int(r_value, 16), r_type, r_sym_name])
	return sorted(got)

def jni_address(libname, logname):
	with open(logname, "r") as f:
		log = [x for x in f if libname in x]

	base = entry = 0
	for l in log:
		if "SEARCH JNI_OnLoad in " in l:
			pos = l.find("@")
			base = int(l[pos + 1: pos+11], 16)
		if "Calling JNI_OnLoad@" in l:
			pos = l.find("@")
			entry = int(l[pos + 1: pos+11], 16)
	
	if base == 0 or entry == 0:
		return 0,0
	else:
		return base,(entry - base)

if __name__ == '__main__':
	got = relocate("libcmcc_rusteze.relo")
	base = 0x89d43000
	for g in got:
		print "%x %x %s %s" % (g[0] - base, g[1], g[2], g[3])

	b,e = jni_address("libaspirecommon.so", "JNI_OnLoad.log")
	print "%x %x" % (b,e)