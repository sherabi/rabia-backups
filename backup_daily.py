#!/usr/bin/python
#backup_daily.py is released under the General Public License.
#Copyright (C) 2010-2012 Shezaan Topiwala
#This file is part of "Rabia Backups".

#backup_daily.py is free software: you can redistribute it and or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#backup_daily.py is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with backup_daily.py.  If not, see <http://www.gnu.org/licenses/>.

import sys
import getopt
import os
import datetime
import time
import shutil
import subprocess
import socket
import pickle
from ConfigParser import SafeConfigParser

hostname = socket.gethostname()
config = 'backup_config'
parser = SafeConfigParser()
parser.read(config)

RSYNC='rsync -avR --delete --stats'
BACKUP_LOG_DAILY = "junk"
BACKUP_MAIL = "junk_mail"
DESTINATION = "foo"
SERVER = "whatever"

def parse_config():
	global BACKUP_LOG_DAILY
	global BACKUP_MAIL
	global DESTINATION
	global SERVER
	for section_name in parser.sections():

		SERVER = section_name

		if parser.has_option(section_name, 'log_dir'):
			# Create the log directory.
			LOG_DIR = parser.get(section_name, 'log_dir')
			if not os.path.exists(LOG_DIR):
				os.makedirs(LOG_DIR, 0755)
			# Initialize backup mail file
			BACKUP_MAIL = LOG_DIR+"/backup_mail_daily"
			BACKUP_LOG_DAILY = LOG_DIR + "/backup_log_daily_" + SERVER
			print "log:", BACKUP_LOG_DAILY
			bkout = open(BACKUP_LOG_DAILY, 'w+')
		else:
			print 'log_dir not set for section %s' % (section_name)
			continue
		
		if parser.has_option(section_name, 'backup_type'):
			LOCATION = parser.get(section_name, 'backup_type')
		else:
			print 'backup_type not set for section %s' % (section_name)
			bkout.write('backup_type not available for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'include'):
			INCLUDES = parser.get(section_name, 'include')
		else:
			print 'include not set for section %s' % (section_name)
			bkout.write('include not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'exclude'):
			EXCLUDES = parser.get(section_name, 'exclude')
		else:
			print 'exclude not available for section %s' % (section_name)
			bkout.write('exclude not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'retention'):
			RETENTION = parser.get(section_name, 'retention')
		else:
			print 'retention not set for section %s' % (section_name)
			bkout.write('retention not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'backup_location'):
			DESTINATION = parser.get(section_name, 'backup_location')
			# Create Target directory.
			if not os.path.exists(DESTINATION):
				os.makedirs(DESTINATION)
		else:
			print 'backup_location not set for section %s' % (section_name)
			bkout.write('backup_location not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'interval'):
			INTERVAL = parser.get(section_name, 'interval')
		else:
			print 'interval not set for section %s' % (section_name)
			bkout.write('interval not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'include_file'):
			INCLUDE_FILENAME = parser.get(section_name, 'include_file')
		else:
			print 'include_file not set for section %s' % (section_name)
			bkout.write('include_file not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'exclude_file'):
			EXCLUDE_FILENAME = parser.get(section_name, 'exclude_file')
		else:
			print 'exclude_file not set for section %s' % (section_name)
			bkout.write('exclude_file not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'username'):
			USER = parser.get(section_name, 'username')
		else:
			print 'username not available for section %s' % (section_name)
			bkout.write('username not available for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'non_admin_emails'):
			MAIL_LIST = parser.get(section_name, 'non_admin_emails')
		else:
			print 'non_admin_emails not available for section %s' % (section_name)
			bkout.write('non_admin_emails not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'admin_emails'):
			ADMIN_EMAILS = parser.get(section_name, 'admin_emails')
		else:
			print 'admin_emails not available for section %s' % (section_name)
			bkout.write('admin_emails not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'disk_alert'):
			DISK_ALERT = parser.get(section_name, 'disk_alert')
		else:
			print 'disk_alert not available for section %s' % (section_name)
			bkout.write('disk_alert not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'disk_report'):
			DISK_REPORT = parser.get(section_name, 'disk_report')
		else:
			print 'disk_report not available for section %s' % (section_name)
			bkout.write('disk_report not set for section %s' % (section_name))
			continue

	 	INCLUDE_FILE = open(INCLUDE_FILENAME+"_"+SERVER, 'w+')
		for inc in INCLUDES.split(','):
			INCLUDE_FILE.write(inc.lstrip(' ')+"\n")
		INCLUDE_FILE.close()
		
		EXCLUDE_FILE = open(EXCLUDE_FILENAME+"_"+SERVER, 'w+')
		for exc in EXCLUDES.split(','):
			EXCLUDE_FILE.write(exc.lstrip(' ')+"\n")
		EXCLUDE_FILE.close()

		if (len(USER) == 0):
			print "username field is empty"
			bkout.write("username field is empty")
			continue

		#for option in ['exclude', 'username', 'non_admin_emails']:
		if (len(DESTINATION) > 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR " + SERVER + " ===\n"
			print "*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***"
			print "Destination: " + DESTINATION
			bkout.write("=== START OF BACKUPS FOR " + SERVER + " ===\n")
			bkout.write("*** BACKUPS FOR " + SERVER + " STARTED " + rightnow + " ***\n")
			bkout.write("Destination: " + DESTINATION + "\n")
		else:
			print "backup_location field is empty"
			bkout.write("backup_location field is empty")
			continue

		disk_space_check(DESTINATION, DISK_ALERT, DISK_REPORT, ADMIN_EMAILS, SERVER)
		bkout.flush()	
		try:
			delete_old(RETENTION, SERVER, DESTINATION+"/"+SERVER+"/daily")
		except:
			print "Directory to delete does not exist"
			bkout.write("Directory to delete does not exist\n")
			pass
		if LOCATION == "remote":
			#time.sleep(1)
			backup_remote(SERVER, DESTINATION, INCLUDE_FILENAME+"_"+SERVER, EXCLUDE_FILENAME+"_"+SERVER, USER)
		else:
			#time.sleep(1)
			backup_local(SERVER, DESTINATION, INCLUDE_FILENAME+"_"+SERVER, EXCLUDE_FILENAME+"_"+SERVER)
		copy_to_today(SERVER, DESTINATION, EXCLUDE_FILENAME+"_"+SERVER)
		bkout.close()

		#print parser.get(section_name, 'include')
		#print 'Section:', section_name
		#print '    Options:', parser.options(section_name)
		#for name, value in parser.items(section_name):
			#print '    %s = %s' % (name,value)
			#print parser.get(section_name, 'include')
		#print
	#print parser.get('Defaults', 'section_name')

def disk_space_check(directory, alert_threshold, disk_report, admin_emails, server):
	global BACKUP_MAIL
	if not os.path.exists(directory):
		os.makedirs(directory)
	ds = open(disk_report, 'w+')
	subprocess.Popen('df -hP ' + directory, shell=True, stdout=ds).communicate()
	ds.close()
	ds = open(disk_report, 'r')
	for i, line in enumerate(ds):
		if i == 1:
			s = line.split(' ')
			partition = s[0]
			use_perc = s[8]
			for char in use_perc:
				if char in "%":
					used_percentage = int(use_perc.replace(char,''))
					if (used_percentage > int(alert_threshold)):
						#time.sleep(3)
						now = datetime.datetime.now()
						backup_mail = open(BACKUP_MAIL, 'a+')
						backup_mail.write('Running out of space on ' + hostname + ' for partition ' + partition + ' as of ' + now.strftime("%Y-%m-%d@%H:%M:%S") + '.\n')
						backup_mail.write('Threshold for disk space was reached at ' + str(alert_threshold) + '% backup was aborted for ' + server)
						backup_mail.close()
						mail_str = 'mailx -s  \"Alert: Almost out of disk space, backups ABORTED - ' + str(used_percentage) + '%\" ' + admin_emails + " < " + BACKUP_MAIL
						subprocess.Popen(mail_str, shell=True)
						print 'Running out of space on ' + hostname + ' for partition ' + partition + ' as of ' + now.strftime("%Y-%m-%d@%H:%M:%S") + '.'
						print 'Threshold for disk space was reached at, ' + str(alert_threshold) + '% backup was aborted.'
						sys.exit(1)	

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def delete_old(retention, server, directory):
	now = datetime.datetime.now()
	TODAY = now.strftime("%Y-%m-%d")
	bkout = open(BACKUP_LOG_DAILY, 'a')
	print "Deletion destination: %s" %(directory)
	bkout.write("Deletion destination: %s\n" %(directory))
	count = 0
	filestack = []
	discard = []
	for dir in os.listdir(directory):
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
				print "Discarded directory: %s\n" %(dir)
				bkout.write("Discarded directory %s\n" %(dir))
		except:
			discard.append(dir)
			pass	
		
	print "Ignored: %s" %(discard)
	bkout.write("Ignored: %s\n" %(discard))
	
	print "Filestack: %s" %(filestack)
	bkout.write("Filestack: %s\n" %(filestack))
	
	sorted_stack = sorted(filestack)
	stack_length = len(sorted_stack)
	print "Sorted Stack: %s" %(sorted_stack)
	print "Stack Length: %s" %(stack_length)
	bkout.write("Sorted Stack %s\n" %(sorted_stack))
	bkout.write("Stack Length: %s\n" %(stack_length))

	if (count <= int(retention)):
		last_element = sorted_stack[stack_length-1]
		print "Last Element %s" %(last_element)
		bkout.write("Last Element: %s\n" %(last_element))
		if (TODAY == last_element):
			print "Backup of name %s already exists" %(last_element)
			bkout.write("Backup of name %s already exists\n" %(last_element))
			delete_num = 0
		else:
			print "Retention: " + retention
			bkout.write("Retention: " + retention + "\n")
			delete_num = count-int(retention)+1
			print "Files to delete, count match: " + str(delete_num)
			bkout.write("Files to delete, count match: " + str(delete_num) + "\n")
	elif (count > int(retention)):
		delete_num = count-int(retention)
		print "Files to delete, count greater: " + str(delete_num)
		bkout.write("Files to delete, count greater: " + str(delete_num) + "\n")
	else:
		delete_num = 0
		print "Nothing to delete " + str(delete_num)
		bkout.write("Nothing to delete " + str(delete_num) + "\n")
	try:
		os.chdir(directory)
	except:
		print "Unable to switch directory, no such directory or permission issue"
		bkout.write("Unable to switch directory, no such directory or permission issue\n")
		pass

	delete_stack = sorted_stack[:delete_num]
	print "Delete these %s" %(delete_stack)
	bkout.write("Delete these %s\n" %(delete_stack))
	keep_stack = sorted_stack[delete_num:]
	print "Keep these ", keep_stack
	bkout.write("Keep these %s\n" %(keep_stack))
	for folder in delete_stack:
		shutil.rmtree(folder)
	bkout.flush()
	#bkout.close()

# If backup is to type "remote" then rsync over ssh.
def backup_remote(server, directory, include_file, exclude_file, username):
	print "Daily LOG:", BACKUP_LOG_DAILY
	bkout = open(BACKUP_LOG_DAILY, 'a+')
	CURRENT = directory+"/"+server+"/daily/current"
	DAILY_DST = directory+"/"+server+"/daily/"
	if not os.path.exists(DAILY_DST):
		os.makedirs(DAILY_DST)
	INC_FILE = open(include_file, 'r')
	for inc_line in INC_FILE:
		line = inc_line.rstrip()
		print RSYNC + " --exclude-from=" + exclude_file + " -e ssh " + username + "@" + server + ":" + line + " " + CURRENT
		process = subprocess.Popen(RSYNC + ' --exclude-from=' + exclude_file + ' -e ssh ' + username + '@' + server + ':' + line + ' ' + CURRENT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#process = subprocess.Popen(RSYNC + ' --exclude-from=' + exclude_file + ' -e ssh ' + username + '@' + server + ':' + line + ' ' + CURRENT, shell=True, stdout=bkout)
		ret_code = process.wait()
		out = process.communicate()
		myout = out[0]
		myerr = out[1]
		print myout
		print myerr
		bkout.write(myout + myerr + "\n")
	INC_FILE.close()
	bkout.flush()
	#bkout.close()

# If backup is of type "local" then do a regular rsync.
def backup_local(server, directory, include_file, exclude_file):
	print "Daily LOG:", BACKUP_LOG_DAILY
	bkout = open(BACKUP_LOG_DAILY, 'a+')
	CURRENT = directory+"/"+server+"/daily/current"
	DAILY_DST = directory+"/"+server+"/daily/"
	if not os.path.exists(DAILY_DST):
		os.makedirs(DAILY_DST)
	INC_FILE = open(include_file, 'r')
	for inc_line in INC_FILE:
		line = inc_line.rstrip()
		print RSYNC + ' --exclude-from=' + include_file + ' ' + line + ' ' + CURRENT
		process = subprocess.Popen(RSYNC + ' --exclude-from=' + exclude_file + ' ' + line + ' ' + CURRENT, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		#process = subprocess.Popen(RSYNC + ' --exclude-from=' + exclude_file + ' ' + line + ' ' + CURRENT, shell=True, stdout=bkout, stderr=bkout)
		ret_code = process.wait()
		out = process.communicate()
		myout = out[0]
		myerr = out[1]
		print myout
		print myerr
	bkout.write(myout + myerr + "\n")
	INC_FILE.close()
	bkout.flush()
	#bkout.close()

# Hardlink files from "current" directory to todays dated directory.
# Hardlinks here allow for incremental backups.
def copy_to_today(server, directory, exclude_file):
	global SERVER
	now = datetime.datetime.now()
	TODAY = now.strftime("%Y-%m-%d")
	bkout = open(BACKUP_LOG_DAILY, 'a+')
	CURRENT = directory+"/"+server+"/daily/current"
	NEW_DST = directory+"/"+server+"/daily/"+TODAY
	if not os.path.exists(NEW_DST):
		os.makedirs(NEW_DST)
	if not os.path.exists(CURRENT):
		os.makedirs(CURRENT)
	# Start of adding support to remove an exclusion if it previously existed
	EXC_FILE = open(exclude_file, 'r')
	if os.stat(exclude_file)[6] != 1:
		for exc_line in EXC_FILE:
			line = exc_line.rstrip()
			delete_path = CURRENT+"/"+line
			print "Delete path is:",delete_path
			rm_process = subprocess.Popen('rm -rf ' + delete_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			#rm_process = subprocess.Popen('rm -rf ' + delete_path, shell=True, stdout=bkout, stderr=bkout)
			ret_code_rm = rm_process.wait()
			rm_out = rm_process.communicate()
			rm_myout = rm_out[0]
			rm_myerr = rm_out[1]
			bkout.write(rm_myout + rm_myerr + "\n")
	EXC_FILE.close()
	# End of adding support to remove an exclusion if it previously existed
	#process = subprocess.Popen('cp -al ' + CURRENT+"/* " + NEW_DST, shell=True, stdout=bkout, stderr=bkout)
	process = subprocess.Popen('cp -al ' + CURRENT+"/* " + NEW_DST, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	ret_code = process.wait()
	out = process.communicate()
	myout = out[0]
	myerr = out[1]
	bkout.write(myout + myerr + "\n")

	new_time = datetime.datetime.now()
	print "*** BACKUPS FOR " + SERVER + " ENDED "+ new_time.strftime("%Y-%m-%d@%H:%M:%S") + " ***"
	print "=== END OF BACKUPS FOR " + SERVER + " ===\n\n"
	bkout.write("*** BACKUPS FOR " + SERVER + " ENDED "+ new_time.strftime("%Y-%m-%d@%H:%M:%S") + " ***\n")
	bkout.write("=== END OF BACKUPS FOR " + SERVER + " ===\n\n")
	bkout.flush()
	#bkout.close()

parse_config()
