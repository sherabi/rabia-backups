#!/usr/bin/python
import os
import subprocess
from bkenv import *

if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR)
if not os.path.exists(BACKUP_TARGET):
	os.makedirs(BACKUP_TARGET)

config = open(BACKUP_CONFIG, 'r')
config_daily = open(BACKUP_CONFIG_DAILY, 'w+')
for line in config:
	line = line.rstrip()
	if line != '': # Ignore newlines or empty lines
		if not line.startswith("#"): #Ignore comments
			field = line.split(':')
			LOCATION = field[0]
			SERVER = field[1]
			INCLUDES = field[2]
			EXCLUDES = field[3]
			RETENTION = field[4]
			TARGET = field[5]
			USER = field[6]
			INTERVAL = field[7]
			MAIL_LIST = field[8]

			config_daily.write(LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST+"\n")

#This is the main command to run
cmd = "python "+ BACKUP_DAILY + " -t " + BACKUP_TARGET + " -c " + BACKUP_CONFIG_DAILY + " -l " +  BACKUP_LOG_DAILY + " -u " +  BACKUP_USER
print cmd
out = open(BACKUP_LOG_DAILY, 'w+')
#err = open('', 'w+')
subprocess.Popen(cmd, shell=True, stdout=out)
#subprocess.Popen(cmd, shell=True)
out.close()
#err.close()

config.close()
config_daily.close()
