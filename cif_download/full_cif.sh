#!/bin/bash

# This script should be run as a cron job at 00:30 on 2nd of each month

day=$( date +%d )
cd ~/cif
rm -rf *
FILE="$day.CIF_ALL_FULL_DAILY.CIF"
curl -L -u $NROD_USER:$NROD_PASS -o $FILE.gz 'https://datafeeds.networkrail.co.uk/ntrod/CifFileAuthenticate?type=CIF_ALL_FULL_DAILY&day=toc-full.CIF.gz'
gzip -d $FILE.gz
HEADER=$(head $FILE -n 1)
HD_DATE=${HEADER:22:6}
touch $FILE -d $HD_DATE
