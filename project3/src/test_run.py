
#! /usr/bin/env python3
import subprocess
from os import path

HERE = path.abspath(path.dirname(__file__))

child1 = subprocess.Popen(["python3", "server.py", "50005"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50005", "download", "./test/1/NEW", "./test/1/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/1/NEW", "./test/1/OLD"], cwd = HERE, check = True)


child1 = subprocess.Popen(["python3", "server.py", "50002"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50002", "download", "./test/2/NEW", "./test/2/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/2/NEW", "./test/2/OLD"], cwd = HERE, check = True)


child1 = subprocess.Popen(["python3", "server.py", "50003"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50003", "download", "./test/3/NEW", "./test/3/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/3/NEW", "./test/3/OLD"], cwd = HERE, check = True)

assert (not path.exists("./test/3/OLDTEMP_LOG"))



child1 = subprocess.Popen(["python3", "server.py", "50004"],cwd = HERE)

subprocess.run(["python3", "client.py", '', "50004", "download", "./test/4/NEW", "./test/4/OLD"],cwd = HERE, check=True)

assert child1.wait() == 0

subprocess.run(["diff", "./test/4/NEW", "./test/4/OLD"], cwd = HERE, check = True)

subprocess.run(["rm", "-r", "./test"], cwd = HERE, check = True)

subprocess.run(["cp", "-r", "./test_reset", "./test"], cwd = HERE, check = True)