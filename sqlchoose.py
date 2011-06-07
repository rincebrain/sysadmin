#!/usr/bin/env python

# Script to calculate pseudorandom trigger of backups
# per-database, to try and distribute the load of
# full backups

__author__   = "Rich Ercolani, rercola@acm.jhu.edu"
__version__  = "0.0.1"


import sys,os,random,socket,time

# maximum time between full backups
MAX_DAYS = 90

"""Arbitrary time in the past greater than 90 days,
guaranteed to trigger a full backup."""
MAGIC_TIME = 900000000

class sqldb:
  """A SQL database.
  
  They have a host, a name, when they were added to the
  backup schedule, when they were last backed up,
  when they were last given a full backup, and whether
  they still exist."""
  def __init__(self,name,host,last=None,deleted=False):
    self.name = name
    if (last is None):
      last = time.gmtime(MAGIC_TIME)
    self.last_backup = last
    self.last_full = last
    self.host = host
    self.deleted = deleted
  
  def __repr__(self):
    return "%s.%s" % (self.host,self.name)
    

class sqlhost(object):
  """A SQL host which requires backing up.
  
  Hosts have a list of databases associated with them,
  along with when we first saw that DB and when it was
  last fully backed up.
  
  Any new databases should automatically be thrown into
  the full backup queue for the day."""

  def __init__(self,hostname,dbs=None):
    if dbs is None:
      dbs = get_dblist(hostname)
    self.dbs = dbs
    self.hostname = hostname
  
  def backup_host(self):
    # Is there any point in keeping permanent state?
    # After all, if we're just queuing backups on
    # TSM, we'll be reliant on it knowing when
    # we last backed up anyway...
    self._dbstatus = get_last_updates(self.hostname)
    # for db in db update list

  def __repr__(self):
    return self.hostname

def get_dblist(host):
  # Ignore host for now, setting up for next version
  # system(tdpsql query sql * parse)
  # strip periods and spaces from left hand side, split to k-v
  # return list of [[db_name,db_space_alloc,db_space_used,db_log_alloc,db_log_used,db_options],...]
  pass

# get last time of update for a db on a host
def get_last_update(host,db_name):
  # Ignore host variable for now, setting up for next version
  # Should be a single query against the SQL DB on the client
  pass

def get_last_updates(host):
  dbs = get_dblist(host)
  last_update = {}
  for db in dbs:
    if db in last_update.keys:
      # fail
      print "DB %s found already in last_update list!" % db["db_name"]
    last_update[db] = get_last_update(host,db["db_name"])
  return last_update

def main():
  inc_update = []
  full_update = []
  # Not going to be used outside of logging...yet.
  host = socket.gethostname()
  # 
  sql_server = sqlhost(host)
  # cd %PROGDIR%\tivoli\tsm\tdpsql or die()
  # rand = new Random()
  # rand.seed()
  # dbs = get_dblist()
  # for db in dbs:
  #   db_name = db["db_name"]
  #   # special case master
  #   if db_name is "master":
  #     full_update.append(db_name)
  #	continue
  #   last_updated = get_last_update(db_name)
  #   # If never backed up
  #   if last_updated == -1:
  #	full_update.append(db_name)
  #   else:
  #	# Weighting
  #	p_mass = last_updated**2
  #	rand_num = rand.randint(0,MAX_DAYS+1)**2
  #	# If our random number is within the range of [0,p_mass],
  #	# we do a full backup - otherwise, incremental.
  #	if (p_mass >= rand_num):
  #	   full_update.append(db_name)
  #	else:
  #	   inc_update.append(db_name)
  # call the full update script with the list of fulls
  # call the incremental update script with the list of incrementals
  pass

if __name__ is "__main__":
  main()