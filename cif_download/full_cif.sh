#!/bin/bash

set -u

cd $CIF_FOLDER
rm -rf *
URL='https://publicdatafeeds.networkrail.co.uk/ntrod/CifFileAuthenticate'

function get_ref {
  echo $(head -n 1 $1 | awk '{print $1}' | cut -d. -f3)
}

function get_date {
  echo $(head -n 1 $1 | awk '{print $1}' | grep -Eo 'PD[0-9]{6}' | sed 's/PD//')
}

# Download the latest FULL CIF & un-gzip
FILE="CIF_ALL_FULL_DAILY.CIF"
curl -L -u $NROD_USER:$NROD_PASS -o $FILE.gz "$URL?type=CIF_ALL_FULL_DAILY&day=toc-full.CIF.gz"

if gzip -t $FILE.gz; then
  gzip -d $FILE.gz
else
  rm $FILE.gz
  exit 1
fi

# Get the file reference
REF=$(get_ref $FILE)

# Get the file date
FULL_DATE=$(get_date $FILE)

# Rename the full CIF and adjust the file date
mv $FILE "$REF.CIF"
touch "$REF.CIF" -d $FULL_DATE

DAYS=("sat" "sun" "mon" "tue" "wed" "thu")
for DAY in ${DAYS[@]}; do
  FILE="toc-update-$DAY"
  curl -L -u $NROD_USER:$NROD_PASS -o $FILE.gz "$URL?type=CIF_ALL_UPDATE_DAILY&day=$FILE.CIF.gz"
  
  if gzip -t $FILE.gz; then
    gzip -d $FILE.gz
  else
    rm $FILE.gz
    continue
  fi

  # Get the file reference
  REF=$(get_ref $FILE)

  # Get the file date
  DATE=$(get_date $FILE)

  # Compare dates
  FULL_CIF_DATE=$(date -d $FULL_DATE +"%Y%m%d")
  UPDATE=$(date -d $DATE +"%Y%m%d")
  if [ $FULL_CIF_DATE -ge $UPDATE ];
  then
    rm $FILE
  else
    mv $FILE "$REF.CIF"
    touch "$REF.CIF" -d $DATE
  fi

done
