#!/usr/bin/python

from datetime import datetime
from datetime import timedelta

import pdb
pdb.set_trace()

start = datetime(2016,6,1,13,0,0)
onehour = timedelta(hours=1)

while start < datetime(2016,6,30,23,0,0):
    end = start + onehour
    print start.strftime("%Y%m%d%H")+ "-"+ end.strftime("%Y%m%d%H")
    start = end
    
