#!/usr/bin/env python

import subprocess
import datetime
import time
from os.path import expanduser
home = expanduser("~")

today=datetime.date.today()

host = "www.google.com"

SLEEPTIME=15
count = 0
f=open("/Users/james/bin/ping/pingtimes-%s.log" % today, "a")
while count < 3:
    dt= datetime.datetime.now()
    ping = subprocess.Popen(
                ["ping", "-c", "1", host],
                    stdout = subprocess.PIPE,
                        stderr = subprocess.PIPE
                        )
    try:
        out, error = ping.communicate()
        lines=out.split("\n")
        data=lines[1].split(" ")
        key,val= data[6].split("=")
        f.write("%s,%s\n" % (dt,val))
    except:
        # write out to standard file
        f.write("%s,%s\n" % (dt,-1))
        exf=open("/Users/james/bin/ping/errors/error-%s.log" % dt, "a")
        exf.write(out)
        exf.write("\n\n")
        exf.write(error)
        exf.close
    count+=1
    time.sleep(SLEEPTIME)

f.close()
