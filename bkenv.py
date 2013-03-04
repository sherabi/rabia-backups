#!/usr/bin/python
#bkenv.py is released under the General Public License.
#Copyright (C) 2010-2012 Shezaan Topiwala
#This file is part of "Rabia Backups".

#bkenv.py is free software: you can redistribute it and or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#bkenv.py is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with bkenv.py.  If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
HOME = os.getenv("HOME")
now = datetime.datetime.now()

BIN = HOME+"/rabia-backups" # Parent directory for all "backup scripts" and "backup-config".
BACKUP_DAILY = HOME+"/mydev/backup_daily.py" # Executable for daily backups.
BACKUP_WEEKLY = BIN+"/backup-weekly" # Executable for weekly backups.
BACKUP_MONTHLY = BIN+"/backup-monthly" # Executable for monthly backups.
BACKUP_YEARLY = BIN+"/backup-yearly" # Executable for yearly backups.
BACKUP_CONFIG = HOME+"/mydev/backup-config" # Location of configuration file.
BACKUP_TARGET = HOME+"/mydev/backups" # Parent destination where all backups will be stored. Must be changed to meet your criteria.
LOG_DIR = HOME+"/mydev/backup-logs" # Location of log files.
DISK_SPACE_ALERT = 95 # Backups are aborted if this disk space threshold is reached.
BACKUP_USER = "stopiwala" # Default remote and local backup user. This user can be overridden in the config file.
ADMIN_EMAILS = "stopiwala@questrade.com"

### DO NOT EDIT BELOW THIS LINE ###
TODAY = now.strftime("%Y-%m-%d@%H:%M:%S")
BACKUP_CONFIG_DAILY = LOG_DIR+"/backup-config-daily" # Automatically created by the respective executable
BACKUP_CONFIG_WEEKLY = LOG_DIR+"/backup-config-weekly" # Automatically created by the respective executable. 
BACKUP_CONFIG_MONTHLY = LOG_DIR+"/backup-config-monthly" # Automatically created by the respective executable. 
BACKUP_CONFIG_YEARLY = LOG_DIR+"/backup-config-yearly" # Automatically created by the respective executable. 
BACKUP_LOG_DAILY = LOG_DIR+"/backup-log-daily"
BACKUP_LOG_WEEKLY = LOG_DIR+"/backup-log-weekly"
BACKUP_LOG_MONTHLY = LOG_DIR+"/backup-log-monthly"
BACKUP_LOG_YEARLY = LOG_DIR+"/backup-log-yearly"