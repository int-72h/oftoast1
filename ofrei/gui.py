from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from steam import *
from sys import exit
from tvn import *
import httpx
import traceback
import shutil
import hashlib

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtGui import QPalette, QColor
import sys

global version
version = '0.2.2'


class Ui_MainWindow(object):
    def setupUi(self, app, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(608, 180)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(638, 180))
        MainWindow.setMaximumSize(QtCore.QSize(638, 180))
        MainWindow.setAcceptDrops(False)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setAnimated(True)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 20, 131, 141))
        self.label.setText("")
        if getattr(sys, "frozen", False):
            # PyInstaller executable
            toasty = str(Path(sys._MEIPASS).resolve().joinpath("toast.png"))
        else:
            # Raw .py file
            toasty = "toast.png"
        self.label.setPixmap(QtGui.QPixmap(toasty))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(toasty), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(160, 20, 421, 28))
        self.lineEdit.setObjectName("lineEdit")
        #self.lineEdit.setDisabled(True)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(160, 60, 121, 31))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(290, 60, 291, 28))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(160, 100, 421, 16))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setFormat("")
        self.progressBar.setObjectName("progressBar")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(330, 130, 90, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.clickUpdate)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(430, 130, 90, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.clickCancel)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(110, 133, 211, 20))
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(230, 130, 90, 28))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.clickVerify)
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(530, 130, 90, 28))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_4.clicked.connect(self.clickLaunch)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(65, 133, 211, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OFToast " + version))
        self.lineEdit.setText(_translate("MainWindow", "GAMEDIR"))
        self.label_2.setText(_translate("MainWindow", "Download URL"))
        self.lineEdit_2.setText(_translate("MainWindow", "https://toast.openfortress.fun/toast"))
        self.pushButton.setText(_translate("MainWindow", "Update"))
        self.pushButton_2.setText(_translate("MainWindow", "Cancel"))
        self.pushButton_3.setText(_translate("MainWindow", "Verify"))
        self.label_3.setText(_translate("MainWindow", "Installed Revision: None"))
        self.pushButton_4.setText(_translate("MainWindow", "Launch"))

    def clickBrowse(self):
        temp = self.lineEdit.text()
        gamepath = QFileDialog.getExistingDirectory(MainWindow, "Game path", "")
        if gamepath == '':
            self.lineEdit.setText(temp)
        else:
            self.lineEdit.setText(gamepath)
        revision = get_installed_revision(Path(self.lineEdit.text()))
        if revision >= 0:
            self.label_3.setText("Installed Revision: " + str(revision))
        else:
            self.label_3.setText("Installed Revision: None")

    def clickUpdate(self):
        global version
        try:
            self.pushButton.setText('Updating...')
            self.pushButton.setDisabled(True)
            self.pushButton_2.setDisabled(True)
            self.pushButton_3.setDisabled(True)
            app.processEvents()
            game_path = Path(self.lineEdit.text())
            url = self.lineEdit_2.text()
            response = httpx.get(url, follow_redirects=True)
            resUrl = response.url
            url = "https://" + resUrl.host + "/toast/"
            print("Server Selected: " + url)
            if 'open_fortress' not in str(game_path):
                try:
                    Path.mkdir(game_path / Path('open_fortress'))
                except FileExistsError:
                    pass
            installed_revision = get_installed_revision(game_path)
            try:
                num_threads = get_threads(url)
                latest_ver = get_latest_ver(url)
                latest_revision = fetch_latest_revision(url)
            except:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("OFToast")
                errorMsg.setText("Invalid URL!")
                errorMsg.exec_()
                exit(1)
            print(version)
            if latest_ver != version:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("out of date!")
                errorMsg.setText(
                    "This isn't the latest version! you need to download the latest version from the website.\nlatest "
                    "version: " + latest_ver)
                errorMsg.exec_()
            revisions = fetch_revisions(url, installed_revision, latest_revision)
            changes = replay_changes(revisions)
            writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))
            client = httpx.Client(headers={'user-agent': 'Mozilla/5.0', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0'})
            todl = [[url + "objects/" + x["object"], game_path / x["path"], x["hash"], client] for x in writes]
            try:
                os.remove(game_path / ".revision")
            except FileNotFoundError:
                pass

            for x in list(filter(lambda x: x["type"] == TYPE_DELETE, changes)):
                try:
                    os.remove(game_path / x["path"])
                except FileNotFoundError:
                    pass

            for x in list(filter(lambda x: x["type"] == TYPE_MKDIR, changes)):
                try:
                    os.mkdir(game_path / x["path"], 0o777)
                except FileExistsError:
                    pass
            self.pushButton.setText('Downloading...')
            pbar_sg(todl, self, app, num_threads)
            (game_path / ".revision").touch(0o777)
            (game_path / ".revision").write_text(str(latest_revision))
            exitMsg = QMessageBox()
            exitMsg.setWindowTitle("OFToast")
            exitMsg.setText("Done!")
            exitMsg.exec_()
            exit(1)
        except TimeoutError or httpx.RequestError or ConnectionResetError or httpx.ReadTimeout:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("The server you've connected to is down! Try again later.")
            errorMsg.exec_()
        except TimeoutError or httpx.RequestError or ConnectionResetError:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("The server you've connected to is down! Try again later.")
            errorMsg.exec_()
        except Exception as e:
            error_message = traceback.format_exc()
            if 'timeout' or 'reset' in error_message:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("rei?")
                errorMsg.setText("The server you've connected to is down! Try again later.")
                errorMsg.exec_()
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText(
                "Something's gone wrong! Post the following error in the troubleshooting channel: " + error_message)
            errorMsg.exec_()
            exit(1)

    def clickCancel(self):
        exit(1)

    
    def clickVerify(self):
        global version
        try:
            self.pushButton_3.setText('Verifying...')
            self.pushButton.setDisabled(True)
            self.pushButton_2.setDisabled(True)
            self.pushButton_3.setDisabled(True)
            app.processEvents()
            game_path = Path(self.lineEdit.text())
            url = self.lineEdit_2.text()
            response = httpx.get(url, follow_redirects=True)
            resUrl = response.url
            url = "https://" + resUrl.host + "/toast/"
            print("Server Selected: " + url)
            if 'open_fortress' not in str(game_path):
                try:
                    Path.mkdir(game_path / Path('open_fortress'))
                except FileExistsError:
                    pass
            installed_revision = -1 # = get_installed_revision(game_path)
            try:
                num_threads = get_threads(url)
                latest_ver = get_latest_ver(url)
                latest_revision = fetch_latest_revision(url)
            except:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("OFToast")
                errorMsg.setText("Invalid URL!")
                errorMsg.exec_()
                exit(1)
            print(version)
            if latest_ver != version:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("out of date!")
                errorMsg.setText(
                    "This isn't the latest version! you need to download the latest version from the website.\nlatest "
                    "version: " + latest_ver)
                errorMsg.exec_()
            revisions = fetch_revisions(url, installed_revision, latest_revision)
            changes = replay_changes(revisions)
            writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))
            client = httpx.Client(headers={'user-agent': 'Mozilla/5.0', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0'})
            todl = [[url + "objects/" + x["object"], game_path / x["path"], x["hash"], client] for x in writes]
            try:
                os.remove(game_path / ".revision")
            except FileNotFoundError:
                pass

            for x in list(filter(lambda x: x["type"] == TYPE_DELETE, changes)):
                try:
                    os.remove(game_path / x["path"])
                except FileNotFoundError:
                    pass

            for x in list(filter(lambda x: x["type"] == TYPE_MKDIR, changes)):
                try:
                    os.mkdir(game_path / x["path"], 0o777)
                except FileExistsError:
                    pass
            self.pushButton_3.setText('Verifying...')
            pbar_sg_verif(todl, self, app, num_threads)
            (game_path / ".revision").touch(0o777)
            (game_path / ".revision").write_text(str(latest_revision))
            exitMsg = QMessageBox()
            exitMsg.setWindowTitle("OFToast")
            exitMsg.setText("Done!")
            exitMsg.exec_()
            exit(1)
        except TimeoutError or httpx.RequestError or ConnectionResetError or httpx.ReadTimeout:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("The server you've connected to is down! Try again later.")
            errorMsg.exec_()
        except TimeoutError or httpx.RequestError or ConnectionResetError:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("The server you've connected to is down! Try again later.")
            errorMsg.exec_()
        except Exception as e:
            error_message = traceback.format_exc()
            if 'timeout' or 'reset' in error_message:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("rei?")
                errorMsg.setText("The server you've connected to is down! Try again later.")
                errorMsg.exec_()
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText(
                "Something's gone wrong! Post the following error in the troubleshooting channel: " + error_message)
            errorMsg.exec_()
            exit(1)
            
    def clickLaunch(self):
        self.pushButton_4.setText('Launching...')
        game_path = Path(self.lineEdit.text())
        if 'open_fortress' not in str(game_path):
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("You dont seem to have Open Fortress installed! Click the 'Update' button to install.")
            errorMsg.exec_()
            self.pushButton_4.setText('Launch')
            return
            
        ofpath = getpath()
        if ofpath != -1:
            library_folders = vdf.load(open(ofpath.parents[1] / Path('libraryfolders.vdf')))['libraryfolders']
            sdkExists = False
            for x in library_folders:
                if ('243750' in library_folders[x]['apps'].keys()):
                    print(library_folders[x]['path'])
                    sdkPath = (library_folders[x]['path'] / Path('steamapps') / Path('common') / Path('Source SDK Base 2013 Multiplayer'))
                    sdkExists = True
            if sdkExists == False:
                errorMsg = QMessageBox()
                errorMsg.setWindowTitle("rei?")
                errorMsg.setText("You dont seem to have the Source Sdk 2013 base multiplayer installed!")
                errorMsg.exec_()
                self.pushButton_4.setText('Launch')
                return
        else:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("rei?")
            errorMsg.setText("You dont seem to have Open Fortress installed! Click the 'Update' button to install.")
            errorMsg.exec_()
            self.pushButton_4.setText('Launch')
            return
        
        if platform.startswith('win32'):
            hl2 = "{sdk}\hl2.exe".format(sdk = sdkPath)
            run([hl2, "-game", ofpath], shell=True)
        else:
            hl2 = "{sdk}\hl2_linux".format(sdk = sdkPath)
            run([hl2, "-game", ofpath])
        self.pushButton_4.setText('Launch')



def get_threads(url):
    r = httpx.get(url + "/reithreads")
    return int(r.text)


def get_latest_ver(url):
    r = httpx.get(url + "/reiversion")
    return r.text.strip()


def work(arr):
    exists = False
    while exists == False:
        wasProblematic = False
        goodDownload = False
        hasher = hashlib.md5()
        while goodDownload == False:
            resp = arr[3].get(arr[0])
            hasher.update(resp.content)
            hodl = hasher.hexdigest()
            #print("Hash of file:", hodl)
            #print("Compared to stored hash of:", arr[2])
            if hodl == arr[2]:
                goodDownload = True
            else:
                if wasProblematic == False:
                    print("Hash failed for file", arr[1], "Retrying...")
                wasProblematic = True
                hasher = hashlib.md5() #reset hasher
                goodDownload = False
        if wasProblematic:
            print(arr[1], "was able to finish downloading!")
        file = open(arr[1], "wb+")
        file.write(resp.content)
        file.close()
        if arr[1].exists():
            exists = True
        else:
            print("file hasn't downloaded...")

def work_verif(arr):
    if arr[1].exists():
        f = open(arr[1], "rb")
        fcontents = f.read()
        f.close()
        hasher = hashlib.md5()
        hasher.update(fcontents)
        hodl = hasher.hexdigest()
        if hodl == arr[2]:
            #good :)
            pass
        else:
            print(arr[1], "failed verification, redownloading...")
            work(arr)
    else:
        print(arr[1], "not found, redownloading...")
        work(arr)


def pbar_sg(iter, self, app, num_cpus=16):
    length = len(iter)
    z = 0
    executor = ThreadPoolExecutor(num_cpus)
    futures = {executor.submit(work, x): x for x in iter}
    for _ in as_completed(futures):
        z = z + 1
        self.progressBar.setValue(z)
        self.progressBar.setMaximum(length)
        app.processEvents()

def pbar_sg_verif(iter, self, app, num_cpus=16):
    length = len(iter)
    z = 0
    executor = ThreadPoolExecutor(num_cpus)
    futures = {executor.submit(work_verif, x): x for x in iter}
    for _ in as_completed(futures):
        z = z + 1
        self.progressBar.setValue(z)
        self.progressBar.setMaximum(length)
        app.processEvents()


def get_revision(url: str, revision: int):
    r = httpx.get(url + "/" + str(revision))
    return json.loads(r.text)


def existing_game_check(ui, MainWindow):
    ofpath = getpath()
    if ofpath != -1:
        sdk_download(ofpath.parents[1])
        revision = get_installed_revision(ofpath)
        if revision >= 0:
            ui.label_3.setText("Installed Revision: " + str(revision))
        ui.lineEdit.setText(str(ofpath))


def set_theme(app, MainWindow):
    QApplication.setStyle("fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#584169'))
    palette.setColor(QPalette.WindowText, QColor('#C8C1C7'))
    palette.setColor(QPalette.Base, QColor('#F7EAD6'))
    palette.setColor(QPalette.AlternateBase, QColor("#27234d"))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor('#433157'))
    palette.setColor(QPalette.Button, QColor("#2C1642"))
    palette.setColor(QPalette.ButtonText, QColor('#C8C1C7'))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor("#584169"))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    set_theme(app, MainWindow)
    ui.setupUi(app, MainWindow)
    existing_game_check(ui, MainWindow)
    MainWindow.show()

    sys.exit(app.exec_())
