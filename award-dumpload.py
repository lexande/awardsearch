#!/usr/bin/env python

import sys
import datetime
import xmlrpclib

if len(sys.argv) < 2:
  sys.exit("Too few arguments")

s = xmlrpclib.ServerProxy('http://localhost:8000',use_datetime=True)

if sys.argv[1] == "dump":
  print s.cacheDump()
if sys.argv[1] == "load":
  indump = sys.stdin.read()
  s.cacheLoad(indump)
