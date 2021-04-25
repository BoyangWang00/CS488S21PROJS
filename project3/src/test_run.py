
#! /usr/bin/env python3
import subprocess
from os import path
import os

HERE = path.abspath(path.dirname(__file__))

#test1 append change to the end of file

child1 = subprocess.Popen(["python3", "server.py", "50005"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50005", "download", "./test/1/NEW", "./test/1/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/1/NEW", "./test/1/OLD"], cwd = HERE, check = True)

#test2 insert multiple new lines in the beginning/middle/end of the file

child1 = subprocess.Popen(["python3", "server.py", "50002"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50002", "download", "./test/2/NEW", "./test/2/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/2/NEW", "./test/2/OLD"], cwd = HERE, check = True)

#include a not-finished temp_log in the directory and download process should resume based on temp_log

child1 = subprocess.Popen(["python3", "server.py", "50003"],cwd = HERE)

#set the environment variable for client.py process and client code will check len(shopping_list) < (len(server_file)-len(client_file))

os.environ['CHECK_SHOPPING_LIST_SHOULD_BE_SHORT'] = '1'

subprocess.run(["python3", "client.py", '', "50003", "download", "./test/3/NEW", "./test/3/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/3/NEW", "./test/3/OLD"], cwd = HERE, check = True)

assert (not path.exists("./test/3/OLDTEMP_LOG"))



child1 = subprocess.Popen(["python3", "server.py", "50004"],cwd = HERE)

del os.environ['CHECK_SHOPPING_LIST_SHOULD_BE_SHORT']

subprocess.run(["python3", "client.py", '', "50004", "download", "./test/4/NEW", "./test/4/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/4/NEW", "./test/4/OLD"], cwd = HERE, check = True)

subprocess.run(["rm", "-r", "./test"], cwd = HERE, check = True)

subprocess.run(["cp", "-r", "./test_reset", "./test"], cwd = HERE, check = True)