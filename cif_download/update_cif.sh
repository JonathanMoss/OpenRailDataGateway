#!/bin/bash

set -u

cd $CIF_FOLDER
URL='https://datafeeds.networkrail.co.uk/ntrod/CifFileAuthenticate'

function get_ref {
  echo $(head -n 1 $1 | awk '{print $1}' | cut -d. -f3)
}

function get_date {
  echo $(head -n 1 $1 | awk '{print $1}' | grep -Eo 'PD[0-9]{6}' | sed 's/PD//')
}

function full_cif_date {
  echo $(find $CIF_FOLDER/*.CIF -type f -printf '%T+ %p\n' | sort | head -n 1 | grep -Eo "[0-9]{4}-[0-9]{2}-[0-9]{2}")
}

function file_count {
  echo $(ls $CIF_FOLDER | wc -l)
}

# Check to make sure there are files in the directory
if [ $(file_count) = 0 ];
then
  echo "No FULL CIF can be found, closing..."
  exit 1
fi

# Get the Full CIF date
FULL_DATE=$(full_cif_date)

# Download the updates
DAYS=("sat" "sun" "mon" "tue" "wed" "thu" "fri")

for DAY in ${DAYS[@]}; do
  FILE="toc-update-$DAY"
  curl -L -u $NROD_USER:$NROD_PASS -o $FILE.gz "$URL?type=CIF_ALL_UPDATE_DAILY&day=$FILE.CIF.gz"
  gzip -d $FILE.gz

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
