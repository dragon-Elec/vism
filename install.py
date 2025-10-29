#!/bin/env python3

import os, sys, shutil

if sys.platform.find("linux") == -1:
    print("Vi Software Manager designed only for linux, sorry")
    sys.exit(1)

if os.getuid():
    print("Run me as root!")
    sys.exit(1)

shutil.copytree(os.getcwd(), os.path.expanduser("~/.software"), dirs_exist_ok=True)

for file in os.listdir(os.path.expanduser("~/.software/bin")):
    os.system(
        f"ln -s {os.path.expanduser('~/.software/bin/' + file)} /usr/local/bin/{file}"
    )

print("Done, you can delete this directory")
