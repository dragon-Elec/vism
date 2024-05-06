#!/bin/env python3

import os, sys, shutil

if sys.platfort.find("linux") == -1:
	print("Vi Software Manager designed only for linux, sorry")
	sys.exit(1)

if os.getuid():
	print("Run me as root!")

shutil.copytree(os.getcwd(), os.path.expanduser("~/.software"))

for file in os.listdir(os.path.expanduser("~/.software/bin")):
	os.system(f"ln -s {os.path.expanduser('~/.software/bin/'+file} /usr/bin/{file}")

print("Done, you can delete this directory")
