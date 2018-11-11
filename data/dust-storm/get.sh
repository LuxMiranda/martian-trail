#!/bin/bash


for day in {186..350}
do
  urlBase="http://www-mars.lmd.jussieu.fr/mcd_python/cgi-bin/"
  request="mcdcgi.py?datekeyhtml=1&ls=$day&localtime=all&year=2018&month=11&day=10&hours=1&minutes=3&seconds=15&julian=2458432.543923611&martianyear=34&martianmonth=10&sol=539&latitude=-6.084&longitude=239.061&altitude=1&zkey=3&isfixedlt=off&dust=5&hrkey=1&zonmean=off&var1=swdown&var2=rho&var3=wind&var4=none&dpi=80&islog=off&colorm=jet&minval=&maxval=&proj=cyl&plat=&plon=&trans=&iswind=off&latpoint=&lonpoint="

  filename=$(wget -q "$urlBase$request" -O - | grep "href" | cut -d "'" -f2)

  echo "Fetching data for Mars Ls $day..."
  wget "$urlBase$filename" -O $day.txt 2> /dev/null
  sleep 0.1
done
