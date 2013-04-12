#!/usr/bin/env python

import re
import sys
import math
import datetime
import xmlrpclib

staralliance = ["A3","AC","BD","CA","CO","ET","JJ","JK","JP","KF","LH","LO","LX","MS","NH",
                "NZ","OS","OU","OZ","PZ","SA","SK","SN","SQ","TG","TK","TP","UA","US"]

# The following two functions are not used, but may be later for MPM calculation etc
def getlatlong(code):
  airports = open("arm/airports.dat")
  for line in airports.readlines(): 
    splitline = re.split(r"\t",line)
    if splitline[0] == code:
      airports.close()
      return [float(splitline[1]),float(splitline[2])]

def gcdist(origstring,deststring):
  orig = getlatlong(origstring)
  dest = getlatlong(deststring)
  lat1 = orig[0]*math.pi/180
  lat2 = dest[0]*math.pi/180
  longdiff = abs(orig[1]-dest[1])*math.pi/180
  return 3958.8 * math.acos(math.sin(lat1)*math.sin(lat2) +
                            math.cos(lat1)*math.cos(lat2)*math.cos(longdiff))

def getdests(code):
  dests = []
  routes = open("arm/routes.dat")
  for line in routes.readlines():
    if re.match(r"#",line):
      continue
    splitline = re.split(r"\t",line)
    if splitline[1] == code:
      if splitline[0] in staralliance:
        if splitline[2] not in dests:
          dests.append(splitline[2])
  routes.close()
  return dests

def printflights(list):
  for flight in list:
    print flight[0],"\tdep",flight[1].strftime("%F %H:%M"),"arr",flight[2].strftime("%F %H:%M")

def checkavail(depdate,orig,dest,fjy):
  return s.checkAvail(depdate.strftime("%Y-%m-%d"),orig,dest,fjy)

if len(sys.argv) < 4:
  sys.exit("Too few arguments")  
elif len(sys.argv) < 5:
  fjy = "Y"
else:
  fjy = sys.argv[4]

if len(sys.argv) > 5 and sys.argv[5] == 'nonstop':
  nonstop = True
else:
  nonstop = False

orig = sys.argv[1]
dest = sys.argv[2]

datearg=re.split('-',sys.argv[3])
depdate=datetime.datetime(int(datearg[0]),int(datearg[1]),int(datearg[2]))

s = xmlrpclib.ServerProxy('http://localhost:8000',use_datetime=True)

nonstops = checkavail(depdate,orig,dest,fjy)
if nonstops:
  print "Nonstops:"
  printflights(nonstops)


if not (nonstop):
  onestops = []
  for xfer in getdests(orig):
    if xfer not in getdests(dest):
      continue
    firstlegs = checkavail(depdate,orig,xfer,fjy)
    if not firstlegs:
      continue
    secondlegs = checkavail(depdate,xfer,dest,fjy) + checkavail(depdate + datetime.timedelta(1),xfer,dest,fjy) + checkavail(depdate + datetime.timedelta(2),xfer,dest,fjy)
    for firstleg in firstlegs:
      for secondleg in secondlegs:
        if firstleg[2] < secondleg[1] and secondleg[1] - firstleg[2] < datetime.timedelta(1):
           onestops.append((xfer,[firstleg,secondleg]))

  if onestops:
    i = 1
    for onestop in onestops:
      print "Onestop", i, "via",onestop[0]
      printflights(onestop[1])
      i = i+1
