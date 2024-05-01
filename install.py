#!/bin/env python3

import os, sys, shutil

if sys.platfort.find("linux") == -1:
	print("Vi Software Manager designed only for linux, sorry")
	sys.exit(1)

shutil.copytree(os.getcwd(), os.path.expanduser("~/.software"))

with open(os.path.expanduser("~/.bashrc"), "at") as f:
	f.write("export PATH=\"$HOME/.software/bin:$PATH\"\nexport SW=\"$HOME/.software\"")

os.system("source ~/.bashrc")

print("Done, you can delete this directory")
