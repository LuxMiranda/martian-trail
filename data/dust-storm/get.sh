#!/bin/bash

sol=371
while read LS ; do
  sol=$((sol+1))
  rounded=$(printf '%.2f' $LS)
  echo "Fetching data for Mars Sol $sol (Ls $rounded°)"
  urlBase="http://www-mars.lmd.jussieu.fr/mcd_python/cgi-bin/"
  request="mcdcgi.py?datekeyhtml=1&ls=$LS&localtime=all&year=2018&month=11&day=11&hours=22&minutes=46&seconds=38&julian=2458434.4490509257&martianyear=34&martianmonth=10&sol=541&latitude=-6.084&longitude=240.349&altitude=1&zkey=3&isfixedlt=off&dust=5&hrkey=1&zonmean=off&var1=swdown&var2=rho&var3=wind&var4=none&dpi=80&islog=off&colorm=jet&minval=&maxval=&proj=cyl&plat=&plon=&trans=&iswind=off&latpoint=&lonpoint="

  datafile=$(wget -q "$urlBase$request" -O - | grep "href" | cut -d "'" -f2)

  filename=$(printf '%0*d' 3 $sol)
  wget_output=$(wget "$urlBase$datafile" -O $filename.txt 2>/dev/null)

  while [ $? -ne 0 ]; do
    echo "Failed. Retrying..."
    wget_output_again=$(wget "$urlBase$datafile" -O $filename.txt 2>/dev/null)
  done

  echo "Done. Saved to $filename.txt"
  sleep 0.1
done < ../sols.txt
