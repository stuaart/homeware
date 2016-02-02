#!/bin/bash

HOMEWARE=/home/pi/homeware/
python $HOMEWARE/hw-latesttojson.py

scp $HOMEWARE/data/latest-state.json stuart@zubin.tropic.org.uk:~/public_html/homeware/

