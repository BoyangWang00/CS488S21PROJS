from socket import *
import sys
import os
import subprocess # For executing a shell command
import re

host = int(sys.argv[1])
#ping in flood mode with -f flag
response = os.system("ping -c 1 " + host)
