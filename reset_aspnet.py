#!/usr/bin/env python
import os,sys,string
try:
  import wmi
except:
  print "I need the wmi module to function correctly."
  sys.exit(-1)

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
  optp.add_option("-f","--force",dest="force",action="store_true",default=False,help="Overrides all sanity checks on options and just runs. (DANGEROUS)")
  optp.add_option("-R","--raw-options",dest="RAW",help="Passes the options you give as an argument to this straight through to aspnet_regiis. (DANGEROUS)")
  optp.add_option("--run",dest="run",action="store_true",help="Actually run the aspnet_regiis we generate (!)")

  (options, args) = optp.parse_args()

  c = wmi.WMI(namespace="MicrosoftIISv2")
  if (options.list_net):
    fwdir = "Framework"
    if (options.b64):
      fwdir += "64"
    netdir = os.path.join(os.environ["WINDIR"],"Microsoft.NET",fwdir)
    entries = os.listdir(netdir)
    cleaned_entries = []
    for entry in entries:
      if str.strip(entry)[0] == "v" and str.strip(entry)[1] in string.digits:
        cleaned_entries.append(str.strip(entry))
        
    for entry in cleaned_entries:
      print entry[1:]
    # pass
    return 0
  if (options.list_sites):
    # pass
    return 0

  if len(args) == 0:
    optp.print_help()
    return 0
  
  

  sites = c.IISWebVirtualDirSetting()

  #for item in sites:
  #  print "%s => %s" % (str(item.Path).strip().lower().replace("c:\\www\\",""),item.Name)
  #print q[0].path

  #for item in sites:
  #  print item

if __name__ == "__main__":
  __main__()

