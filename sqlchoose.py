#!/usr/bin/env python

# Script to calculate pseudorandom trigger of backups
# per-database, to try and distribute the load of
# full backups

__author__   = "Rich Ercolani, rercola@acm.jhu.edu"
__version__  = "0.0.1"


import sys,os,random,socket,time,re

# maximum time between full backups
MAX_DAYS = 90

"""Arbitrary time in the past greater than 90 days,
guaranteed to trigger a full backup."""
MAGIC_TIME = 900000000

TDPSQL="C:\\Program Files\\Tivoli\\TSM\\TDPSql\\TDPSQLc.exe"

"""The special-cased databases which always get full backups.
"""
SPECIAL_CASES=["master"]

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

"""A command to extract the bits you care about from
a TDPSQLC query SQL * command and hand them back as a list.
Looks like
[[hostname],
[db_name,db_space_alloc,db_space_used,db_log_alloc,db_log_used,db_options],
[db_name,db_space_alloc,db_space_used,db_log_alloc,db_log_used,db_options],
...]"""
def parse_tdpsql_dbs(lines):
    # Whee, state machine time
    _tmpdb = {}
    dbs = []
    extractor = re.compile("^(?P<key>.+) (\.+) (?P<value>.+)$")
    kv_map = {"SQL Database Name":"db_name","SQL Database Data Space Allocated":"db_space_alloc","SQL Database Data Space Used":"db_space_used","SQL Database Log Space Allocated":"db_log_alloc","SQL Database Log Space Used":"db_log_used","SQL Database Options":"db_options"}
    
    for line in lines:
      line = str.strip(line)
      if len(line) == 0:
        if len(_tmpdb.keys()) != 0:
          dbs.append(_tmpdb)
          _tmpdb = {}
      found = extractor.match(line)
      if found is not None:      
        _k = str.strip(found.group("key"))
        _v = str.strip(found.group("value"))
#        print "(%s,%s)" % (_k,_v)
        if _k == "SQL Server Name":
          dbs.append([_v])
          continue
        if _k in kv_map.keys():
          # If we see this, we're on a new DB, append the old one if any
          if kv_map[_k] == "db_name" and len(_tmpdb.keys()) != 0:
            dbs.append(_tmpdb)
            _tmpdb = {}
          _tmpdb[kv_map[_k]] = _v
          continue
        print "(%s,%s)" % (_k,_v)
        #sys.exit(-1)
      else:
        #print "Not Match: %s" %line
        continue
    if len(_tmpdb.keys()) != 0:
      dbs.append(_tmpdb)
      _tmpdb = {}
    return dbs

def get_dblist(host):
  #print "Bees"
  # Ignore host for now, setting up for next version
  # system(tdpsql query sql *)
  # parse
  # strip periods and spaces from left hand side, split to k-v
  # return list of [[db_name,db_space_alloc,db_space_used,db_log_alloc,db_log_used,db_options],...]
  #try:
    foo = os.path.dirname(TDPSQL)
    #print foo
    os.chdir(foo)
    _tmp = os.popen3("\"%s\" query SQL *" % TDPSQL)[1].readlines()
    
    return parse_tdpsql_dbs(_tmp)[1:]
          
    
  #except:
  #  raise RuntimeError("Unable to query SQL databases on host!")

# get last time of update for a db on a host
# returns number of days
def get_last_update(host,db_name):
  # Ignore host variable for now, setting up for next version
  # Should be a single query against the SQL DB on the client
  return -1

def get_last_updates(host):
  dbs = get_dblist(host)
  last_update = {}
  for db in dbs:
    if db in last_update.keys:
      # fail
      print "DB %s found already in last_update list!" % db["db_name"]
    last_update[db] = get_last_update(host,db["db_name"])
  return last_update

def do_full_update(dbname,host=""):
  print "Full update on DB %s on host %s" % (dbname,host)
  pass

def do_inc_update(dbname,host=""):
  print "Inc update on DB %s on host %s" % (dbname,host)
  pass

def main():
  inc_update = []
  full_update = []
  # Not going to be used outside of logging...yet.
  host = socket.gethostname()
  # 
  sql_server = sqlhost(host)
  
  #touch SQLPATH or die()
  rand = random.Random()
  rand.seed()
  dbs = get_dblist(host)
  for db in dbs:
     db_name = db["db_name"]
     # special case master
     #if db_name in special_cases:
       #full_update.append(db_name)
      # continue
     last_updated = get_last_update(host,db_name)
     # If never backed up
     if last_updated == -1:
       full_update.append(db_name)
     else:
       # Weighting
       # Just naive 
       p_mass = (double(last_updated)/(MAX_DAYS))**2.0
       rand_num = rand.randint(0,MAX_DAYS+1)
       # If our random number is within the range of [0,p_mass],
       # we do a full backup - otherwise, incremental.
       if (p_mass >= rand_num):
         full_update.append(db_name)
       else:
         if db_name not in special_cases:
           inc_update.append(db_name)
  for db in full_update:
    do_full_update(dbname=db,host=host)
  for db in inc_update:
    do_inc_update(dbname=db,host=host)
  # call the full update script with the list of fulls
  # call the incremental update script with the list of incrementals

if __name__ == "__main__":
  main()
