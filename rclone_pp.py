#!/usr/bin/env python3

################################################################################
### NZBGET POST-PROCESSING SCRIPT                                            ###
################################################################################

# Rclone move script by ssnjr.
#
# Uploads successful downloads to your gdrive.

################################################################################
### NZBGET POST-PROCESSING SCRIPT                                            ###
################################################################################

import os
import sys
import subprocess
from xmlrpc.client import ServerProxy

# NZBGET rpc ctrl creds:
host = os.environ.get("NZBOP_CONTROLIP")
port = os.environ.get("NZBOP_CONTROLPORT")
username = os.environ.get("NZBOP_CONTROLUSERNAME")
password = os.environ.get("NZBOP_CONTROLPASSWORD")
# Downloaded NZB name:
down_nzb_name = os.environ.get("NZBPP_NZBNAME")
# Post processed NZB upload directory:
upload_dir = os.environ.get("UPLOAD_DIR")
# Gives downloaded file directory without the trailing '/':
nzb_down_dir = os.environ.get("NZBPP_DIRECTORY")
# Checks download status:
status = os.environ.get("NZBPP_TOTALSTATUS")
# Uses rclone listremote to list availabe remotes and chooses the first one:
remote_name = str(
    subprocess.check_output("rclone listremotes", shell=True).decode("UTF-8")
).splitlines()[0]

if host == "0.0.0.0":
    host = "127.0.0.1"

# Build an URL for XML-RPC requests:
rpcUrl = f"http://{username}:{password}@{host}:{port}/xmlrpc"
# Create remote server object:
server = ServerProxy(rpcUrl)

# Function for running rclone cmds with live output to logs:
def rclone(command):
    with subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    ) as proc:
        while True:
            output = proc.stdout.readline().decode("UTF-8").strip()
            if output != "":
                server.writelog("INFO", output)
            if output == "" and proc.poll() is not None:
                server.writelog(
                    "INFO",
                    f'"{down_nzb_name}" has been uploaded to '
                    + f'"{remote_name}" sucessfully!',
                )
                break


nzb_upload_dir = f"{remote_name}/{upload_dir}/{down_nzb_name}"

rclone(
    f'rclone move "{nzb_down_dir}" "{nzb_upload_dir}" '
    + "-v --stats=1s --stats-one-line"
)
sys.exit(93)
