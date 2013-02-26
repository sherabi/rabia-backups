#!/usr/bin/python
#run_backup_daily.py is released under the General Public License.
#Copyright (C) 2010-2012 Shezaan Topiwala
#This file is part of "Rabia Backups".

#run_backup_daily.py is free software: you can redistribute it and or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#run_backup_daily.py is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with run_backup_daily.py.  If not, see <http://www.gnu.org/licenses/>.

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
cmd = "python " + BACKUP_DAILY + " -t " + BACKUP_TARGET + " -c " + BACKUP_CONFIG_DAILY + " -l " +  BACKUP_LOG_DAILY + " -u " +  BACKUP_USER
print cmd
output = open(BACKUP_LOG_DAILY, 'w+')
subprocess.Popen(cmd, shell=True, stdout=output)
#subprocess.Popen(cmd, shell=True, stdout=out, stderr=out)
output.close()
config.close()
config_daily.close()
