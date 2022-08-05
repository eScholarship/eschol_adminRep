#! /bin/bash

set -o pipefail
set -o errtrace
set -o nounset
set -o errexit


DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR

### Log file
NOW="$(date +"%d-%b-%Y")"
echo $NOW

#LOG_NAME=./logs/fix_$NOW.log

#. ../p3/bin/activate
#python FixSplash.py &> $LOG_NAME
#/apps/eschol/erep/xtf/control/tasks/s3copy.py --force  qt0024f03m
input="idsToFix.txt"
while IFS= read -r line
do
   echo "$line"
   erepredo convert $line
   # /apps/eschol/erep/xtf/control/tasks/syncOut.py  $line  
done < "$input"


