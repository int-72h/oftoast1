#!/usr/bin/python

from tvn import *
import argparse
import sys
import os
import tempfile
import urllib

from concurrent.futures import ThreadPoolExecutor, as_completed
from steam import *
from pathlib import Path, PosixPath, WindowsPath
from sys import exit
from shutil import move
import httpx

parser = argparse.ArgumentParser(description="Manage Open Fortress installation.")
parser.add_argument("action", type=str, help='action to execute on a directory, currently only "upgrade"')
parser.add_argument("directory", type=str, help='action to execute on a directory, currently only "upgrade"')
parser.add_argument("-u", default="http://toast.openfortress.fun/toast/", help="url to fetch data from")
parser.add_argument("-c", default="4", help="no. of cores")
args = parser.parse_args()

if args.action != "upgrade":
    print("invalid action", file=sys.stderr)
    exit(1)

game_path = Path(args.directory)

installed_revision = get_installed_revision(game_path)
latest_revision = fetch_latest_revision(args.u)

print(installed_revision, "->", latest_revision, file=sys.stderr)

revisions = fetch_revisions(args.u, installed_revision, latest_revision)
changes = replay_changes(revisions)

temp_dir = tempfile.TemporaryDirectory()
temp_path = Path(temp_dir.name)

writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))
executor = ThreadPoolExecutor(int(args.c))


def work(x):
    with httpx.Client(http2=True, headers={'user-agent': 'Mozilla/5.0'}) as client:
        resp = client.get(args.u + "/objects/" + x["object"])
        file = open(temp_path / x["object"], "wb+")
        file.write(resp.content)
        file.close()


# futures = {executor.submit(work, x): x for x in writes}
futures = {}
for x in writes:
    if x["type"] == TYPE_WRITE:
        futures[executor.submit(work, x)] = x
for x in as_completed(futures):
    print('WRITE ' + futures[x]["path"])
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
    os.mkdir(game_path / x["path"], 0o777)

for x in writes:
    move(temp_path / x["object"], str(game_path) + "/" + x["path"])

(game_path / ".revision").touch(0o777)
(game_path / ".revision").write_text(str(latest_revision))
