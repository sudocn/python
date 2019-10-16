
class Flow(object):

	def __init__(self):
		self.req = [ "1", "2", "3", "4", "5" ]
		self.req.remove("2")

	def p(self):
		print self.req


print "1"
f1 = Flow()
f1.p()
print "2"
f2 = Flow()
f2.p()
print "3"
