#!/usr/bin/python
import sys
import getopt
import os
import datetime
#import time
import shutil
import subprocess
import socket
from bkenv import *

# Pre startup variables
hostname = socket.gethostname()
EXCLUDE_FILENAME = LOG_DIR+"/backup-excludes-daily"
INCLUDE_FILENAME = LOG_DIR+"/backup-includes-daily"
BACKUP_MAIL = LOG_DIR+"/backup-mail-daily"
DISK_STATUS = LOG_DIR+"/disk-report-daily"
RSYNC='rsync -avR --delete --stats'

TODAY = now.strftime("%Y-%m-%d")
DESTINATION = "foo"
OVERIDE_USER = "bar"

# Create the log directory.
if not os.path.exists(LOG_DIR):
	os.makedirs(LOG_DIR, 0744)
# Create Target directory.
if not os.path.exists(BACKUP_TARGET):
	os.makedirs(BACKUP_TARGET)

bkout = open(BACKUP_LOG_DAILY, 'w+')

# Parse out ONLY the DAILY configuration file.
# The daily configuration file is created by the run file.
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
			bkout.write("=== START OF BACKUPS FOR " + SERVER + " ===\n")
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			bkout.write("*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***\n")
			print "Only default location specified: Priority set to Default " + BASE_BACKUP_DIR
			bkout.write("Only default location specified: Priority set to Default " + BASE_BACKUP_DIR + "\n")
			DESTINATION = BASE_BACKUP_DIR
			print "Destination: " + DESTINATION
			bkout.write("Destination: " + DESTINATION + "\n")
		elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) == 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			bkout.write("=== START OF BACKUPS FOR " + SERVER + " ===\n")
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			bkout.write("*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***\n")
			print "Only target location specified: Priority set to Target " + TARGET
			bkout.write("Only target location specified: Priority set to Target " + TARGET + "\n")
			DESTINATION = TARGET
			print "Destination:" + DESTINATION
			bkout.write("Destination: " + DESTINATION + "\n")
		elif (len(TARGET) > 0) and (len(BASE_BACKUP_DIR) > 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " +  SERVER + " ===\n"
			bkout.write("=== START OF BACKUPS FOR " + SERVER + " ===\n")
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			bkout.write("*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***\n")
			print "Both locations specified: Priority set to Target " + TARGET
			bkout.write( "Both locations specified: Priority set to Target " + TARGET + "\n")
			DESTINATION = TARGET
			print "Destination: " + DESTINATION
			bkout.write("Destination: " + DESTINATION + "\n")
		elif (len(TARGET) == 0) and (len(BASE_BACKUP_DIR) == 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			#print LOCATION+":"+SERVER+":"+INCLUDES+":"+EXCLUDES+":"+RETENTION+":"+TARGET+":"+USER+":"+INTERVAL+":"+MAIL_LIST
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***\n"
			print "Neither locations specified: Priority set to Target " + TARGET
			DESTINATION = TARGET
			print "Destination: " + DESTINATION
			bkout.write("Destination: " + DESTINATION + "\n")
		if (len(USER) == 0) and (len(BACKUP_USER) > 0):
			print "Only default user specified: Priority set to Default user " + BACKUP_USER
			bkout.write("Only default user specified: Priority set to Default user " + BACKUP_USER + "\n")
			OVERIDE_USER = BACKUP_USER
			print "Overide user: " + OVERIDE_USER
			bkout.write("Overide user: " + OVERIDE_USER + "\n")
		elif (len(USER) > 0) and (len(BACKUP_USER) == 0):
			print "Only overiding user specified: Priority set to use Overide user " + USER
			bkout.write("Only overiding user specified: Priority set to use Overide user " + USER + "\n")
			OVERIDE_USER = USER
			print "Overide user: " + OVERIDE_USER
			bkout.write("Overide user: " + OVERIDE_USER + "\n")
		elif (len(USER) > 0) and (len(BACKUP_USER) > 0):
			print "Both users specified: Priority to use Overide user " + USER
			bkout.write("Both users specified: Priority to use Overide user " + USER + "\n")
			OVERIDE_USER = USER
			print "Overide user: " + OVERIDE_USER
			bkout.write("Overide user: " + OVERIDE_USER + "\n")
		elif (len(USER) == 0) and (len(BACKUP_USER) == 0):
			print "Both users specified: Priority to use Overide user " + USER
			bkout.write("Both users specified: Priority to use Overide user " + USER + "\n")
			OVERIDE_USER = USER
			print "Overide user: " + OVERIDE_USER
			bkout.write("Overide user: " + OVERIDE_USER + "\n")

		disk_space_check()
		try:
			delete_old(RETENTION, SERVER, DESTINATION+"/"+SERVER+"/daily")
		except:
			print "Directory to delete does not exist"
			bkout.write("Directory to delete does not exist\n")
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
		bkout.write("*** BACKUPS FOR " + SERVER + " ENDED "+ new_time.strftime("%Y-%m-%d@%H:%M:%S") + " ***\n")
		print "=== END OF BACKUPS FOR " + SERVER + " ===\n\n"
		bkout.write("=== END OF BACKUPS FOR " + SERVER + " ===\n\n")
	config.close()

# Delete backups older than the RETENTION number of backups.
def delete_old(RETENTION, SERVER, DIRECTORY):
	DESTINATION = DIRECTORY
	print "Deletion destination" + DESTINATION
	bkout.write("Deletion destination " + DESTINATION + "\n")
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
				print "Discarded directory: " + dir
				bkout.write("Discarded directory " + dir + "\n")
		except:
			discard.append(dir)
			pass

	print "Ignored", discard
	discard_str = ', '.join(discard)
	bkout.write("Ignored: " + "[" + discard_str + "]" + "\n")
	print "Filestack: ", filestack
	filestack_str = ', '.join(filestack)
	bkout.write("Filestack: " + "[" + filestack_str + "]" + "\n")
	
	if (count < int(RETENTION)):
		stack_length = len(filestack)
		print "Stack Length: ", stack_length
		bkout.write("Stack Length: " + str(stack_length) + "\n")
		last_element = filestack[stack_length-1]
		print "Last Element " + last_element
		bkout.write("Last Element: " + last_element + "\n")
		if (TODAY == last_element):
			print "Backup of this name already exists"
			bkout.write("Backup of this name already exists\n")
			delete_num = 0
		else:
			print "Retention: " + RETENTION
			bkout.write("Retention: " + RETENTION + "\n")
			delete_num = count-int(RETENTION)+1
			print "Files to delete, count match: " + delete_num
			bkout.write("Files to delete, count match: " + delete_num + "\n")
	elif (count > int(RETENTION)):
		delete_num = count-int(RETENTION)
		print "Files to delete, count greater: ", delete_num
		bkout.write("Files to delete, count greater: " + str(delete_num) + "\n")
	else:
		delete_num = 0 
		print "Nothing to delete " + delete_num
		bkout.write("Nothing to delete " + delete_num + "\n")
	try:
		os.chdir(DIRECTORY)
	except:
		print "Unable to switch directory, no such directory or permission issue"
		bkout.write("Unable to switch directory, no such directory or permission issue\n")
		pass
	sorted_stack = sorted(filestack)
	sorted_stack_str = ', '.join(sorted_stack)
	print "Sorting... ", sorted_stack
	bkout.write("Sorting... " + sorted_stack_str + "\n")
	delete_stack = sorted_stack[:delete_num]
	delete_stack_str = ', '.join(delete_stack)
	print "Delete these ", delete_stack
	bkout.write("Delete these " + delete_stack_str + "\n")
	keep_stack = sorted_stack[delete_num:]
	keep_stack_str = ', '.join(keep_stack)
	print "Keep these ", keep_stack
	bkout.write("Keep these " + keep_stack_str + "\n")
	for folder in delete_stack:
		shutil.rmtree(folder)

# Hardlink files from "current" directory to todays dated directory.
# Hardlinks here allow for incremental backups.
def copy_to_today(server):
	global DESTINATION
	CURRENT = DESTINATION+"/"+server+"/daily/current"
	NEW_DST = DESTINATION+"/"+server+"/daily/"+TODAY
	if not os.path.exists(NEW_DST):
		os.makedirs(NEW_DST)
	if not os.path.exists(CURRENT):
		os.makedirs(CURRENT)
	# Start of adding support to remove an exclusion if it previously existed
	EXC_FILE = open(EXCLUDE_FILENAME, 'r')
	if os.stat(EXCLUDE_FILENAME)[6] != 1:
		for exc_line in EXC_FILE:
			line = exc_line.rstrip()
			delete_path = CURRENT+"/"+line
			print "Delete path is:",delete_path
			#if os.path.isdir(CURRENT+"/"+line) and os.path.exists(CURRENT+"/"+line):
				#shutil.rmtree(CURRENT+"/"+line)
			#elif  os.path.exists(CURRENT+"/"+line):
				#os.remove(CURRENT+"/"+line)
			rm_process = subprocess.Popen('rm -rf ' + delete_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			rm_out = rm_process.communicate()
			rm_myout = rm_out[0]
			rm_myerr = rm_out[1]
			bkout.write(rm_myout + rm_myerr + "\n")
			#print rm_myout
			#print rm_myerr
	EXC_FILE.close()
	# End of adding support to remove an exclusion if it previously existed
	process = subprocess.Popen('cp -al ' + CURRENT+"/* " + NEW_DST, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out = process.communicate()
	myout = out[0]
	myerr = out[1]
	bkout.write(myout + myerr + "\n")
	#print myout
	#print myerr

# If backup is to type "remote" then rsync over ssh.
def backup_remote(server):
	global DESTINATION
	CURRENT = DESTINATION+"/"+server+"/daily/current"
	DAILY_DST = DESTINATION+"/"+server+"/daily/"
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
		bkout.write(myout + myerr + "\n")
	INC_FILE.close()

# If backup is of type "local" then do a regular rsync.
def backup_local(server):
	global DESTINATION
	CURRENT = DESTINATION+"/"+server+"/daily/current"
	DAILY_DST = DESTINATION+"/"+server+"/daily/"
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
		bkout.write(myout + myerr + "\n")
	INC_FILE.close()

# Check for diskspace and compare against threshold alert in bkenv.py
def disk_space_check():
	global DESTINATION
	if not os.path.exists(DESTINATION):
		os.makedirs(DESTINATION)
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

# Yank text between "START" and "END" delimiters of the main log file.
# and write it out to an independant server log file with timestamp.
def strip_chunk():
	config = open(BACKUP_CONFIG).readlines()
	for line in config:
		line = line.rstrip()
		if line !='': # Ignore newlines or empty lines
			if not line.startswith("#"):  #Ignore comments
				field = line.split(':')
				server = field[1]
				new_time = datetime.datetime.now()
				right_now = new_time.strftime("%Y-%m-%d@%H:%M:%S")
				infile = open(BACKUP_LOG_DAILY).readlines()
				outfile = open(BACKUP_LOG_DAILY + "_" + server + "_" + right_now, 'w+')
				parsing = False
				for myline in infile:
					if myline.startswith("=== START OF BACKUPS FOR " + server + " ==="):
						parsing = True
					elif myline.startswith("=== END OF BACKUPS FOR " + server + " ==="):
						outfile.write(myline)
						parsing = False
						outfile.close()
					if parsing:
						outfile.write(myline)

# Check if variable is a number or not
def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def usage():
	print "\n\tUsage: backup_daily.py -t target -c config_file -l log_file -u backup_username"
	print "\t-h --help: Print this help."
	print "\t-t --target: Location of backups, see or edit bkenv.py."
	print "\t-c --config: Location of config file, see or edit backup-config."
	print "\t-l --logfile: Location of log file, see or edit bkenv.py."
	print "\t-u --user: User whose ssh key/s permit backups."
	print "\tGlobal/Default settings editable by file bkenv.py."
	print "\tConfiguration/Overiding bkenv.py settings editable by file backup-config."


# Evaluate all the options/flags
def main(argv):
	help = False
	try:
		options, args = getopt.getopt(argv, "ht:c:l:u:", ["target=", "config=", "logfile=", "user=", "help"])
		if len(options) < 4:
			usage()
			sys.exit(3)
	except getopt.GetoptError:
		print "Exception not working"
		sys.exit(2)
	for opt, arg in options:
		if opt in ("-h", "--help"):
			print "Something is wrong"
		elif opt in ("-t", "--target"):
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
	parse_daily_config()

if __name__ == "__main__":
	main(sys.argv[1:])
	bkout.close()
	strip_chunk()
