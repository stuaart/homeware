#!/bin/bash

HOMEWARE=./
python $HOMEWARE/hw-dbtojson.py
python $HOMEWARE/hw-dbtocsv.py

scp $HOMEWARE/data/*.{json,csv,db} stuart@zubin.tropic.org.uk:~/public_html/homeware/

