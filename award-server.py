#!/usr/bin/env python

import mechanize
import re
import sys
from bs4 import BeautifulSoup
import datetime
from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
import pickle
import copy

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

def readConf():
  conf = open("awardsearch.conf")
  accountnum = re.match("Account number: (.*)\n",conf.readline()).group(1)
  password = re.match("Password: (.*)\n",conf.readline()).group(1)
  return (accountnum, password)

def datetimeFromContents(indate,tdcontents,weekday):
  intime = datetime.datetime.strptime(tdcontents[0],"%H:%M").time()
  indt = datetime.datetime.combine(indate,intime) + datetime.timedelta(weekday)
  if len(tdcontents) > 1:
    if tdcontents[2] == '+1':
      indt = indt+datetime.timedelta(1)
    elif tdcontents[2] == '+2':
      indt = indt+datetime.timedelta(2)
  return indt

def flightLookup(depdate,orig,dest,fcy):
  results = [[],[],[],[],[],[],[]]
  print "Looking up" , orig , "to", dest, "the week of", depdate.strftime("%F")
  rtndate = rtndate=depdate+datetime.timedelta(7)
  br.open("https://aswbe-i.ana.co.jp/p_per/sky_ip_per_jp/preAwdSearchLogin.do?LANG=en")
  br.select_form("awdSelectAwardMethodForm")
  br.submit(name='buttons.starTicketButton', label="Use Star Alliance Member Airlines" )
  br.select_form("awdSearchRoundtripInputForm")
  br.submit(name="buttons.search7DayButton", label="7-Day Availability (direct flights only)")
  br.select_form("awdSearch7DayInputForm")
  br["departureAirportCD"] = orig
  br["arrivalAirportCD"] = dest
  br["leaveMonth"] = [str(depdate.month)]
  br["leaveDay"] = [str(depdate.day)]
  br["returnMonth"] = [str(rtndate.month)]
  br["returnDay"] = [str(rtndate.day)]
  br["seatClassArea"] = [fcy]
  response = br.submit(name='buttons.nextButton', label="Next")
  html = response.read()
  if re.search(r"Aircraft Type",html):
    soup = BeautifulSoup(html)
    rows = soup.find_all('tr')
    for row in rows:
      if (len(row.contents) < 2):
        continue
      if re.search(r"absmiddle",str(row)):
        continue
      tds = row.find_all('td')
      if re.search(r"Return:",str(tds)):
        break
      elif (len(tds) > 16):
        continue
      elif (len(tds) < 14):
        continue
      else:
        for weekday in range(0,7):
          if len(tds[weekday-7].contents) < 2:
            results[weekday] = "gray"
          elif not tds[weekday-7].contents[1].get('alt'):
            results[weekday] = "gray"
          if results[weekday] == "gray":
            continue
          if tds[weekday-7].contents[1].get('alt') == 'Available':
            results[weekday].append((re.sub(r"\r\n.* (.*)\r\n",r"\1",tds[0].contents[2]),
                     datetimeFromContents(depdate,tds[-10].contents,weekday),
                     datetimeFromContents(depdate,tds[-9].contents,weekday)))
  return results

def checkAvail(datestring,orig,dest,fcy):
  depdate = datetime.datetime.strptime(datestring,"%Y-%m-%d")
  if (depdate,orig,dest,fcy) not in resultsCache:
    lookupresults = flightLookup(depdate,orig,dest,fcy)
    for weekday in range(0,7):
      if lookupresults[weekday] == "gray":
        continue
      else:
        resultsCache[(depdate+datetime.timedelta(weekday),orig,dest,fcy)] = lookupresults[weekday]
  return resultsCache[(depdate,orig,dest,fcy)]

def cacheDump():
  return pickle.dumps(resultsCache)

def cacheLoad(indump):
  inload = pickle.loads(indump)
  for key in inload.keys():
    resultsCache[key] = inload[key]
  return 0

resultsCache = {}

br = mechanize.Browser()
br.set_handle_robots(False)   # no robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Lynx/2.8.7pre.5 libwww-FM/2.14 SSL-MM/1.4.1')]
br.open("https://aswbe-i.ana.co.jp/p_per/sky_ip_per_jp/preAwdSearchLogin.do?LANG=en")
br.select_form("loginForm")
conf = readConf()
br["cardNo"] = conf[0]
br["password"] = conf[1]
br.submit()

server = SimpleXMLRPCServer(("localhost", 8000))
server.register_function(checkAvail,"checkAvail")
server.register_function(cacheDump,"cacheDump")
server.register_function(cacheLoad,"cacheLoad")

print "Serving..."
server.serve_forever()
