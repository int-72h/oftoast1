#!/usr/bin/env python3

from tvn import *
import argparse
import os
from subprocess import Popen,PIPE


from pathlib import Path
from sys import exit, stderr
import httpx

parser = argparse.ArgumentParser(description="Manage Open Fortress installation.")
parser.add_argument("action", type=str, help='action to execute on a directory, currently only "upgrade"')
parser.add_argument("directory", type=str, help='a directory to install it to.')
parser.add_argument("-u", default="https://toast.openfortress.fun/toast/", help="url to fetch data from")
parser.add_argument("-c", default="4", help="no. of threads")
args = parser.parse_args()

if args.action != "upgrade":
    print("invalid action", file=stderr)
    exit(1)

game_path = Path(args.directory)


user_agent = 'murse/0.0.2'

url = args.u
response = httpx.get(url, headers={'user-agent': 'murse/0.0.2'}, follow_redirects=True)
resUrl = response.url
url = "https://" + resUrl.host + "/toast/"
print("Server Selected: " + url)
num_threads = httpx.get(url + "/reithreads", headers={'user-agent': user_agent}, follow_redirects=True).text
latest_revision = fetch_latest_revision(url)
installed_revision = get_installed_revision(game_path)

print(installed_revision, "->", latest_revision, file=stderr)

revisions = fetch_revisions(url, installed_revision, latest_revision)
changes = replay_changes(revisions)



writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))


try:
    os.remove(game_path / ".revision")
except FileNotFoundError:
    pass

for x in list(filter(lambda x: x["type"] == TYPE_DELETE, changes)):
    print("DEL", x["path"])
    try:
        os.remove(game_path / x["path"])
    except FileNotFoundError:
        pass

for x in list(filter(lambda x: x["type"] == TYPE_MKDIR, changes)):
    print("MKDIR", x["path"])
    try:
        os.remove(game_path / x["path"])
    except FileNotFoundError:
        pass
    os.makedirs(game_path / x["path"], mode=0o777, exist_ok=True)
todl = open('todl.txt','w')
for x in writes:
    if x["type"] == TYPE_WRITE:
        todl.write('{}\n out={}\n checksum=md5={}\n'.format(url+"objects/"+x["object"], game_path / str(x["path"]), x["hash"]))
todl.close()
fp = Popen('aria2c -i todl.txt -d . -x 12 -j 100 -m 10 -V -U murse/0.0.2', shell=True,stdin=PIPE, stdout=PIPE, universal_newlines=True)
for line in fp.stdout:
    print(line)

(game_path / ".revision").touch(0o777)
(game_path / ".revision").write_text(str(latest_revision))
