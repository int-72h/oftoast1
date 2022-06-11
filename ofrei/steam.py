import vdf
from pathlib import Path
from sys import platform
from subprocess import run
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog

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
        if (target_path / Path('.svn')).exists() or (target_path / Path('.git')).exists():
            warnMsg = QMessageBox()
            warnMsg.setWindowTitle("OFToast")
            warnMsg.setText(
                "You should remove .svn or .git from your open_fortress folder. We can't do this, you will. It's not "
                "mandatory but recommended.")
            warnMsg.setStandardButtons(QMessageBox.Ok)
            buttonPressed = warnMsg.exec_()
        else:
            print('already exists, carrying on')
    elif target_path.parents[0].exists():
        Path.mkdir(target_path)
        print('carrying on...')
    elif target_path.parents[1].exists():
        print('Generating sourcemods folder...')
        Path.mkdir(target_path.parents[0])
        Path.mkdir(target_path)

    else:
        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText(
            "We can't find your steam install. Use the browse button to navigate to the sourcemods folder.")
        exitMsg.setStandardButtons(QMessageBox.Ok)
        buttonPressed = exitMsg.exec_()
        return -1
    return target_path


def sdk_download(path_to_steamapps):
    #Check Source SDK
    already_downloaded = False
    try:
        library_folders = vdf.load(open(path_to_steamapps / Path('libraryfolders.vdf')))['libraryfolders']
        for x in library_folders:
            if ('243750' in library_folders[x]['apps'].keys()):
                already_downloaded = True
    except:
        pass
    if not already_downloaded:
        if platform.startswith('win32'):
            run(["start", "steam://install/243750"], shell=True)
        else:
            run(["xdg-open", "steam://install/243750"])
        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText(
            "You need to install Source SDK 2013 for Open Fortress to run.\nAn install box should have "
            "appeared. If it hasn't, pop this URL into your browser: \nsteam://install/243750\nIf "
            "you've already got it installed, ignore this message.")
        exitMsg.exec_()
    else:
        print("sdk 2013 already installed!")

    #Check TF2
    already_downloaded=False
    try:
        library_folders = vdf.load(open(path_to_steamapps / Path('libraryfolders.vdf')))['libraryfolders']
        for x in library_folders:
            if ('440' in library_folders[x]['apps'].keys()):
                already_downloaded = True
    except:
        pass
    if not already_downloaded:
        if platform.startswith('win32'):
            run(["start", "steam://install/440"], shell=True)
        else:
            run(["xdg-open", "steam://install/440"])
        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText(
            "You need to install Team Fortress 2 on Steam for Open Fortress to run.\nAn install box should have "
            "appeared. If it hasn't, pop this URL into your browser: \nsteam://install/440\nIf "
            "you've already got it installed, ignore this message.")
        exitMsg.exec_()
    else:
        print("tf2 already installed!")
# handle other inputs here
