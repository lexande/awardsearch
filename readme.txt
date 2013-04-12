Programs for searching for frequent flyer award availability on Star Alliance airlines, by scraping ANA's web interface

Your ANA username and password should be set near the top of award-server.py

Usage:
./award-server.py
(pipe to /dev/null or leave in a terminal so you can see progress)

./award-client.py origin destination yyyy-mm-dd class
(origin and destination are IATA codes; class is Y, C or F)
./award-client.py origin destination yyyy-mm-dd class nonstop
(to search for only nonstop flights)

./award-dumpload.py dump > cachedump
./award-dumpload.py load < cachedump
(to dump and load results cache)

Data in directory arm/ is from http://arm.64hosts.com/ (copyright flyertalk user cockpitvisit)
Awardsearch scripts GPL by Alexander Rapp (alexander@alexander.co.tz)
