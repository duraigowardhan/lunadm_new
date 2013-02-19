import paramiko
import os
import sys

hostname = "10.72.201.72"
port = 22
username = "root"
password = ""

conn = paramiko.SSHClient()

try:
        __hostKeyFile = os.path.expanduser("~/.ssh/known_hosts")
except IOError:
        try:
                __hostKeyFile = os.path.expanduser("~/ssh/known_hosts")
        except IOError:
                log.err("Unable to open host keys file")

x = conn.get_host_keys()
if x == {}:
        conn.load_host_keys(__hostKeyFile)
        
conn.connect(hostname, port, username, password)

stdin, stdout, stderr = conn.exec_command("lun show all")

sys.stdout.write(stdout.read())