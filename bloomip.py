#!/usr/bin/env python2

import sys,os,re

from stat import *
import socket

match_line = "^(?P<datetime>.+) rio\-grande dhcpd\: \[ID 702911 local1\.([a-z]+)\] (?P<message>.+)$"
line_re = re.compile(match_line)
ip_re = re.compile("(?P<IPaddr>128\.220\.233\.[0-9]+)")
line_rep_re = re.compile(".*last message repeated.*")

dhcpd_logdir = "/ssd/dhcpd_logs/"

dirlist = os.listdir(dhcpd_logdir)

used_ips = {}

for file in dirlist:
  if not S_ISREG(os.stat(os.path.join(dhcpd_logdir,file)).st_mode):
    continue
  lines = open(os.path.join(dhcpd_logdir,file)).readlines()
  for line in lines:
    if not line_re.match(line):
      if not line_rep_re.match(line):
        print "Unknown type of line: %s" % line
      continue
    data = line_re.match(line)
    time = data.group("datetime")
    msg = data.group("message")
    ips_in_line = ip_re.findall(msg)
    for ip in ips_in_line:
      if not ip in used_ips.keys():
        used_ips[ip] = [time]
      else:
        used_ips[ip].append(time)

for ip in xrange(1,254):
  testip = "128.220.233.%d" % ip
  if not testip in used_ips.keys():
    hn = ""
    try:
      hn = socket.gethostbyaddr(testip)[0]
    except:
      hn = "UNKNOWN HOSTNAME"
    print "%s (%s) available" % (testip,hn)


# for log in logdir
  # for line in lines:
    # read line
    # extract all IPs in 233 from _message_
    # update hashmap with IP and date of DHCP entry [append to list of entries if necessary]

# for host in xrange(1,254):
#   if not host in hashmap.keys()
#   print host
#
# possibly cleverer logic for all entries older than [epsilon]