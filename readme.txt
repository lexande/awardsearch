Programs for searching for frequent flyer award availability on Star Alliance airlines, by scraping ANA's web interface

Your ANA username and password must be specified in awardsearch.conf, and you must have ANA miles in your account for searching to work.

USAGE:
To start the server process:
./award-server.py
(pipe to /dev/null or leave in a terminal so you can see progress)

To make searches:
./award-client.py origin destination yyyy-mm-dd class
(origin and destination are IATA codes; class is Y, C or F)
./award-client.py origin destination yyyy-mm-dd class nonstop
(to search for only nonstop flights)

To dump and load the server's results cache:
./award-dumpload.py dump > cachedump
./award-dumpload.py load < cachedump

Data in directory arm/ is from http://arm.64hosts.com/ (copyright flyertalk user cockpitvisit)
Awardsearch scripts GPL by Alexander Rapp (alexander@alexander.co.tz)
