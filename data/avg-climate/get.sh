#!/bin/bash

sol=634
while read LS ; do
  sol=$((sol+1))
  rounded=$(printf '%.2f' $LS)
  echo "Fetching data for Mars Sol $sol (Ls $rounded°)"
  urlBase="http://www-mars.lmd.jussieu.fr/mcd_python/cgi-bin/"
  request="mcdcgi.py?datekeyhtml=1&ls=$LS&localtime=all&year=2018&month=11&day=10&hours=6&minutes=24&seconds=25&julian=2458432.7669560183&martianyear=34&martianmonth=10&sol=539&latitude=-6.084&longitude=240.349&altitude=1&zkey=3&isfixedlt=off&dust=1&hrkey=1&zonmean=off&var1=swdown&var2=rho&var3=wind&var4=none&dpi=80&islog=off&colorm=jet&minval=&maxval=&proj=cyl&plat=&plon=&trans=&iswind=off&latpoint=&lonpoint="

  datafile=$(wget -q "$urlBase$request" -O - | grep "href" | cut -d "'" -f2)

  filename=$(printf '%0*d' 3 $sol)
  wget "$urlBase$datafile" -O $filename.txt 2> /dev/null
  echo "Done. Saved to $filename.txt"
  sleep 0.1
done < ../sols.txt
