rabia-backups
=============

Dedicated to my lovely, kind hearted and beautiful wife Rabia. With this package you can create daily, weekly, monthly and yearly backups which are either incremental, full or mixed in nature.

### HOW T0

This "How To" describes a complete account of how "Rabia Backups" should be used along with a use case scenario.
The backups use a "pull" mechanism. Hence the scripts need to run only on the target machine to which backups need to be saved.
The target and source machines only needs the "rsync" installed.
This also implies that the public SSH keys from the target machine need to be copied over to the source machine.
It is recommended to backup as the "root" user as it is the only user that can backup files outside of the source users home directory.
If for example you wish to backup the /etc directory then no other user than the root user will most likely be in that privileged position. For security purposes only the root user from the target machine should be allowed access to the source machine by changing the following in /etc/ssh/sshd_config of the source machine:
	
	PermitRootLogin yes
	AllowUsers root@<target-machine>
	
Edit the backup-config but not before making a backup copy of it. The configuration file has enough comments to help you with your own custom setup.
###### Field1: State whether the backup is either "local" or "remote" these are keywords.

######	Field2: IP address or FQDN of the source machine.

######	Field3: Directories to include (NO spaces between commas)

######	Filed4: Directories to exclude (NO spaces between commas). DO NOT place a forward slash at the beginning of the each of the excluded directories.

######	Field5:	Retention days. These are the number of days after which you want the oldest backups to be removed.

######	Field6 (Optional): Overriding backup/destination directory. Make sure this directory exists and that the overriding user (if any) specified by Field7 can write to this directory. Default location specified in "backup-headers" as "BACKUP_TARGET". You will most likely want to change this here or in the backup-headers file.

######	Field7 (Optional): Overriding backup user. If NOT using the "root" account, specify account/user name here. Else leave blank.

######	Field8 (Optional): Depending on which script combinations you wish to use this defaults to daily incremental backups. See backup-config for more examples. Several options are available here.

######	Field9 (Optional): List of non-super-admin email accounts. These are email addresses that only receive part of the log file for particular backups. In the event that you want to backup up multiple source machines this setting is useful. Lets say you want emails for source1.example.com to go to admin1@example.com and emails for source2.example.com to go to admin2@example.com then these can be set here. Each souce machine can have multiple email accounts specified as well. The super admin email account(s) which is specified in backup-headers as "ADMIN_EMAILS" should be changed as well. These super admin emails receive full backup logs and metrics of all machines unlike the non-super-admin emails specified in this field i.e. Field9.
Multiple email addresses must be specified with a space beween commas e.g. admin1@example.com, admin2@example.com (WITH spaces between commas)

Make sure that the appropriate SSH public keys are copied over to source machine without a password. It is quite likely that you will have to manually do this step the first time by agreeing to add the public key of the source machine to the targets user's .ssh/known_hosts file when prompted.

Example Scenario 1:
	Lets say you want to do all backups as the "root" user on the target machine then the root account's public ssh key (without a password) should be copied over to the source machine's root account. This key must be added under .ssh/authorized_keys of the "root" account on the source machine.

	Target machine name: target.example.com
	Source machine name: source.example.com

In this example scenario we want to backup a Debian server. The following need to be backed up: /etc/apache2 and /etc/php5, however we want to exclude the following sub-directories from /etc/apache2 i.e. /etc/apache2/mods-available and /etc/apache2/sites-available. Lets further assume that we want to only keep backups for 7days, which is to say that we only want 7 daily backups at any point in time. We want to save these backups in a directory "/backups". Once the backups have successfully completed we want to send out non-super-admin emails to admin1@example.com and admin2@example.com and send super-admin emails specified by "ADMIN_EMAILS"
in backup-headers file.

Edit backup-headers. This configuration holds all the important default variables. Please ALWAYS edit the following variables.
```
		BIN=$HOME 	# Parent directory for all "backup scripts" and "backup-config".
		BACKUP_DAILY=$BIN/backup-daily # Executable for daily backups.
		BACKUP_WEEKLY=$BIN/backup-weekly # Executable for weekly backups.
		BACKUP_MONTHLY=$BIN/backup-monthly # Executable for monthly backups.
		BACKUP_YEARLY=$BIN/backup-yearly # Executable for yearly backups.
		BACKUP_CONFIG=$BIN/backup-config # Location of configuration file.
		BACKUP_TARGET=/tmp # Parent destination where all backups will be stored. Must be changed to meet your criteria.
		LOG_DIR=/tmp/backup-logs # Location of log files.
		DISK_SPACE_ALERT=90 # Backups are aborted if this disk space threshold is reached.
		BACKUP_USER="root" # Default remote and local backup user. This user can be overridden in the config file.
		ADMIN_EMAILS="super-admin1@example.com, super-admin2@example.com"
```

In our example scenario our single line in "backup-config" will look like this:
```
	remote:source.example.com:/etc/apache2,/etc/php5:etc/apache2/mods-available,etc/apache2/sites-available:7:/backups:::admin1@example.com, admin2@example.com
```

In our example scenario our "backup-headers" file will look like this:
```
		BIN=/root   # Parent directory for all "backup scripts" and "backup-config". Assuming this is where all the scripts reside.
        BACKUP_DAILY=$BIN/backup-daily # Executable for daily backups.
        BACKUP_WEEKLY=$BIN/backup-weekly # Executable for weekly backups.
        BACKUP_MONTHLY=$BIN/backup-monthly # Executable for monthly backups.
        BACKUP_YEARLY=$BIN/backup-yearly # Executable for yearly backups.
        BACKUP_CONFIG=$BIN/backup-config # Location of configuration file.
        BACKUP_TARGET=/tmp # Parent destination where all backups will be stored. Must be changed to meet your criteria.
        LOG_DIR=/tmp/backup-logs # Location of log files.
        DISK_SPACE_ALERT=90 # Backups are aborted if this disk space threshold is reached.
        BACKUP_USER="root" # Default remote and local backup user. This user can be overridden in the config file.
        ADMIN_EMAILS="super-admin1@example.com, super-admin2@example.com"
```

Finally add the following to the root accounts crontab:
```
	1 2 * * * cd /root/backup-scripts && ./run-backup-daily # Run daily backups at 2:01 am every morning
```

Example Scenario 2:
	Lets say you want to do all backups as the account "tom" on the target machine and you wish to backup the account "stacy" who wants her home directory backed up then the "tom" account's public ssh key (without a password) should be copied over to the source machine's "stacy" account. This key must be added under .ssh/authorized_keys of the "stacy" account on the source machine.

	Target machine name: target.example.com
	Source machine name: source.example.com

In this example scenario we want to backup a remote users (stacy's) home directory. The following need to be backed up: /home/stacy, however we want to exclude the following sub-directories from /home/stacy i.e. /home/stacy/scratch. Lets further assume that we want to only keep 10 weekly incremental backups which are performed every Sunday and 12 full monthly backups to be performed on the first of every month. We want to save these backups in a directory "/backups". Once the backups have successfully completed we want to send out non-super-admin emails to stacy@example.com to notify her if her backups were successful and send super-admin emails specified by "ADMIN_EMAILS" in backup-headers file.

In our example scenario our "backup-config" will look like this:
```
	remote:source.example.com:/home/stacy:home/stacy/scratch:10:/backups:tom:weekly-incremental-sunday:stacy@example.com
	remote:source.example.com:/home/stacy:home/stacy/scratch:10:/backups:tom:monthly-full-1:stacy@example.com
```

In our example scenario our "backup-headers" file will look like this:
```
		BIN=/root   # Parent directory for all "backup scripts" and "backup-config". Assuming this is where all the scripts reside.
        BACKUP_DAILY=$BIN/backup-daily # Executable for daily backups.
        BACKUP_WEEKLY=$BIN/backup-weekly # Executable for weekly backups.
        BACKUP_MONTHLY=$BIN/backup-monthly # Executable for monthly backups.
        BACKUP_YEARLY=$BIN/backup-yearly # Executable for yearly backups.
        BACKUP_CONFIG=$BIN/backup-config # Location of configuration file.
        BACKUP_TARGET=/tmp # Parent destination where all backups will be stored. Must be changed to meet your criteria.
        LOG_DIR=/tmp/backup-logs # Location of log files.
        DISK_SPACE_ALERT=90 # Backups are aborted if this disk space threshold is reached.
        BACKUP_USER="root" # Default remote and local backup user. This user can be overridden in the config file.
        ADMIN_EMAILS="super-admin1@example.com, super-admin2@example.com"
```

Finally add the following to the "tom" accounts crontab:
	1 2 * * * cd /root/backup-scripts && ./run-backup-weekly # Run weekly backups at 2:01 am every morning
	1 4 * * * cd /root/backup-scripts && ./run-backup-monthly # Run monthly backups at 4:01 am every morning


The following holds true for any type of backup or backup schedule:
	If you anticipate that all backups from every source machine will reside in the same directory eveytime then you can change the `BACKUP_TARGET=/tmp` in backup-headers to point to that location and instead leave Field6 blank in the backup-config file. 

	For example:
	If you anticipate that all backups from every source machine will reside in the /backups directory eveytime then you can change the "BACKUP_TARGET=/tmp" in backup-headers to "BACKUP_TARGET=/backups" and instead leave Field6 (Overriding backup location) blank in the backup-config file.
