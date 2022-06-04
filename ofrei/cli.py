#!/usr/bin/env python3

from tvn import *
import argparse
import os

from concurrent.futures import ThreadPoolExecutor, as_completed
#from ofrei.steam import *
from pathlib import Path
from sys import exit, stderr
from shutil import copy,rmtree
import httpx

parser = argparse.ArgumentParser(description="Manage Open Fortress installation.")
parser.add_argument("action", type=str, help='action to execute on a directory, currently only "upgrade"')
parser.add_argument("directory", type=str, help='a directory to install it to.')
parser.add_argument("-u", default="http://toast.openfortress.fun/toast/", help="url to fetch data from")
parser.add_argument("-c", default="4", help="no. of threads")
args = parser.parse_args()

if args.action != "upgrade":
    print("invalid action", file=stderr)
    exit(1)

game_path = Path(args.directory)

installed_revision = get_installed_revision(game_path)
latest_revision = fetch_latest_revision(args.u)

print(installed_revision, "->", latest_revision, file=stderr)

revisions = fetch_revisions(args.u, installed_revision, latest_revision)
changes = replay_changes(revisions)



writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))
executor = ThreadPoolExecutor(int(args.c))


def work(x):
    with httpx.Client(http2=True, headers={'user-agent': 'Mozilla/5.0', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0'}) as client:
        resp = client.get(args.u + "/objects/" + x["object"])
        file = open(game_path / x["object"], "wb+")
        file.write(resp.content)
        file.close()


#futures = {executor.submit(work, x): x for x in writes}
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
futures = {}
for x in writes:
    if x["type"] == TYPE_WRITE:
        futures[executor.submit(work, x)] = x
for x in as_completed(futures):
    print('WRITE ' + futures[x]["path"])
(game_path / ".revision").touch(0o777)
(game_path / ".revision").write_text(str(latest_revision))
