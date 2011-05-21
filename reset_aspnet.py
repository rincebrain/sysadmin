#!/usr/bin/env python
import os,sys,wmi

c = wmi.WMI(namespace="MicrosoftIISv2")

sites = c.IISWebVirtualDirSetting()

for item in sites:
  print "%s => %s" % (str(item.Path).strip().lower().replace("c:\\www\\",""),item.Name)
#print q[0].path

#for item in sites:
#  print item
