#!/bin/bash

/home/pi/homeware/hw-dbtojson.py

scp /home/pi/homeware/data/env_data.json stuart@zubin.tropic.org.uk:~/public_html/homeware/
