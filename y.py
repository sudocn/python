
def line(filename):
	f = open(filename)
	for l in f:
		yield l

	f.close()

for l in line("list.txt"):
	print l
