#!/usr/bin/python
import sys
import getopt
import os
import datetime
import shutil
from bkenv import *

EXCLUDE_FILE=LOG_DIR+"/backup-excludes-daily"
INCLUDE_FILE=LOG_DIR+"/backup-includes-daily"
BACKUP_MAIL=LOG_DIR+"/backup-mail-daily"
DISK_STATUS=LOG_DIR+"/disk-report-daily"
RSYNC='rsync -avR --delete --stats'

# Create the log directory
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR, 0744)

# Evaluate all the options/flags
def main(argv):
	try:
		options, args = getopt.getopt(argv, "t:c:l:u:", ["target=", "config=", "logfile=", "user="])
		#print "Options: ", options
		#print "Args:", args

	except getopt.GetoptError:
		print "Usage...TBD"
		sys.exit(1)
	
	for opt, arg in options:
		if opt in ("-t", "--target"):
			global BASE_BACKUP_DIR
			BASE_BACKUP_DIR = arg
			#print BASE_BACKUP_DIR
		elif opt in ("-c", "--config"):
			global BACKUP_CONFIG
			BACKUP_CONFIG = arg
			#print BACKUP_CONFIG
		elif opt in ("-l", "--logfile"):
			global BACKUP_LOG
			BACKUP_LOG = arg
			#print BACKUP_LOG
		elif opt in ("-u", "--user"):
			global BACKUP_USER
			BACKUP_USER = arg
			#print BACKUP_USER
	parse_generic_config()
	parse_daily_config()

now = datetime.datetime.now()
rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
TODAY = now.strftime("%Y-%m-%d")
global DESTINATION
DESTINATION = ""
OVERIDE_USER = ""

# Parse out the GENERIC config file.
def parse_generic_config():
	if not os.path.exists(LOG_DIR):
		os.makedirs(LOG_DIR)
	if not os.path.exists(BACKUP_TARGET):
		os.makedirs(BACKUP_TARGET)
	print BACKUP_COFIG
	config = open(BACKUP_CONFIG, 'r')
	config_daily = open(LOG_DIR+'/backup-config-daily', 'w+')
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
				#cmd = "python "+ BACKUP_DAILY + " -t " + BACKUP_TARGET + " -c " + BACKUP_CONFIG_DAILY + " -l " +  BACKUP_LOG_DAILY + " -u " +  BACKUP_USER
				#print cmd

	config.close()
	config_daily.close()

# Parse out ONLY the DAILY configuration file.
def parse_daily_config():
	config = open(BACKUP_CONFIG_DAILY, 'r')
	for line in config:
		line = line.rstrip()
		if line != '':
			if not line.startswith("#"):
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
				
				#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
				if (len(TARGET) == 0) and (len(BASE_BACKUP_DIR) > 0):
					print "=== START OF BACKUPS FOR $SERVER ===\n"
					print "Target length:", len(TARGET)
					print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
					print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
					print "Only default location specified: Priority set to Default " + BASE_BACKUP_DIR
					DESTINATION = BASE_BACKUP_DIR
					print "Destination:", DESTINATION
				elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) == 0):
				 	print "=== START OF BACKUPS FOR $SERVER ===\n"
					print "Target length:", len(TARGET)
					print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
					print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
					print "Only target location specified: Priority set to Target " + TARGET
					DESTINATION = TARGET
					print "Destination:", DESTINATION
				elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) > 0):
				 	print "=== START OF BACKUPS FOR $SERVER ===\n"
					print "Target length:", len(TARGET)
					print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
					print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
					print "Both locations specified: Priority set to Target " + TARGET
					DESTINATION = TARGET
					print "Destination:", DESTINATION
				elif (len(TARGET) == 0) and (len(BASE_BACKUP_DIR) == 0):
					print "=== START OF BACKUPS FOR $SERVER ===\n"
					print "Target length:", len(TARGET)
					print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
					print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
					print "Neither locations specified: Priority set to Target " + TARGET
					DESTINATION = TARGET
					print "Destination:", DESTINATION

				if (len(USER) == 0) and (len(BACKUP_USER) > 0):
					print "Only default user specified: Priority set to Default user " + BACKUP_USER
					OVERIDE_USER = BACKUP_USER
					print "Overide user: ", OVERIDE_USER
				elif (len(USER) > 0) and (len(BACKUP_USER) == 0):
					print "Only overiding user specified: Priority set to use Overide user " + USER
					OVERIDE_USER = USER
					print "Overide user: ", OVERIDE_USER
				elif (len(USER) > 0) and (len(BACKUP_USER) > 0):
					print "Both users specified: Priority to use Overide user " + USER
					OVERIDE_USER = USER
					print "Overide user: ", OVERIDE_USER
				elif (len(USER) == 0) and (len(BACKUP_USER) == 0):
					print "Both users specified: Priority to use Overide user " + USER
					OVERIDE_USER = USER
					print "Overide user: ", OVERIDE_USER

				#disk_space_check()

				#delete_old(RETENTION, SERVER, DESTINATION+"/"+SERVER+"/daily")
				delete_old(RETENTION, SERVER, "/tmp/shez/"+SERVER+"/daily")

def delete_old(RETENTION, SERVER, DIRECTORY):
	DESTINATION = DIRECTORY
	print "Destination", DESTINATION
	count = 0
	filestack = []
	discard = []
	for dir in os.listdir(DIRECTORY):
		try:
			pattern = dir.split('-')
			year = pattern[0]
			month = pattern[1]
			day = pattern[2]
			#print year, month, day
			#print is_number(year)
			if is_number(year) == True and is_number(month)== True and is_number(day) == True and len(year) == 4 and len(month) == 2 and len(day) == 2:
				count = count+1
				filestack.append(dir)
			else:
				discard.append(dir)
				print "Discarded directory:", dir
		except:
			discard.append(dir)
			pass

	print "Ignored/Discarded", discard		
	print "Filestack", filestack
	
	if (count < int(RETENTION)):
		stack_length = len(filestack)
		print "Stack Length:", stack_length
		last_element = filestack[stack_length-1]
		print "Last Element", last_element
		if (TODAY == last_element):
			print "Backup of this name already exists"
			delete_num = 0
		else:
			print "Retention:",RETENTION
			delete_num = count-int(RETENTION)+1
			print "Files to delete, count match:", delete_num
	elif (count > int(RETENTION)):
		delete_num = count-int(RETENTION)
		print "Files to delete, count greater:", delete_num
	else:
		delete_num = 0 
		print "Nothing to delete", delete_num
	try:
		#os.chdir(DESTINATION+"/"+SERVER+"/daily")
		os.chdir(DIRECTORY)
	except:
		print "Unable to switch directory, no such directory or permission issue"
		pass
	sorted_stack = sorted(filestack)
	print "Sorting...", sorted_stack
	#print "Delete num:", delete_num
	delete_stack = sorted_stack[:delete_num]
	print "Delete these", delete_stack
	keep_stack = sorted_stack[delete_num:]
	print "Keep these", keep_stack
	for folder in delete_stack:
		#os.rmdir(folder) # Test please
		shutil.rmtree(folder) # Test please


def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False



#if __name__ == '__main__':
#	shez = backup()
#	shez.parse_config()

if __name__ == "__main__":
    main(sys.argv[1:])
