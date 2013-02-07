#!/usr/bin/python
import os
import datetime
HOME = os.getenv("HOME")
now = datetime.datetime.now()

BIN = HOME+"/rabia-backups" # Parent directory for all "backup scripts" and "backup-config".
BACKUP_DAILY = HOME+"/mydev/backup-daily.py" # Executable for daily backups.
BACKUP_WEEKLY = BIN+"/backup-weekly" # Executable for weekly backups.
BACKUP_MONTHLY = BIN+"/backup-monthly" # Executable for monthly backups.
BACKUP_YEARLY = BIN+"/backup-yearly" # Executable for yearly backups.
BACKUP_CONFIG = HOME+"/mydev/backup-config" # Location of configuration file.
BACKUP_TARGET = HOME+"/mydev/backups" # Parent destination where all backups will be stored. Must be changed to meet your criteria.
LOG_DIR = HOME+"/mydev/backup-logs" # Location of log files.
DISK_SPACE_ALERT = 90 # Backups are aborted if this disk space threshold is reached.
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
