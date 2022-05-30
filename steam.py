import vdf
from pathlib import Path
from sys import platform,exit
from subprocess import run
from shutil import rmtree

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
import sys

if platform.startswith('win32'):
    from winreg import *
def getpath():
    if platform.startswith('linux'):
        target_path = Path.home() / Path('.steam/steam/steamapps/sourcemods/open_fortress')
    elif platform.startswith('win32'):
        try:
            regkey = OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Wow6432Node\\Valve\\Steam")
        except FileNotFoundError:
            try:
                regkey = OpenKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Valve\\Steams")
            except FileNotFoundError:
                print("steam install not found...")
                return -1
        target_path = Path(QueryValueEx(regkey, "InstallPath")[0]) / Path('steamapps/sourcemods/open_fortress')
    else:
        print("you aren't on anything we support.")
        return -1
    if target_path.exists():
        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText("Old Open fortress installations aren't compatible with the new launcher.\nYour old installation will be removed. ")
        exitMsg.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        buttonPressed = exitMsg.exec_()

        if buttonPressed == QMessageBox.Ok:
            rmtree(target_path)
        else:
            exit()
    elif target_path.parents[0].exists():
        print('All good, carrying on')
        Path.mkdir(target_path)
    elif target_path.parents[1].exists():
        print('Generating sourcemods folder...')
        Path.mkdir(target_path.parents[0])
        Path.mkdir(target_path)
    else:
        print("Ok something's wrong, put in your path manually")
        return -1
    return target_path

def sdk_download(path_to_steamapps):
    library_folders = vdf.load(open(path_to_steamapps/Path('libraryfolders.vdf')))['libraryfolders']
    already_downloaded = False
    for x in library_folders:
        try:
            z = library_folders[x]['apps']['243750']
            already_downloaded = True
        except KeyError:
            continue
    if not already_downloaded:
        if platform.startswith('win32'):
            run(["start","steam://install/243750"])
        else:
            run(["xdg-open","steam://install/243750"])
        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText("You need to install Source SDK 2013 on Steam first.\nAn install box should have appeared. If it hasn't, pop this URL into your browser: steam://install/243750")
        exitMsg.exec_()
        exit(1)
    else:
        print("sdk 2013 already installed!")
#handle other inputs here