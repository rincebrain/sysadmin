#!/usr/bin/env python
import os,sys,string
try:
  import wmi
except:
  print "I need the wmi module to function correctly."
  sys.exit(-1)

def list_sites():
    c = wmi.WMI(namespace="MicrosoftIISv2")
    sites = c.IIsWebVirtualDirSetting()
    #print foo[0]
    src_dirs = []
    log_dirs = []
    path_map = {}
    for item in sites:
      src_dir = str(item.Path).strip().lower()# .replace("c:\\www\\","")
      log_dir = str(item.Name).strip().lower()

      if src_dir not in src_dirs:
        src_dirs.append(src_dir)
        path_map[src_dir] = log_dir
      if log_dir not in log_dirs:
        log_dirs.append(log_dir)
    
    src_dirs.sort()
    log_dirs.sort()
    
#    for entry in src_dirs:
#      print entry    
    #for item in sites:
    #  print item
    # pass
    return (src_dirs,log_dirs,path_map)

def map_site(src_path,src_dirs,path_map):
#  print src_path,os.getcwd()
  src_dirs_cleaned = []
  
  rel_path = False # relative directory naming
  
  for entry in src_dirs:
    if len(os.path.splitunc(entry)[0]) <> 0: # If we found a UNC path
      pass
    else:
      src_dirs_cleaned.append(entry)
  root_path = os.path.commonprefix(src_dirs_cleaned)
  if len(root_path) == 0:
    # We don't have a common root? Fascinating.
    # FIXME: I should assume relative path and give up here
    print "Help, I can't find the common webdir root! Write some intelligent code to fix this!"
    sys.exit(-1)

  if len(os.path.splitdrive(src_path)[0]) == 0 and len(os.path.splitunc(src_path)[0]) == 0: # relative path, go!
    rel_path = True
  
  abs_path = ""
  
  if rel_path:
    abs_path = os.path.join(os.getcwd(),src_path)
  else:
    abs_path = src_path
  
  app_path = abs_path
  sub_path = ""
#  print app_path
  
  tmp = None
  for item in path_map.keys():
    if "turbulence.pha.jhu.edu" in item:
      tmp = item
      break
  
#  tmp = os.path.normpath(os.path.normcase(tmp))
  app_path = os.path.normpath(os.path.normcase(app_path))
  
  while len(app_path) > 0:
        
#    if not app_path == "C:\\":
#      print "app_path in src_dirs_cleaned %s %d" % (app_path,app_path in path_map.keys())
#      print "app_path magic_key %s %s %d %d" % (app_path,tmp, app_path in src_dirs_cleaned, app_path == tmp)
#      sys.exit(-1)
    if app_path in src_dirs_cleaned: # If we found the matching application root
      app_path = path_map[app_path]
      break
    (car,cdr) = os.path.split(app_path)
    if len(car) == 0: # Something is horribly broken.
      break
    if len(cdr) == 0: # Trailing \
      #print app_path
      app_path = car
      continue
    sub_path = os.path.join(cdr,sub_path)
    app_path = car
  return os.path.normpath(os.path.normcase(os.path.join(app_path,sub_path))).replace("\\","/")

def list_net(is_64):
  fwdir = "Framework"
  if (is_64):
    fwdir += "64"
  netdir = os.path.join(os.environ["WINDIR"],"Microsoft.NET",fwdir)
  entries = os.listdir(netdir)
  cleaned_entries = []
  for entry in entries:
    if str.strip(entry)[0] == "v" and str.strip(entry)[1] in string.digits:
      cleaned_entries.append(str.strip(entry))
      
#  for entry in cleaned_entries:
#    print entry[1:]
  # pass
  return cleaned_entries

    

def __main__():
  try:
    import optparse
  except:
    print "I need the optparse module to work interactively."
    return -1
  optp = optparse.OptionParser(usage="usage: %prog [options] site")
  optp.add_option("--list",dest="list_net",action="store_true",default=False,help="List the .NET versions installed")
  optp.add_option("--list-sites",dest="list_sites",action="store_true",default=False,help="List the sites configured in IIS")
  optp.add_option("-N","--net-version",dest="net_vers",help="Version of .NET to configure the site to use")
  optp.add_option("--64-bit",dest="b64",action="store_true",default=False,help="Use 64-bit .NET versions (default:32-bit)")
#  optp.add_option("--raw",dest="raw_net",action="store_true",default=False,help="Interpret the .NET version as a raw string, rather than looking up versions in a table.")
  optp.add_option("-f","--force",dest="force",action="store_true",default=False,help="Overrides all sanity checks on options and just runs. (DANGEROUS!)")
  optp.add_option("-R","--raw-options",dest="RAW",help="Passes the options you give as an argument to this straight through to aspnet_regiis. (DANGEROUS!)")
  optp.add_option("--run",dest="run",action="store_true",default=False,help="Actually run the aspnet_regiis we generate (!)")
  optp.add_option("-r",dest="recurse",action="store_true",default=False,help="Change ASP.NET version recursively at location specified (DANGEROUS!)")

  (options, args) = optp.parse_args()

  c = wmi.WMI(namespace="MicrosoftIISv2")
  net_versions = list_net(options.b64)
  if (options.list_net):
    for entry in net_versions:
      print entry
    return 0
  if (options.list_sites):
    sites = list_sites()[0]
    for entry in sites:
      print entry
    return 0

  if len(args) == 0:
    optp.print_help()
    return 0

  requested_net_version = str(options.net_vers).strip()
  net_re = re.compile("^%s(.*)$" % requested_net_version)
  
  net_results = []
  for possible in net_versions:
    if net_re.match(possible):
      net_results.append(possible)
  if len(net_results) == 0:
    print ".NET version \"%s\" does not match any available on the system!" % requested_net_version
    return -1
  if len(net_results) > 1:
    print ".NET version \"%s\" matches more than one version on the system!" % requested_net_version
    return -1
  net_version = net_results[0]

  (site_paths,site_logical_paths,path_map) = list_sites()
  
  # map ambiguous site path to canonical site in our knowledge
  canonical_site = map_site(str(args[0]).strip(),site_paths,path_map)

  # generate template command
  aspnet_cmd = os.path.join(os.environ["WINDIR"],"Microsoft.NET",net_version,"aspnet_regiis.exe")
  
  # add raw options
  if optp.RAW and len(optp.RAW) > 0:
    for item in optp.RAW:
      aspnet_cmd += " %s " % item
  
  if options.recurse:
    aspnet_cmd += " -ir "
  else:
    aspnet_cmd += " -i "
  
  aspnet_cmd += " %s" % canonical_site
  
  print aspnet_cmd
  
  if (options.run):
    print "I don't trust myself enough to actually run this yet!"
    

  #for item in sites:
  #  print "%s => %s" % (str(item.Path).strip().lower().replace("c:\\www\\",""),item.Name)
  #print q[0].path

  #for item in sites:
  #  print item

if __name__ == "__main__":
  __main__()

