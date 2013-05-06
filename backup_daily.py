#!/usr/bin/python
#backup_daily.py is released under the General Public License.
#Copyright (C) 2010-2013 Shezaan Topiwala
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
import os
import datetime
import shutil
import subprocess
import socket
import fnmatch
from ConfigParser import SafeConfigParser
from os.path import join, abspath

hostname = socket.gethostname()
config = 'backup_config'
parser = SafeConfigParser()
parser.read(config)

RSYNC='rsync -avR --delete --stats'

def parse_config():
	for section_name in parser.sections():
		server = section_name
		if parser.has_option(section_name, 'log_dir'):
			# Create the log directory.
			log_dir = parser.get(section_name, 'log_dir')
			if not os.path.exists(log_dir):
				os.makedirs(log_dir, 0755)
			# Initialize backup mail file
			disk_report = log_dir+"/disk_report_daily"
			daily_log = log_dir + "/backup_log_daily_" + server
			include_filename =  log_dir + "/backup_includes_daily_" + server
			exclude_filename =  log_dir + "/backup_excludes_daily_" + server
			bkout = open(daily_log, 'w+', 0)
		else:
			print 'log_dir not set for section %s' % (section_name)
			continue
		
		if parser.has_option(section_name, 'backup_type'):
			location = parser.get(section_name, 'backup_type')
		else:
			print 'backup_type not set for section %s' % (section_name)
			bkout.write('backup_type not available for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'include'):
			includes = parser.get(section_name, 'include')
		else:
			print 'include not set for section %s' % (section_name)
			bkout.write('include not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'exclude'):
			excludes = parser.get(section_name, 'exclude')
		else:
			print 'exclude not available for section %s' % (section_name)
			bkout.write('exclude not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'retention'):
			retention = parser.get(section_name, 'retention')
		else:
			print 'retention not set for section %s' % (section_name)
			bkout.write('retention not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'backup_location'):
			destination = parser.get(section_name, 'backup_location')
			# Create Target directory.
			if not os.path.exists(destination):
				os.makedirs(destination)
		else:
			print 'backup_location not set for section %s' % (section_name)
			bkout.write('backup_location not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'interval'):
			interval = parser.get(section_name, 'interval')
		else:
			print 'interval not set for section %s' % (section_name)
			bkout.write('interval not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'username'):
			user = parser.get(section_name, 'username')
		else:
			print 'username not available for section %s' % (section_name)
			bkout.write('username not available for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'non_admin_emails'):
			mail_list = parser.get(section_name, 'non_admin_emails')
		else:
			print 'non_admin_emails not available for section %s' % (section_name)
			bkout.write('non_admin_emails not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'admin_emails'):
			admin_emails = parser.get(section_name, 'admin_emails')
		else:
			print 'admin_emails not available for section %s' % (section_name)
			bkout.write('admin_emails not set for section %s' % (section_name))
			continue

		if parser.has_option(section_name, 'disk_alert'):
			disk_alert = parser.get(section_name, 'disk_alert')
		else:
			print 'disk_alert not available for section %s' % (section_name)
			bkout.write('disk_alert not set for section %s' % (section_name))
			continue

	 	include_file = open(include_filename, 'w+')
		for inc in includes.split(','):
			include_file.write(inc.lstrip(' ')+"\n")
		include_file.close()
		
		exclude_file = open(exclude_filename, 'w+')
		for exc in excludes.split(','):
			exclude_file.write(exc.lstrip(' ')+"\n")
		exclude_file.close()

		if (len(user) == 0):
			print "username field is empty"
			bkout.write("username field is empty")
			continue

		if (len(destination) > 0):
			now = datetime.datetime.now()
			rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
			print "=== START OF BACKUPS FOR %s ===\n" %(server)
			print "*** BACKUPS FOR %s STARTED %s ***" %(server, rightnow)
			print "Destination: %s" %(destination)
			bkout.write("=== START OF BACKUPS FOR %s ===\n" %(server))
			bkout.write("*** BACKUPS FOR %s STARTED %s ***\n" %(server, rightnow))
			bkout.write("Destination: %s\n" %(destination))
		else:
			print "backup_location field is empty"
			bkout.write("backup_location field is empty")
			continue

		bkout.flush()
		disk_space_check(destination, disk_alert, disk_report, admin_emails, server)
		try:
			bkout.flush()
			delete_old(retention, server, destination+"/"+server+"/daily", daily_log)
		except:
			print "Directory to delete does not exist"
			bkout.write("Directory to delete does not exist\n")
			pass
		if location == "remote":
			backup_remote(server, destination, include_filename, exclude_filename, user, daily_log)
		else:
			backup_local(server, destination, include_filename, exclude_filename, daily_log)
		copy_to_today(server, destination, exclude_filename, daily_log)
		bkout.close()

def disk_space_check(directory, alert_threshold, disk_report, admin_emails, server):
	st = os.statvfs(directory)
	free = st.f_bavail * st.f_frsize
	total = st.f_blocks * st.f_frsize
	used = (st.f_blocks - st.f_bavail) * st.f_frsize
	used_percentage = used * 100 / total
	if (used_percentage > int(alert_threshold)):
		now = datetime.datetime.now()
		disk_report_mail = open(disk_report, 'w+')
		disk_report_mail.write('Running out of space on %s for %s as of %s.\n' %(hostname, directory, now.strftime("%Y-%m-%d@%H:%M:%S")))
		disk_report_mail.write('Threshold for disk space was reached at %s%% backup was aborted for %s ' %(str(alert_threshold), server))
		disk_report_mail.close()
		mail_str = 'mailx -s  \"Alert: Almost out of disk space, backups ABORTED - ' + str(used_percentage) + '%\" ' + admin_emails + " < " + disk_report
		subprocess.Popen(mail_str, shell=True)
		print 'Running out of space on %s for %s as of %s.' %(hostname, directory, now.strftime("%Y-%m-%d@%H:%M:%S"))
		print 'Threshold for disk space was reached at, %s%% backup was aborted for %s' %(str(alert_threshold), server)
		disk_report_mail.close()
		sys.exit(1)	

def is_number(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def delete_old(retention, server, directory, daily_log):
	now = datetime.datetime.now()
	today = now.strftime("%Y-%m-%d")
	count = 0
	filestack = []
	discard = []
	bkout = open(daily_log, 'a', 0)
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
		if (today == last_element):
			print "Backup of name %s already exists" %(last_element)
			bkout.write("Backup of name %s already exists\n" %(last_element))
			delete_num = 0
		else:
			print "Retention: %s" %(retention)
			bkout.write("Retention: %s.\n" %(retention))
			delete_num = count-int(retention)+1
			print "Files to delete, count match: %s" %(str(delete_num))
			bkout.write("Files to delete, count match: %s.\n" %(str(delete_num)))
	elif (count > int(retention)):
		delete_num = count-int(retention)
		print "Files to delete, count greater: %s" %(str(delete_num))
		bkout.write("Files to delete, count greater: %s.\n" %(str(delete_num)))
	else:
		delete_num = 0
		print "Nothing to delete %s" %(str(delete_num))
		bkout.write("Nothing to delete %s.\n" %(str(delete_num)))
	try:
		os.chdir(directory)
	except:
		print "Unable to switch directory, no such directory or permission issue"
		bkout.write("Unable to switch directory, no such directory or permission issue\n")
		pass
	delete_stack = sorted_stack[:delete_num]
	print "Delete these: %s" %(delete_stack)
	bkout.write("Delete these: %s\n" %(delete_stack))
	keep_stack = sorted_stack[delete_num:]
	print "Keep these: %s" %(keep_stack)
	bkout.write("Keep these: %s\n" %(keep_stack))
	for folder in delete_stack:
		shutil.rmtree(folder)
	bkout.flush()

# If backup is of type "remote" then rsync over ssh.
def backup_remote(server, directory, include_file, exclude_file, username, daily_log):
	print "Daily LOG: %s" %(daily_log)
	bkout = open(daily_log, 'a', 0)
	bkout.write("Daily LOG: %s\n" %(daily_log))
	current = directory+"/"+server+"/daily/current"
	daily_dst = directory+"/"+server+"/daily/"
	if not os.path.exists(daily_dst):
		os.makedirs(daily_dst)
	inc_file = open(include_file, 'r')
	for inc_line in inc_file:
		line = inc_line.rstrip()
		print "%s --exclude-from=%s %s@%s:%s %s" %(RSYNC, exclude_file, username, server, line, current)
		bkout.write("%s --exclude-from=%s %s@%s:%s %s\n" %(RSYNC, exclude_file, username, server, line, current))
		process = subprocess.Popen("%s --exclude-from=%s %s@%s:%s %s\n" %(RSYNC, exclude_file, username, server, line, current), shell=True, stdout=bkout, stderr=bkout)
		ret_code = process.wait()
	inc_file.close()
	bkout.flush()

# If backup is of type "local" then do a regular rsync.
def backup_local(server, directory, include_file, exclude_file, daily_log):
	print "Daily LOG:", daily_log
	bkout = open(daily_log, 'a', 0)
	bkout.write("Daily LOG: %s\n" %(daily_log))
	current = directory+"/"+server+"/daily/current"
	daily_dst = directory+"/"+server+"/daily/"
	if not os.path.exists(daily_dst):
		os.makedirs(daily_dst)
	inc_file = open(include_file, 'r')
	for inc_line in inc_file:
		line = inc_line.rstrip()
		print "%s --exclude-from=%s %s %s" %(RSYNC, exclude_file, line, current)
		bkout.write("%s --exclude-from=%s %s %s\n" %(RSYNC, exclude_file, line, current))
		process = subprocess.Popen("%s --exclude-from=%s %s %s\n" %(RSYNC, exclude_file, line, current), shell=True, stdout=bkout, stderr=bkout)
		ret_code = process.wait()
	inc_file.close()
	bkout.flush()

def hardcopy(src, dst):
	dest = abspath(dst)
	os.mkdir(dst)
	os.chdir(src)
	for root, dirs, files in os.walk('.'):
		curdst = join(dst, root)
		for d in dirs:
			os.mkdir(join(curdst, d))
		for f in files:
			fromfile = join(root, f)
			to = join(curdst, f)
			os.link(fromfile, to)

# Hardlink files from "current" directory to todays dated directory.
# Hardlinks here allow for incremental backups.
def copy_to_today(server, directory, exclude_file, daily_log):
	now = datetime.datetime.now()
	rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
	today = now.strftime("%Y-%m-%d")
	bkout = open(daily_log, 'a', 0)
	current = directory+"/"+server+"/daily/current"
	new_dst = directory+"/"+server+"/daily/"+today
	if os.path.exists(new_dst):
		shutil.rmtree(new_dst)
	if not os.path.exists(current):
		os.makedirs(current)
	# Start of adding support to remove an exclusion from "current" if it previously existed
	exc_file = open(exclude_file, 'r')
	if os.stat(exclude_file)[6] != 1:
		for exc_line in exc_file:
			line = exc_line.rstrip()
			delete_path = current+line
			if os.path.exists(delete_path):
				print "Delete path is: %s" %(delete_path)
				bkout.write("Delete path is: %s\n" %(delete_path))
			else:
				print "Exclusion path %s doesn't exist or is already removed." %(delete_path)
				bkout.write("Exclusion path %s doesn't exist or is already removed.\n" %(delete_path))
			rm_process = subprocess.Popen('rm -rf %s' %(delete_path), shell=True, stdout=bkout, stderr=bkout)
			ret_code_rm = rm_process.wait()
	exc_file.close()
	# End of adding support to remove an exclusion if it previously existed
	hardcopy(current, new_dst)
	print "*** BACKUPS FOR %s ENDED %s ***" %(server, rightnow)
	print "=== END OF BACKUPS FOR %s ===\n\n" %(server)
	bkout.write("*** BACKUPS FOR %s ENDED %s ***\n" %(server, rightnow))
	bkout.write("=== END OF BACKUPS FOR %s ===\n\n" %(server))
	bkout.flush()

def uniq(inlist): 
	# order preserving
	uniques = []
	for item in inlist:
		if item not in uniques:
			uniques.append(item)
	return uniques

def log_aggregator():
	now = datetime.datetime.now()
	rightnow = now.strftime("%Y-%m-%d@%H:%M:%S")
	log_dir_stack = []
	for section_name in parser.sections():
		if parser.has_option(section_name, 'log_dir'):
			log_dir = parser.get(section_name, 'log_dir')
			log_dir_stack.append(log_dir)
	log_dir_stack = uniq(log_dir_stack) # Re-Initialize log_dir_stack with unique entries.
	for log_dir in log_dir_stack:
		filestack = []
		backup_daily_master_log = open(log_dir + "/backup_daily_master_log_" + rightnow, 'a+')
		for log in os.listdir(log_dir):
			if fnmatch.fnmatch(log, 'backup_log_daily_*'):
				file = log_dir + "/" + log
				filestack.append(file)
		for filename in filestack:
			out = open(filename,'r')
			for line in out:
				backup_daily_master_log.write(line)
		backup_daily_master_log.close()

if __name__ == "__main__":
	parse_config()
	log_aggregator()
