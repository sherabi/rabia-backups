#!/usr/bin/python
import sys
import getopt
import os
import datetime
#import time
import shutil
import subprocess
import socket
import smtplib
from bkenv import *

hostname = socket.gethostname()
EXCLUDE_FILENAME = LOG_DIR+"/backup-excludes-daily"
INCLUDE_FILENAME = LOG_DIR+"/backup-includes-daily"
BACKUP_MAIL = LOG_DIR+"/backup-mail-daily"
DISK_STATUS = LOG_DIR+"/disk-report-daily"
RSYNC='rsync -avR --delete --stats'

TODAY = now.strftime("%Y-%m-%d")
DESTINATION = "foo"
OVERIDE_USER = "bar"

# Create the log directory
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR, 0744)

# Parse out the GENERIC config file.
def parse_generic_config():
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

	config.close()
	config_daily.close()

# Parse out ONLY the DAILY configuration file.
def parse_daily_config():
	global DESTINATION
	global OVERIDE_USER
	config = open(BACKUP_CONFIG_DAILY, 'r')
	for line in config:
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
			
		INCLUDE_FILE = open(INCLUDE_FILENAME, 'w+')
		for inc in INCLUDES.split(','):
			INCLUDE_FILE.write(inc+"\n")
				
		EXCLUDE_FILE = open(EXCLUDE_FILENAME, 'w+')
		for exc in EXCLUDES.split(','):	
			EXCLUDE_FILE.write(exc+"\n")

		INCLUDE_FILE.close()
		EXCLUDE_FILE.close()

		if (len(TARGET) == 0) and (len(BASE_BACKUP_DIR) > 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			print "Only default location specified: Priority set to Default " + BASE_BACKUP_DIR
			DESTINATION = BASE_BACKUP_DIR
			print "Destination:", DESTINATION
		elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) == 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			print "Only target location specified: Priority set to Target " + TARGET
			DESTINATION = TARGET
			print "Destination:", DESTINATION
		elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) > 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " +  SERVER + " ===\n"
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			print "Both locations specified: Priority set to Target " + TARGET
			DESTINATION = TARGET
			print "Destination:", DESTINATION
		elif (len(TARGET) == 0) and (len(BASE_BACKUP_DIR) == 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
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

		disk_space_check()
		try:
			delete_old(RETENTION, SERVER, DESTINATION+SERVER+"/daily")
		except:
			print "Directory to delete does not exist"
			pass
		if LOCATION == "remote":
			#time.sleep(1)
			backup_remote(SERVER)
		else:
			#time.sleep(1)
			backup_local(SERVER)
		copy_to_today(SERVER)
		#time.sleep(3)
		new_time = datetime.datetime.now()
		print "*** BACKUPS FOR " + SERVER + " ENDED "+ new_time.strftime("%Y-%m-%d@%H:%M:%S") + " ***"
		print "=== END OF BACKUPS FOR " + SERVER +" ===\n"

	config.close()

# Delete backup older than RETENTION number of backups.
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
		os.chdir(DIRECTORY)
	except:
		print "Unable to switch directory, no such directory or permission issue"
		pass
	sorted_stack = sorted(filestack)
	print "Sorting...", sorted_stack
	delete_stack = sorted_stack[:delete_num]
	print "Delete these", delete_stack
	keep_stack = sorted_stack[delete_num:]
	print "Keep these", keep_stack
	for folder in delete_stack:
		shutil.rmtree(folder)

def copy_to_today(server):
	global DESTINATION
	CURRENT = DESTINATION+server+"/daily/current"
	NEW_DST = DESTINATION+server+"/daily/"+TODAY
	if not os.path.exists(NEW_DST):
		os.makedirs(NEW_DST)
	#subprocess.Popen('cp -al ' + CURRENT+"/* " + NEW_DST, shell=True).communicate()
	process = subprocess.Popen('cp -al ' + CURRENT+"/* " + NEW_DST, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = process.communicate()
	myout = out[0]
	myerr = out[1]
	print myout
	print myerr

def backup_remote(server):
	global DESTINATION
	CURRENT = DESTINATION+server+"/daily/current"
	DAILY_DST = DESTINATION+server+"/daily/"
	if not os.path.exists(DAILY_DST):
		os.makedirs(DAILY_DST)
	INC_FILE = open(INCLUDE_FILENAME, 'r')
	for inc_line in INC_FILE:
		line = inc_line.rstrip()
		print RSYNC + " --exclude-from=" + EXCLUDE_FILENAME + " -e ssh " + OVERIDE_USER + "@" + server + ":" + line + " " + CURRENT
		#subprocess.Popen(RSYNC + ' --exclude-from=' + EXCLUDE_FILENAME + ' -e ssh ' + OVERIDE_USER + '@' + server + ':' + line + ' ' + CURRENT, shell=True).communicate()
		process = subprocess.Popen(RSYNC + ' --exclude-from=' + EXCLUDE_FILENAME + ' -e ssh ' + OVERIDE_USER + '@' + server + ':' + line + ' ' + CURRENT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out = process.communicate()
		myout = out[0]
		myerr = out[1]
		print myout
		print myerr
	INC_FILE.close()

def backup_local(server):
	global DESTINATION
	CURRENT = DESTINATION+server+"/daily/current"
	DAILY_DST = DESTINATION+server+"/daily/"
	if not os.path.exists(DAILY_DST):
		os.makedirs(DAILY_DST)
	INC_FILE = open(INCLUDE_FILENAME, 'r')
	for inc_line in INC_FILE:
		line = inc_line.rstrip()
		print RSYNC + ' --exclude-from=' + EXCLUDE_FILENAME + ' ' + line + ' ' + CURRENT
		#subprocess.Popen(RSYNC + ' --exclude-from=' + EXCLUDE_FILENAME + ' ' + line + ' ' + CURRENT, shell=True).communicate()
		process = subprocess.Popen(RSYNC + ' --exclude-from=' + EXCLUDE_FILENAME + ' ' + line + ' ' + CURRENT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out = process.communicate()
		myout = out[0]
		myerr = out[1]
		print myout
		print myerr
	INC_FILE.close()

def disk_space_check():
	global DESTINATION
	ds = open(DISK_STATUS, 'w+')
	subprocess.Popen('df -hP ' + DESTINATION, shell=True, stdout=ds).communicate()
	#subprocess.Popen('df -hP ' + DESTINATION, shell=True, stdout=ds)
	ds.close()
	ds = open(DISK_STATUS, 'r')
	for i, line in enumerate(ds):
		if i == 1:
			s = line.split(' ')
			partition = s[0]
			use_perc = s[9]
			for char in use_perc:
				if char in "%":
					used_percentage = int(use_perc.replace(char,''))
					if used_percentage > DISK_SPACE_ALERT:
						#time.sleep(3)
						new_time = datetime.datetime.now()
						backup_mail = open(BACKUP_MAIL, 'w+')
						backup_mail.write('Running out of space on ' + hostname + ' for partition ' + partition + ' as of ' + new_time.strftime("%Y-%m-%d@%H:%M:%S") + '.\n')
						backup_mail.write('Threshold for disk space was reached at, ' + str(DISK_SPACE_ALERT) + '% backup was aborted.')
						backup_mail.close()
						mail_str = 'mailx -s  \"Alert: Almost out of disk space, backups ABORTED - ' + str(used_percentage) + '%\" ' + ADMIN_EMAILS + " < " + BACKUP_MAIL
						subprocess.Popen(mail_str, shell=True)
						print 'Running out of space on ' + hostname + ' for partition ' + partition + ' as of ' + new_time.strftime("%Y-%m-%d@%H:%M:%S") + '.'
						print 'Threshold for disk space was reached at, ' + str(DISK_SPACE_ALERT) + '% backup was aborted.'
						sys.exit(1)

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

# Evaluate all the options/flags
def main(argv):
	try:
		options, args = getopt.getopt(argv, "t:c:l:u:", ["target=", "config=", "logfile=", "user="])
	except getopt.GetoptError:
		print "Usage...TBD"
		sys.exit(1)
	
	for opt, arg in options:
		if opt in ("-t", "--target"):
			global BASE_BACKUP_DIR
			BASE_BACKUP_DIR = arg
		elif opt in ("-c", "--config"):
			global BACKUP_CONFIG
			BACKUP_CONFIG = arg
		elif opt in ("-l", "--logfile"):
			global BACKUP_LOG
			BACKUP_LOG = arg
		elif opt in ("-u", "--user"):
			global BACKUP_USER
			BACKUP_USER = arg
	parse_generic_config()
	parse_daily_config()


if __name__ == "__main__":
    main(sys.argv[1:])
