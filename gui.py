from concurrent.futures import ThreadPoolExecutor,as_completed
import os
import urllib.request
from urllib.error import HTTPError
import tempfile
from steam import *
from pathlib import Path, PosixPath, WindowsPath
from sys import exit
from tvn import *
from shutil import move
import httpx

from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtGui import QPalette, QColor
import sys


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
        MainWindow.setMinimumSize(QtCore.QSize(608, 180))
        MainWindow.setMaximumSize(QtCore.QSize(608, 180))
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
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.browse = QtWidgets.QPushButton(self.centralwidget)
        self.browse.setGeometry(QtCore.QRect(160, 20, 121, 28))
        self.browse.setObjectName("browse")
        self.browse.clicked.connect(self.clickBrowse)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(290, 20, 291, 28))
        self.lineEdit.setObjectName("lineEdit")
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
        self.pushButton.setGeometry(QtCore.QRect(380, 130, 90, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.clickUpdate)
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(480, 130, 90, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.clickCancel)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(160, 133, 211, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(200, 100, 341, 16))
        self.label_4.setText("")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "OFToast"))
        self.browse.setText(_translate("MainWindow", "Browse"))
        self.lineEdit.setText(_translate("MainWindow", "GAMEDIR"))
        self.label_2.setText(_translate("MainWindow", "Download URL"))
        self.lineEdit_2.setText(_translate("MainWindow", "https://www.openfortress.fun/toast/"))
        self.pushButton.setText(_translate("MainWindow", "Update"))
        self.pushButton_2.setText(_translate("MainWindow", "Cancel"))
        self.label_3.setText(_translate("MainWindow", "Installed Revision: None"))

    def clickBrowse(self):
        gamepath = QFileDialog.getExistingDirectory(MainWindow, "Game path", "")
        # self.lineEdit.setText(gamepath[0].removesuffix("gameinfo.txt"))
        revision = get_installed_revision(Path(self.lineEdit.text()))
        if revision >= 0:
            self.label_3.setText("Installed Revision: " + str(revision))
        else:
            self.label_3.setText("Installed Revision: None")

    def clickUpdate(self):
        self.browse.setDisabled(True)
        self.pushButton.setDisabled(True)
        self.pushButton_2.setDisabled(True)
        game_path = Path(self.lineEdit.text())
        if 'open_fortress' not in str(game_path):
            try:
                Path.mkdir(game_path / Path('open_fortress'))
            except FileExistsError:
                pass
        installed_revision = get_installed_revision(game_path)
        try:
            latest_revision = fetch_latest_revision(self.lineEdit_2.text())
        except HTTPError:
            errorMsg = QMessageBox()
            errorMsg.setWindowTitle("OFToast")
            errorMsg.setText("Invalid URL!")
            errorMsg.exec_()
            exit(1)
        print(latest_revision)
        revisions = fetch_revisions(self.lineEdit_2.text(), installed_revision, latest_revision)
        changes = replay_changes(revisions)

        temp_dir = tempfile.TemporaryDirectory()
        temp_path = Path(temp_dir.name)

        writes = list(filter(lambda x: x["type"] == TYPE_WRITE, changes))
        todl = [[self.lineEdit_2.text() + "/objects/" + x["object"], temp_path / x["object"]] for x in writes]
        x = [x for x in pbar_sg(todl, self, app)]
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

        for x in writes:
            move(temp_path / x["object"], str(game_path) + "/" + x["path"])

        (game_path / ".revision").touch(0o777)
        (game_path / ".revision").write_text(str(latest_revision))

        exitMsg = QMessageBox()
        exitMsg.setWindowTitle("OFToast")
        exitMsg.setText("Done!")
        exitMsg.exec_()
        exit(1)

    def clickCancel(self):
        exit(1)


def work(arr):
    with httpx.Client(http2=True, headers={'user-agent': 'ofl/0.0.0'}) as client:
        resp = client.get(arr[0])
        file = open(arr[1], "wb+")
        file.write(resp.content)
        file.close()

def pbar_sg(iter, self, app, num_cpus=40):
    length = len(iter)
    z = 0
    executor = ThreadPoolExecutor(num_cpus)
    futures = {executor.submit(work, x): x for x in iter}
    for future in as_completed(futures):
        it = futures[future]
        z = z + 1
        self.label_4.setText(it[0])
        self.progressBar.setValue(z)
        self.progressBar.setMaximum(length)
        app.processEvents()


def get_revision(url: str, revision: int) -> list[Change]:
    r = urllib.request.urlopen(url + "/" + str(revision), headers={'User-Agent': 'rei/0.0.1'}).read()
    return json.loads(r)


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
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("toast.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    MainWindow.setWindowIcon(icon)
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
    palette.setColor(QPalette.Highlight, QColor("#2C1642"))
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
