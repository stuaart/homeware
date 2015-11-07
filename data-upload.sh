#!/bin/bash

HOMEWARE=/home/pi/homeware/
python $HOMEWARE/hw-dbtojson.py
python $HOMEWARE/hw-dbtocsv.py

scp $HOMEWARE/data/*.{json,csv} stuart@zubin.tropic.org.uk:~/public_html/homeware/

