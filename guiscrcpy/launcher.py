#!/usr/bin/env python3

"""
GUISCRCPY by srevinsaju
Get it on : https://github.com/sevinsaju/guiscrcpy
Licensed under GNU Public License

Icon made by Dave Gandy from www.flaticon.com used under
Creative Commons 3.0 Unported. The original SVG black work
by Dave Gandy has been re-oriented, flipped or color-changed.
The rest of Terms and Conditions put formward by
CC-3.0:Unported has been feverently followed by the developer.
Icons have been adapted in all the three windows.

Icons pack obtained from www.flaticon.com
All rights reserved.

"""

# Prelaunch

__version__ = '2.0.0-raw'

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWidgets import QMessageBox
import qdarkstyle
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import json
import sys
import platform
import argparse
import logging
import webbrowser
import time
from datetime import datetime
from subprocess import PIPE
from subprocess import Popen as po, STDOUT
import os
import os.path
from subprocess import PIPE, Popen

try:
	os.chdir(os.path.dirname(__file__))
except:
    # Its a PyInstaller compiled package
	pass

# get cfgpath
# Declare Config path position
if (platform.system() == 'Windows'):
    cfgpath = os.path.expanduser("~/AppData/Local/guiscrcpy/")
else:
    if (os.getenv('XDG_CONFIG_HOME') is None):
        cfgpath = os.path.expanduser("~/.config/guiscrcpy/")
    else:
        cfgpath = os.getenv('XDG_CONFIG_HOME').split(":")[0]+"/guiscrcpy"

# init parser
parser = argparse.ArgumentParser()
parser.add_argument('-i', '--install', action='store_true',
                    help="Install guiscrcpy system wide on Linux")
parser.add_argument('-s', '--start', action='store_true',
                    help="Start scrcpy first before loading the GUI")
parser.add_argument('-d', '--debug', default=3,
                    help="Set a logging level from 0,1,2,3,4,5")
parser.add_argument('-v', '--version', action='store_true',
                    help="Display guiscrcpy version")
args = parser.parse_args()

if args.debug:
    logging_priority = int(args.debug) * 10
else:
    logging_priority = 30

# setup logging 
logging.basicConfig(
    filename=os.path.join(cfgpath, 'guiscrcpy_log_{}.log'.format(datetime.now().strftime("%Y%m%d_%H%M%S"))),
    filemode='w',
    level=logging_priority,
    format='%(levelname)s :: %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler())

# init pynput if it exists, else pass
try:
    from pynput import keyboard
except Exception as e:
    logging.warning("Running from tty, pass. E:{}".format(e))
    keyboard = None

# FIXME move to version.py
sha = None
try:
    import git
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = "-" + repo.head.object.hexsha
        if not repo.git.describe("--tags").startswith('0.'):
            __version__ = repo.git.describe("--tags")
    except BaseException:
        logging.warning("This is not running from Source. No git sha retrievable")
        logging.warning("Extracting version number from pip")
        try:
            import pkg_resources
            __version__ = pkg_resources.get_distribution(
                "guiscrcpy").version
        except BaseException:
            logging.warning("guiscrcpy not installed as pip package." +
                  "Version retrieve failed.")

except ModuleNotFoundError:
    logging.warning(
        "ERR: gitpython is not found. It is not a dependency,"
        " but you can optionally install it "
        "with python3 -m pip install gitpython"
    )

build = __version__ + " by srevinsaju"

# Argument parser

logging.debug("Received flag {}".format(args.start))


class termcolors:
    if platform.system() == "Linux":
        HEADER = "\033[95m"
        OKBLUE = "\033[94m"
        OKGREEN = "\033[92m"
        WARNING = "\033[93m"
        FAIL = "\033[91mERR:"
        ENDC = "\033[0m"
        BOLD = "\033[1m"
        UNDERLINE = "\033[4m"
    else:
        HEADER = ""
        OKBLUE = ""
        OKGREEN = ""
        WARNING = ""
        FAIL = "ERR:"
        ENDC = ""
        BOLD = ""
        UNDERLINE = ""


# import pdb
# removed multiprocess modules

if not sha:
    commit1 = __version__
else:
    commit1 = __version__ + " commit" + sha

print(
    termcolors.UNDERLINE +
    "                                  " +
    termcolors.ENDC)
print()
print("guiscrcpy")
print("by srevinsaju")
print(termcolors.OKBLUE + commit1 + termcolors.ENDC)
print(
    termcolors.OKBLUE +
    "Licensed under GNU GPL v3 (c) 2019  " +
    termcolors.ENDC)
print(
    termcolors.UNDERLINE +
    "                                  " +
    termcolors.ENDC)
print(termcolors.OKBLUE + "" + termcolors.ENDC)

# chk version argument given or not
if args.version:
    sys.exit(0)

print()
print(
    "MSG: Please ensure you have enabled",
    termcolors.OKGREEN + "USB Debugging" + termcolors.ENDC,
    "on your device. See README.md for more details",
)
# print("Current Working Directory >> ", os.getcwd())
# print('__file__ name             >> ', str(__file__))
# print("os.path Absolute Path     >> ", os.path.abspath(__file__))
logging.debug("Current Working Directory {}".format(os.getcwd()))


# ******************************
# CONFIGURATION FILE CHECKER
# *****************************
# Pre declare variable for handlin NameError, AttributeError exception
config = {
    'dimension': None,
    'swtouches': False,
    'bitrate': 8000,
    'fullscreen': False,
    'dispRO': False,
    'extra': ""}
dimension0 = None
dimension = None
swtouches0 = "False"
bitrate0 = 8000
fullscreen0 = "False"
dispRO0 = "False"
jsonf = 'guiscrcpy.json'


try:
    with open(cfgpath + jsonf, 'r') as f:
        config = json.load(f)
    fileExist = True
    logging.debug("Configuration file found in {} directory".format(cfgpath))

except FileNotFoundError:

    logging.debug("Initializing guiscrcpy for first time use...")
    try:
        os.makedirs(cfgpath)
    except FileExistsError:
        logging.debug("Folder guiscrcpy aldready exists.")
    with open(cfgpath + jsonf, 'w') as f:
        json.dump(config, f)

    logging.debug("Configuration file created in {} directory".format(cfgpath))
    fileExist = False

    if platform.system() == "Windows":
        logging.debug(
            "Detected a Windows Operating System :: {} {}".format(
            platform.release(),
            platform.version()
        ))
        pass
    elif platform.system() == "Linux":

        logging.debug(
            "Detected a Linux Operating System :: {} {} ".format(
            platform.release(),
            platform.version()
        ))
        logging.debug("Installing Trebuchet MS font ...")
        os.system("mkdir ~/.fonts/")
        os.system("cp -r fonts/* ~/.fonts/")

    else:
        logging.debug(" MacOS :: Untested OS detected. Continuing >>> ")

if not fileExist:

    # Init json file for first time use
    config = {
        'dimension': None,
        'swtouches': False,
        'bitrate': 8000,
        'fullscreen': False,
        'dispRO': False,
        'extra': ""}
    with open(cfgpath + jsonf, 'w') as f:
        json.dump(config, f)


elif fileExist:
    with open(cfgpath + jsonf, 'r') as f:
        config = json.load(f)

if platform.system() == "Windows":

    if os.path.isfile("./scrcpy.exe"):
        increment = ".\\"
    else:
        logging.error("scrcpy.exe not found in current directory.")
        print(
            termcolors.BOLD +
            "Fallback to system PATH variable." +
            "Please add scrcpy to path." +
            termcolors.ENDC)
        increment = ""

    if os.path.exists('bin/adb.exe'):
        increment = ".\\bin\\"
    if os.path.exists('bin/scrcpy.exe'):
        increment = ".\\bin\\"

else:
    if not fileExist:
        logging.debug(
            "One time checking for scrcpy executable." +
            "(Use RESET for rechecking)"
        )
        increment = ""
        scrcpy_checker = po(
            "scrcpy -v",
            stdout=PIPE,
            stderr=PIPE,
            shell=True)
        if scrcpy_checker.stderr.read().decode("utf-8").find("not found") != -1:
            logging.error("Failed to find scrcpy on path. 'Start Scrcpy' may not work")
        else:
            logging.debug("Scrcpy found " + scrcpy_checker.stdout.read().decode("utf-8"))
    else:
        increment = ""


# ***************************
# BEGIN ENGIN CODE
# ***************************

def invokeScrcpy():
    optPass = ""

    optPass += " -b " + str(config['bitrate'])
    if(config['fullscreen']):
        optPass += " -f "
    if(config['swtouches']):
        optPass += " -t "
    if(config['dispRO']):
        optPass += " --turn-screen-off "
    backup0r = po(
        increment + "scrcpy " + str(optPass),
        shell=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=STDOUT,
    )
    logging.debug(str(backup0r.stdout))

# ******************************

if (args.start):
    logging.debug("RUNNING SCRCPY DIRECTLY")
    invokeScrcpy()

logging.debug("Importing modules...")

try:
    from .mainui import Ui_MainWindow
except (ModuleNotFoundError, ImportError):
    try:
        from guiscrcpy.mainui import Ui_MainWindow
        logging.debug("Safe submodule import of mainui")
    except Exception as e:
        logging.error(
            "ERR: An Error with Code: {c} has occured explicitly, {m}. Please report to https://github.com/srevinsaju/guiscrcpy/issues".format(
                c=type(e).__name__,
                m=str(e)))

# from bottompanelUI import Ui_Panel
# import breeze_resources
# from toolUI import Ui_Dialog
try:
    import psutil
except ModuleNotFoundError:
    logging.warning(
        "WARNING : psutil is not installed in the python3 directory. "
        "Install with \n $ pip3 install psutil"
    )

try:
    import pyautogui as auto
    from pygetwindow import getWindowsWithTitle
except Exception as e:
    logging.debug("1 {}".format(e))
    auto = None
    getWindowsWithTitle = None


# BEGIN TOOLKIT.UI
class UXMapper:
    def __init__(self):
        logging.debug("Launching UX Mapper")
        self.has_modules = getWindowsWithTitle and auto
        logging.debug("Calculating Screen Size")
        self.adb_dim = po("{}adb shell wm size".format(increment),
            shell=True,
            stdout=PIPE,
            stderr=PIPE)
        self.raw_dimensions = self.adb_dim.stdout.read().decode()
        self.android_dimensions = self.get_dimensions()

    def do_swipe(self, x1=10, y1=10, x2=10, y2=10):
        adb_pull = po(
            "{}adb shell input swipe {} {} {} {}".format(increment, x1, y1, x2, y2),
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
        return True
    
    def do_keyevent(self, key):
        po(
            "{}adb shell input keyevent {}".format(increment, key),
            shell=True,
            stdout=PIPE,
            stderr=PIPE)
        
    def get_dimensions(self):
        for i in ['Override size', 'Physical size']:
            if i in self.raw_dimensions:
                out = self.raw_dimensions[self.raw_dimensions.find(i):]
                out_decoded = out.split(':')[1].strip()
                dimValues = out_decoded.split('x')
                return dimValues
        else:
            logging.error("AndroidDeviceError: adb shell wm size did not return 'Physical Size' or 'Override Size'")

    def copy_devpc(self):
        if self.has_modules:
            scrcpywindow = getWindowsWithTitle("scrcpy")[0]
            scrcpywindow.focus()
            auto.hotkey("ctrl", "c")
        else:
            os.system(
                "wmctrl -x -a  scrcpy && xdotool key --clearmodifiers ctrl+c")

    def key_power(self):
        logging.debug("Passing POWER")
        self.do_keyevent(26)

    def key_menu(self):
        logging.debug("Passing MENU")
        self.do_keyevent(82)

    def key_back(self):
        logging.debug("Passing BACK")
        self.do_keyevent(4)

    def key_volume_up(self):
        logging.debug("Passing BACK")
        self.do_keyevent(24)

    def key_volume_down(self):
        logging.debug("Passing BACK")
        self.do_keyevent(25)

    def key_home(self):
        logging.debug("Passing HOME")
        self.do_keyevent(3)

    def key_switch(self):
        logging.debug("Passing APP_SWITCH")
        self.do_keyevent("KEYCODE_APP_SWITCH")

    def reorientP(self):
        logging.debug("Passing REORIENT [POTRAIT]")
        adb_reo = po(
            increment +
            "adb shell settings put system accelerometer_rotation 0",
            shell=True)

        adb_reosl = po(
            increment +
            " adb shell settings put system rotation 1",
            shell=True)

    def reorientL(self):
        logging.debug("Passing REORIENT [LANDSCAPE]")
        adb_reoo = po(
            increment +
            "adb shell settings put system accelerometer_rotation 0",
            shell=True)
        adb_reool = po(
            increment +
            " adb shell settings put system rotation 1",
            shell=True)

    def expand_notifications(self):
        logging.debug("Passing NOTIF EXPAND")
        self.do_swipe(0, 0, 0, int(self.android_dimensions[1]) - 1)

    def collapse_notifications(self):
        logging.debug("Passing NOTIF COLLAPSE")
        self.do_swipe(0, int(self.android_dimensions[1]) - 1, 0, 0)

    def copy_pc2dev(self):
        if self.has_modules:
            scrcpywindow = getWindowsWithTitle("scrcpy")[0]
            scrcpywindow.focus()
            auto.hotkey("ctrl", "shift", "c")
            logging.warning(" NOT SUPPORTED ON WINDOWS")
        else:
            os.system(
                "wmctrl -x -a  scrcpy && xdotool key --clearmodifiers ctrl+shift+c")

    def fullscreen(self):
        if self.has_modules:
            scrcpywindow = getWindowsWithTitle("scrcpy")[0]
            scrcpywindow.focus()
            auto.hotkey("ctrl", "f")
        else:
            os.system(
                "wmctrl -x -a  scrcpy && xdotool key --clearmodifiers ctrl+f")


class MyAppv(QMainWindow):
    def __init__(self):
        self.oldPos = None
        super(MyAppv, self).__init__()
        self.ux = None
        self.setObjectName("Dialog")
        self.resize(30, 461)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(30, 340))
        self.setMaximumSize(QtCore.QSize(104, 600))
        self.setBaseSize(QtCore.QSize(30, 403))
        self.setWindowTitle("guiscrcpy")
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/res/ui/guiscrcpy_logo.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.setWindowIcon(icon)
        self.setWindowOpacity(1.0)
        self.setStyleSheet(
            "QDialog{\n"
            "width: 30px\n"
            "}\n"
            "QPushButton {\n"
            "                        \n"
            "\n"
            "border-radius: 1px;\n"
            "        background-color: qlineargradient(spread:pad, x1:0, y1:0.915182, x2:0, y2:0.926, stop:0.897059 rgba(41, 41, 41, 255), stop:1 rgba(30, 30, 30, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "                        \n"
            "                    }\n"
            "\n"
            "QPushButton:pressed {\n"
            "border-radius: 5px;\n"
            "                      \n"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 255, 255, 255), stop:1 rgba(0, 255, 152, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "                        }\n"
            "QPushButton:hover {\n"
            "border-radius: 5px;\n"
            "                      \n"
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 199, 199, 255), stop:1 rgba(0, 190, 113, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "                        }\n"
            "")
        self.notif_collapse = QtWidgets.QPushButton(self)
        self.notif_collapse.setEnabled(True)
        self.notif_collapse.setGeometry(QtCore.QRect(0, 75, 30, 25))
        self.notif_collapse.setMouseTracking(True)
        # self.notif_collapse.setTabletTracking(True)
        # self.notif_collapse.setAutoFillkey_background(False)
        self.notif_collapse.setStyleSheet("")
        self.notif_collapse.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/bell-musical-tool(2).svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.notif_collapse.setIcon(icon1)
        self.notif_collapse.setFlat(True)
        self.notif_collapse.setObjectName("notif_collapse")
        self.menuUI = QtWidgets.QPushButton(self)
        self.menuUI.setEnabled(True)
        self.menuUI.setGeometry(QtCore.QRect(0, 275, 30, 25))
        self.menuUI.setMouseTracking(True)
        # self.menuUI.setTabletTracking(True)
        # self.menuUI.setAutoFillkey_background(False)
        self.menuUI.setStyleSheet("")
        self.menuUI.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/reorder-option.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.menuUI.setIcon(icon2)
        self.menuUI.setFlat(True)
        self.menuUI.setObjectName("menuUI")
        self.appswi = QtWidgets.QPushButton(self)
        self.appswi.setEnabled(True)
        self.appswi.setGeometry(QtCore.QRect(0, 300, 30, 25))
        self.appswi.setMouseTracking(True)
        # self.appswi.setTabletTracking(True)
        # self.appswi.setAutoFillkey_background(False)
        self.appswi.setStyleSheet("")
        self.appswi.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/four-black-squares.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.appswi.setIcon(icon3)
        self.appswi.setFlat(True)
        self.appswi.setObjectName("appswi")
        self.pinchoutUI = QtWidgets.QPushButton(self)
        self.pinchoutUI.setEnabled(False)
        self.pinchoutUI.setGeometry(QtCore.QRect(0, 350, 30, 25))
        self.pinchoutUI.setStyleSheet("")
        self.pinchoutUI.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/zoom-out.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.pinchoutUI.setIcon(icon4)
        self.pinchoutUI.setFlat(True)
        self.pinchoutUI.setObjectName("pinchoutUI")
        self.screenfreeze = QtWidgets.QPushButton(self)
        self.screenfreeze.setEnabled(True)
        self.screenfreeze.setGeometry(QtCore.QRect(0, 0, 30, 25))
        self.screenfreeze.setMouseTracking(True)
        # self.screenfreeze.setTabletTracking(True)
        # self.screenfreeze.setAutoFillkey_background(False)
        self.screenfreeze.setStyleSheet("")
        self.screenfreeze.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(
                ":/icons/icons/cross-mark-on-a-black-circle-background.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.screenfreeze.setIcon(icon5)
        self.screenfreeze.setFlat(True)
        self.screenfreeze.setObjectName("screenfreeze")
        self.back = QtWidgets.QPushButton(self)
        self.back.setEnabled(True)
        self.back.setGeometry(QtCore.QRect(0, 250, 30, 25))
        self.back.setMouseTracking(True)
        # self.back.setTabletTracking(True)
        # self.back.setAutoFillkey_background(False)
        self.back.setStyleSheet("")
        self.back.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-left.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.back.setIcon(icon6)
        self.back.setFlat(True)
        self.back.setObjectName("back")
        self.notif_pull = QtWidgets.QPushButton(self)
        self.notif_pull.setEnabled(True)
        self.notif_pull.setGeometry(QtCore.QRect(0, 50, 30, 25))
        self.notif_pull.setMouseTracking(True)
        # self.notif_pull.setTabletTracking(True)
        # self.notif_pull.setAutoFillkey_background(False)
        self.notif_pull.setStyleSheet("")
        self.notif_pull.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(":/icons/icons/bell-musical-tool.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.notif_pull.setIcon(icon7)
        self.notif_pull.setFlat(True)
        self.notif_pull.setObjectName("notif_pull")
        self.powerUI = QtWidgets.QPushButton(self)
        self.powerUI.setEnabled(True)
        self.powerUI.setGeometry(QtCore.QRect(0, 200, 30, 25))
        self.powerUI.setMouseTracking(True)
        # self.powerUI.setTabletTracking(True)
        # self.powerUI.setAutoFillkey_background(False)
        self.powerUI.setStyleSheet("")
        self.powerUI.setText("")
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(":/icons/icons/key_power.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.powerUI.setIcon(icon8)
        self.powerUI.setIconSize(QtCore.QSize(16, 16))
        self.powerUI.setCheckable(False)
        self.powerUI.setFlat(True)
        self.powerUI.setObjectName("powerUI")
        self.pinchinUI = QtWidgets.QPushButton(self)
        self.pinchinUI.setEnabled(False)
        self.pinchinUI.setGeometry(QtCore.QRect(0, 325, 30, 25))
        self.pinchinUI.setStyleSheet("")
        self.pinchinUI.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(
            QtGui.QPixmap(":/icons/icons/zoom-in.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.pinchinUI.setIcon(icon9)
        self.pinchinUI.setFlat(True)
        self.pinchinUI.setObjectName("pinchinUI")
        self.clipD2PC = QtWidgets.QPushButton(self)
        self.clipD2PC.setEnabled(True)
        self.clipD2PC.setGeometry(QtCore.QRect(0, 100, 30, 25))
        self.clipD2PC.setMouseTracking(True)
        # self.clipD2PC.setTabletTracking(True)
        # self.clipD2PC.setAutoFillkey_background(False)
        self.clipD2PC.setStyleSheet("")
        self.clipD2PC.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(
            QtGui.QPixmap(":/icons/icons/copy-document.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.clipD2PC.setIcon(icon10)
        self.clipD2PC.setFlat(True)
        self.clipD2PC.setObjectName("clipD2PC")
        self.potraitUI = QtWidgets.QPushButton(self)
        self.potraitUI.setEnabled(True)
        self.potraitUI.setGeometry(QtCore.QRect(0, 375, 30, 25))

        self.potraitUI.setStyleSheet("")
        self.potraitUI.setText("")
        icon11 = QtGui.QIcon()
        icon11.addPixmap(
            QtGui.QPixmap(":/icons/icons/vertical-resizing-option.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.potraitUI.setIcon(icon11)
        self.potraitUI.setFlat(True)
        self.potraitUI.setObjectName("potraitUI")
        self.landscapeUI = QtWidgets.QPushButton(self)
        self.landscapeUI.setEnabled(True)
        self.landscapeUI.setGeometry(QtCore.QRect(0, 400, 30, 25))

        self.landscapeUI.setStyleSheet("")
        self.landscapeUI.setText("")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(
            QtGui.QPixmap(":/icons/icons/horizontal-resize-option.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.landscapeUI.setIcon(icon12)
        self.landscapeUI.setFlat(True)
        self.landscapeUI.setObjectName("landscapeUI")
        self.home = QtWidgets.QPushButton(self)
        self.home.setEnabled(True)
        self.home.setGeometry(QtCore.QRect(0, 225, 30, 25))
        self.home.setMouseTracking(True)
        # self.home.setTabletTracking(True)
        # self.home.setAutoFillkey_background(False)
        self.home.setStyleSheet("")
        self.home.setText("")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(
            QtGui.QPixmap(":/icons/icons/home.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.home.setIcon(icon13)
        self.home.setFlat(True)
        self.home.setObjectName("home")
        self.vup = QtWidgets.QPushButton(self)
        self.vup.setEnabled(True)
        self.vup.setGeometry(QtCore.QRect(0, 150, 30, 25))
        self.vup.setMouseTracking(True)
        # self.vup.setTabletTracking(True)
        # self.vup.setAutoFillkey_background(False)
        self.vup.setStyleSheet("")
        self.vup.setText("")
        icon14 = QtGui.QIcon()
        icon14.addPixmap(
            QtGui.QPixmap(":/icons/icons/volume-up-interface-symbol.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.vup.setIcon(icon14)
        self.vup.setFlat(True)
        self.vup.setObjectName("vup")
        self.vdown = QtWidgets.QPushButton(self)
        self.vdown.setEnabled(True)
        self.vdown.setGeometry(QtCore.QRect(0, 175, 30, 25))
        self.vdown.setMouseTracking(True)
        # self.vdown.setTabletTracking(True)
        # self.vdown.setAutoFillkey_background(False)
        self.vdown.setStyleSheet("")
        self.vdown.setText("")
        icon15 = QtGui.QIcon()
        icon15.addPixmap(
            QtGui.QPixmap(":/icons/icons/reduced-volume.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.vdown.setIcon(icon15)
        self.vdown.setFlat(True)
        self.vdown.setObjectName("vdown")
        self.fullscreenUI = QtWidgets.QPushButton(self)
        self.fullscreenUI.setEnabled(True)
        self.fullscreenUI.setGeometry(QtCore.QRect(0, 25, 30, 25))
        self.fullscreenUI.setMouseTracking(True)
        # self.fullscreenUI.setTabletTracking(True)
        # self.fullscreenUI.setAutoFillkey_background(False)
        self.fullscreenUI.setStyleSheet("")
        self.fullscreenUI.setText("")
        icon16 = QtGui.QIcon()
        icon16.addPixmap(
            QtGui.QPixmap(":/icons/icons/increase-size-option.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.fullscreenUI.setIcon(icon16)
        self.fullscreenUI.setFlat(True)
        self.fullscreenUI.setObjectName("fullscreenUI")
        self.clipPC2D = QtWidgets.QPushButton(self)
        self.clipPC2D.setEnabled(True)
        self.clipPC2D.setGeometry(QtCore.QRect(0, 125, 30, 25))
        self.clipPC2D.setMouseTracking(True)
        # self.clipPC2D.setTabletTracking(True)
        # self.clipPC2D.setAutoFillkey_background(False)
        self.clipPC2D.setStyleSheet("")
        self.clipPC2D.setText("")
        icon17 = QtGui.QIcon()
        icon17.addPixmap(
            QtGui.QPixmap(":/icons/icons/copy-document(1).svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.clipPC2D.setIcon(icon17)
        self.clipPC2D.setFlat(True)
        self.clipPC2D.setObjectName("clipPC2D")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 410, 31, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(0, 420, 31, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.notif_collapse.raise_()
        self.menuUI.raise_()
        self.appswi.raise_()
        self.pinchoutUI.raise_()
        self.screenfreeze.raise_()
        self.back.raise_()
        self.notif_pull.raise_()
        self.powerUI.raise_()
        self.pinchinUI.raise_()
        self.clipD2PC.raise_()
        self.potraitUI.raise_()
        self.home.raise_()
        self.vup.raise_()
        self.vdown.raise_()
        self.fullscreenUI.raise_()
        self.clipPC2D.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.landscapeUI.raise_()

        _translate = QtCore.QCoreApplication.translate
        self.notif_collapse.setToolTip(
            _translate("self", "Expand notification panel"))
        self.menuUI.setToolTip(_translate("self", "Menu key"))
        self.appswi.setToolTip(
            _translate(
                "self",
                "press the APP_SWITCH button"))
        self.pinchoutUI.setToolTip(_translate(
            "self", "Pinch out in the screen"))
        self.back.setToolTip(_translate("self", "key_back key"))
        self.notif_pull.setToolTip(_translate(
            "self", "Expand notification panel"))
        self.powerUI.setToolTip(_translate("self", "Power on/off"))
        self.pinchinUI.setToolTip(
            _translate("self", "Pinch in the screen"))
        self.clipD2PC.setToolTip(
            _translate(
                "self",
                "Copy device clipbioard to PC"))
        self.potraitUI.setToolTip(_translate("self", "Potrait"))
        self.landscapeUI.setToolTip(_translate("self", "Landscape"))
        self.home.setToolTip(_translate("self", "Home key"))
        self.vup.setToolTip(_translate("self", "Volume Up"))
        self.fullscreenUI.setToolTip(_translate("self", "Fullscreen"))
        self.clipPC2D.setToolTip(
            _translate(
                "self",
                "Copy PC clipboard to Device"))
        self.label.setText(_translate("self", "...."))
        self.label_2.setText(_translate("self", "...."))
        # -----------------------------------

        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        # Connect signals
        # Launch UXMApper
    def init(self):
        self.ux = UXMapper()
        self.clipD2PC.clicked.connect(self.ux.copy_devpc)
        self.clipPC2D.clicked.connect(self.ux.copy_pc2dev)
        self.back.clicked.connect(self.ux.key_back)
        self.screenfreeze.clicked.connect(self.quitn)
        self.appswi.clicked.connect(self.ux.key_switch)
        self.menuUI.clicked.connect(self.ux.key_menu)
        self.home.clicked.connect(self.ux.key_home)
        self.notif_pull.clicked.connect(self.ux.expand_notifications)
        self.notif_collapse.clicked.connect(self.ux.collapse_notifications)
        self.fullscreenUI.clicked.connect(self.ux.fullscreen)
        self.powerUI.clicked.connect(self.ux.key_power)
        self.vup.clicked.connect(self.ux.key_volume_up)
        self.vdown.clicked.connect(self.ux.key_volume_down)
        self.potraitUI.clicked.connect(self.ux.reorientP)
        self.landscapeUI.clicked.connect(self.ux.reorientL)
        self.show()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except TypeError:
            pass

    def quitn(self):
        print("Bye Bye")
        sys.exit()


class SwipeUX(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        super(SwipeUX, self).__init__()
        self.oldPos = None
        self.ux = None
        self.setObjectName("SwipeUX")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.resize(70, 70)
        # -----------------------
        # =====================
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/res/ui/guiscrcpy_logo.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.setWindowIcon(icon)
        self.setStyleSheet(
            "QWidget{background-color: rgba(0,0,0,0);}\nQPushButton {\n"
            "border-radius: 15px;\n"
            "    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.495098, fy:0.5, stop:0.887255 rgba(35, 35, 35, 255), stop:0.901961 rgba(0, 0, 0, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "\n"
            "}\\n\n"
            "QPushButton:pressed {\n"
            "border-radius: 15px;\n"
            "\n"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 255, 255, 255), stop:1 rgba(0, 255, 152, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "   }\n"
            "QMainWindow{background-color: rgba(0,0,0,30);}\n"
            "QPushButton:hover {\n"
            "border-radius: 15px;\n"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 199, 199, 255), stop:1 rgba(0, 190, 113, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "}")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.swirt = QtWidgets.QPushButton(self.centralwidget)
        self.swirt.setGeometry(QtCore.QRect(40, 20, 30, 30))
        self.swirt.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-right.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.swirt.setIcon(icon1)
        self.swirt.setObjectName("swirt")
        self.swilf = QtWidgets.QPushButton(self.centralwidget)
        self.swilf.setGeometry(QtCore.QRect(0, 20, 30, 30))
        self.swilf.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-left.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.swilf.setIcon(icon2)
        self.swilf.setObjectName("swilf")
        self.swidn = QtWidgets.QPushButton(self.centralwidget)
        self.swidn.setGeometry(QtCore.QRect(20, 40, 30, 30))
        self.swidn.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-down.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.swidn.setIcon(icon3)
        self.swidn.setObjectName("swidn")
        self.swiup = QtWidgets.QPushButton(self.centralwidget)
        self.swiup.setGeometry(QtCore.QRect(20, 0, 30, 30))
        self.swiup.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-up.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.swiup.setIcon(icon4)
        self.swiup.setObjectName("swiup")
        self.setCentralWidget(self.centralwidget)
        # -----------------
        # ================

        self.oldpos = self.pos()
        self.swiup.pressed.connect(self.swipup)
        self.swidn.pressed.connect(self.swipdn)
        self.swilf.pressed.connect(self.swipleft)
        self.swirt.pressed.connect(self.swipright)

    def init(self):
        self.ux = UXMapper()
        self.show()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing)
        qp.setPen(Qt.NoPen)
        qp.setBrush(QtGui.QColor(0, 0, 0, 127))
        qp.drawEllipse(0, 0, 70, 70)
        qp.end()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.oldPos)

            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except TypeError:
            pass

    def swipdn(self):
        logging.debug("Passing SWIPE DOWN")
        dimValues = self.ux.android_dimensions
        posy = int(dimValues[1]) - 200
        posx = int(dimValues[0])
        newposx = posx / 2  # find center
        self.ux.do_swipe(newposx, 200, newposx, posy)

    def swipup(self):
        logging.debug("Passing SWIPE UP")
        dimValues = self.ux.android_dimensions
        posy = int(dimValues[1]) - 100
        posx = int(dimValues[0])
        newposx = int(posx / 2)  # find center
        self.ux.do_swipe(newposx, posy, newposx, 200)

    def swipleft(self):
        logging.debug("Passing SWIPE LEFT")
        dimValues = self.ux.android_dimensions
        posy = int(dimValues[1])
        posx = int(dimValues[0]) - 10
        newposy = int(posy / 2)  # find center
        self.ux.do_swipe(10, newposy, posx, newposy)

    def swipright(self):
        logging.debug("Passing SWIPE RIGHT")
        dimValues = self.ux.android_dimensions
        posy = int(dimValues[1])
        posx = int(dimValues[0]) - 10
        newposy = int(posy / 2)  # find center
        self.ux.do_swipe(posx, newposy, 10, newposy)


class Panel(QMainWindow):
    # there was a Dialog in the bracket
    def __init__(self):

        super(Panel, self).__init__()

        # self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
        # self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

        self.setObjectName("self")
        self.resize(328, 26)
        self.oldPos = None
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/res/ui/guiscrcpy_logo.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.setWindowIcon(icon)
        self.setStyleSheet(
            "\n"
            ".QPushButton {\n"
            "border-radius: 1px;\n"
            "color: rgb(0, 0, 0);\n"
            " \n"
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0.915182, x2:0, y2:0.926, stop:0.897059 rgba(41, 41, 41, 255), stop:1 rgba(30, 30, 30, 255));\n"
            "                    }\n"
            "\n"
            "QPushButton:pressed {\n"
            "border-radius: 5px;\n"
            "                      \n"
            "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 255, 255, 255), stop:1 rgba(0, 255, 152, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "                        }\n"
            "QPushButton:hover {\n"
            "border-radius: 5px;\n"
            "                      \n"
            "    background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(0, 199, 199, 255), stop:1 rgba(0, 190, 113, 255));\n"
            "color: rgb(0, 0, 0);\n"
            "                        }\n"
            "")
        self.backk = QtWidgets.QPushButton(self)
        self.backk.setEnabled(True)
        self.backk.setGeometry(QtCore.QRect(210, 0, 51, 25))
        self.backk.setStyleSheet("")
        self.backk.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/icons/icons/chevron-sign-left.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.backk.setIcon(icon1)
        self.backk.setObjectName("backk")
        self.powerUII = QtWidgets.QPushButton(self)
        self.powerUII.setEnabled(True)
        self.powerUII.setGeometry(QtCore.QRect(20, 0, 61, 25))
        self.powerUII.setStyleSheet("")
        self.powerUII.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/icons/icons/key_power.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.powerUII.setIcon(icon2)
        self.powerUII.setCheckable(False)
        self.powerUII.setObjectName("powerUII")
        self.menuUII = QtWidgets.QPushButton(self)
        self.menuUII.setEnabled(True)
        self.menuUII.setGeometry(QtCore.QRect(90, 0, 51, 25))
        self.menuUII.setStyleSheet("")
        self.menuUII.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/icons/icons/reorder-option.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.menuUII.setIcon(icon3)
        self.menuUII.setObjectName("menuUII")
        self.vdownn = QtWidgets.QPushButton(self)
        self.vdownn.setEnabled(True)
        self.vdownn.setGeometry(QtCore.QRect(270, 0, 31, 25))
        self.vdownn.setStyleSheet("")
        self.vdownn.setText("")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/icons/icons/reduced-volume.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.vdownn.setIcon(icon4)
        self.vdownn.setObjectName("vdownn")
        self.homee = QtWidgets.QPushButton(self)
        self.homee.setEnabled(True)
        self.homee.setGeometry(QtCore.QRect(140, 0, 71, 25))
        self.homee.setStyleSheet("")
        self.homee.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(":/icons/icons/home.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off)
        self.homee.setIcon(icon5)
        self.homee.setObjectName("homee")
        self.vupp = QtWidgets.QPushButton(self)
        self.vupp.setEnabled(True)
        self.vupp.setGeometry(QtCore.QRect(300, 0, 31, 25))
        self.vupp.setStyleSheet("")
        self.vupp.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(":/icons/icons/volume-up-interface-symbol.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.vupp.setIcon(icon6)
        self.vupp.setObjectName("vupp")
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, -10, 20, 41))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.homee.raise_()
        self.backk.raise_()
        self.powerUII.raise_()
        self.menuUII.raise_()
        self.vdownn.raise_()
        self.vupp.raise_()
        self.label.raise_()
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Panel", "guiscrcpy"))
        self.backk.setToolTip(_translate("Panel", "key_back key"))
        self.powerUII.setToolTip(_translate("Panel", "Power on/off"))
        self.menuUII.setToolTip(_translate("Panel", "Menu key"))
        self.vdownn.setToolTip(_translate("Panel", "Volume Up"))
        self.homee.setToolTip(_translate("Panel", "Home key"))
        self.label.setText(_translate("Panel", "::"))

        # -----------------------------------
        self.oldpos = self.pos()
        # Ui_Panel.__init__(self)
        # Dialog.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )

    def init(self):
        self.ux = UXMapper()
        self.backk.clicked.connect(self.ux.key_back)
        self.menuUII.clicked.connect(self.ux.key_menu)
        self.homee.clicked.connect(self.ux.key_home)
        self.powerUII.clicked.connect(self.ux.key_power)
        self.vupp.clicked.connect(self.ux.key_volume_up)
        self.vdownn.clicked.connect(self.ux.key_volume_down)
        self.show()


    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QPoint(event.globalPos() - self.oldPos)

            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()
        except TypeError:
            pass

# END TOOLKIT



def checkProcessRunning(processName):
    # Iterate over the all the running process
    for proc in psutil.process_iter():
        try:
            # Check if process name contains the given name string.
            if processName.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


class MyApp(Ui_MainWindow):
    def __init__(self, MainWindow):

        super(MyApp, self).__init__()
        # uic.loadUi(qtCreatorFile, self)
        
        # self.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
        # self.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons


        Ui_MainWindow.__init__(self)
        self.setupUi(MainWindow)

        # self.setupUi(self)
        # self.menuAbout.itemPressed.connect(self.menu_about)

        # check if process Scrcpy is running right now in while loop
        logging.debug(
            "Options received by class are : {} {} {} {} {} ".format(
            config['bitrate'],
            config['dimension'],
            config['swtouches'],
            config['dispRO'],
            config['fullscreen'],
        ))
        self.dial.setValue(int(config['bitrate']))
        if config['swtouches']:
            self.showTouches.setChecked(True)
        else:
            self.showTouches.setChecked(False)
        if config['dispRO']:
            self.displayForceOn.setChecked(True)
        else:
            self.displayForceOn.setChecked(False)
        if config['dimension'] is not None:
            self.dimensionDefaultCheckbox.setChecked(False)
            try:
                self.dimensionSlider.setValue(config['dimension'])
            except TypeError:
                self.dimensionDefaultCheckbox.setChecked(True)
        if config['fullscreen']:
            self.fullscreen.setChecked(True)
        else:
            self.fullscreen.setChecked(False)
        if checkProcessRunning("scrcpy"):
            logging.debug("SCRCPY RUNNING")
            self.runningNot.setText("SCRCPY SERVER RUNNING")
        else:
            logging.debug("SCRCPY SERVER IS INACTIVE")
            self.runningNot.setText("SCRCPY SERVER NOT RUNNING")

        # CONNECT DIMENSION CHECK BOX TO STATE CHANGE
        self.dimensionDefaultCheckbox.stateChanged.connect(
            self.dimensionChange)
        self.build_label.setText("Build " + str(build))

        # DIAL CTRL GRP
        self.dial.sliderMoved.connect(self.dial_text_refresh)
        self.dial.sliderReleased.connect(self.dial_text_refresh)
        # DIAL CTRL GRP

        # MAIN EXECUTE ACTION
        self.executeaction.clicked.connect(self.start_act)
        try:
            if config['extra']:
                self.flaglineedit.setText(config['extra'])
            else:
                pass
        except:
            pass

        # show subwindows
        self.swipe_instance = SwipeUX()  # Load swipe UI
        self.panel_instance = Panel()
        self.side_instance = MyAppv()

        self.quit.clicked.connect(self.quitAct)
        self.dimensionText.setText("DEFAULT")
        config['bitrate'] = int(self.dial.value())
        self.bitrateText.setText(" " + str(config['bitrate']) + "KB/s")
        self.pushButton.setText("RESET")
        self.pushButton.clicked.connect(self.reset)
        self.abtme.clicked.connect(self.openme)
        self.abtgit.clicked.connect(self.opengit)
        self.usbaud.clicked.connect(self.usbaudi)
        self.mapnow.clicked.connect(self.mapp)


    def mapp(self):
        if(os.path.exists(cfgpath + "guiscrcpy.mapper.json")):
            from guiscrcpy import mapper
            mapper.file_check()
        else:
            logging.warning(
                "guiscrcpy ~ mapper is not initialized. Initialize by running" +
                "$ guiscrcpy-mapper" + "reset points by" + "$ guiscrcpy-mapper -r")

    def fin(self):
        result = []
        try:
            from guiscrcpy import __path__ as xz
            str1 = xz
        except:
            str1 = []
        for path in os.getenv('PATH').split(":")+str1:
            logging.debug("PATH: {}".format(path))
            for files in os.listdir(path):
                logging.debug("FILE: {}".format(files))
                if "mapper.py" in files:
                    result.append(os.path.join(path, "mapper.py"))
                    break
            else:
                logging.debug("Mapper.py not found")

        return result

    def usbaudi(self):
        logging.debug("Called usbaudio")
        runnow = po("usbaudio", shell=True, stdout=PIPE, stderr=PIPE)

    def openme(self):
        webbrowser.open("https://srevinsaju.github.io")

    def opengit(self):
        webbrowser.open("https://github.com/srevinsaju/guiscrcpy")

    def about(self):
        abtBox = QMessageBox().window()
        abtBox.about(
            self.pushButton,
            "Info",
            "Please restart guiscrcpy to reset the settings. guiscrcpy will now exit",
        )
        abtBox.addButton("OK", abtBox.hide())
        abtBox.show()

    def reset(self):

        os.remove(cfgpath + jsonf)
        logging.debug("CONFIGURATION FILE REMOVED SUCCESSFULLY")
        logging.debug("RESTART")
        msgBox = QMessageBox().window()
        msgBox.about(
            self.pushButton,
            "Info",
            "Please restart guiscrcpy to reset the settings. guiscrcpy will now exit",
        )
        msgBox.addButton("OK", self.quitAct())
        msgBox.show()

    def quitAct(self):

        sys.exit()

    def menu_about(self):
        pass

    def dimensionChange(self):

        if self.dimensionDefaultCheckbox.isChecked():
            self.dimensionSlider.setEnabled(False)
            config['dimension'] = None
            self.dimensionText.setText("DEFAULT")

        else:
            self.dimensionSlider.setEnabled(True)
            config['dimension'] = int(self.dimensionSlider.value())

            self.dimensionText.setText(
                " " + str(config['dimension']) + "px")
            self.dimensionSlider.sliderMoved.connect(
                self.slider_text_refresh)
            self.dimensionSlider.sliderReleased.connect(
                self.slider_text_refresh)

    def slider_text_refresh(self):
        config['dimension'] = int(self.dimensionSlider.value())
        self.dimensionText.setText(str(config['dimension']) + "px")
        pass

    def dial_text_refresh(self):
        config['bitrate'] = int(self.dial.value())
        self.bitrateText.setText(str(config['bitrate']) + "KB/s")
        pass

    def start_act(self):

        self.runningNot.setText("CHECKING DEVICE CONNECTION")
        timei = time.time()
        self.progressBar.setValue(5)
        adb_chk = po(increment + "adb devices", shell=True, stdout=PIPE)
        output = adb_chk.stdout.readlines()

        needed_output = output[1]

        deco = needed_output.decode("utf-8")
        det = deco.split("\t")
        logging.debug("ADB: {}".format(det))

        if det[0] == "\n":
            self.runningNot.setText("DEVICE IS NOT CONNECTED")
            self.progressBar.setValue(0)
            return 0
        try:
            exc = det[1].find("device")
        except IndexError:
            self.runningNot.setText("DEVICE IS NOT CONNECTED")
            self.progressBar.setValue(0)
            return 0

        if det[1].find("device") > -1:
            self.runningNot.setText(
                "DEVICE " + str(det[0]) + " IS CONNECTED")
            self.progressBar.setValue(10)

        elif det[1][:-1] == "unauthorized":
            self.runningNot.setText(
                "DEVICE IS UNAUTHORIZED. PLEASE CLICK 'OK' ON DEVICE WHEN ASKED FOR"
            )
            self.progressBar.setValue(0)
            return 0

        else:
            self.runningNot.setText(
                "DEVICE CONNECTED BUT FAILED TO ESTABLISH CONNECTION"
            )
            self.progressBar.setValue(0)
            return 0
        # check if the defaultDimension is checked or not for giving signal

        ux = UXMapper()
        dimValues = ux.get_dimensions()

        self.progressBar.setValue(15)

        if self.dimensionDefaultCheckbox.isChecked():
            self.dimensionSlider.setEnabled(False)
            self.dimensionText.setText("DEFAULT")
            config['dimension'] = None

        else:
            self.dimensionSlider.setEnabled(True)
            config['dimension'] = int(self.dimensionSlider.value())
            self.dimensionSlider.setValue(config['dimension'])
            self.dimensionText.setText(str(config['dimension']) + "px")

        # check if the defaultDimension is checked or not for giving signal
        self.progressBar.setValue(20)
        """
        proc =run(["scrcpy"], stdout=PIPE,
                                stderr=PIPE)
        out, err = proc.stdout, proc.stderr
        out_decoded = out.decode("utf-8")
        tmp.append(out_decoded)
        self.terminal.setText(str(tmp))
        """

        # process dimension
        if config['dimension'] is None:
            self.options = " "
            pass
        elif config['dimension'] is not None:
            self.options = " -m " + str(config['dimension'])
        else:
            self.options = ""

        self.progressBar.setValue(25)
        # CHECK BOX GROUP CONNECT
        if self.aotop.isChecked():
            self.options += " --always-on-top"
        if self.fullscreen.isChecked():
            self.options += " -f"
            config['fullscreen'] = True
        else:
            config['fullscreen'] = False
        """
        if self.keepdisplayRO.isChecked():
            self.options += " --no-control"
        """
        self.progressBar.setValue(30)
        if self.showTouches.isChecked():
            self.options += " --show-touches"
            config['swtouches'] = True

            """        if self.keepdisplayRO.isChecked():
            self.options += " --turn-screen-off"
            """

        else:
            config['swtouches'] = False
        if self.recScui.isChecked():
            self.options += " -r " + str(int(time.time())) + ".mp4 "

            """        if self.keepdisplayRO.isChecked():
            self.options += " --turn-screen-off"
            """
        if self.displayForceOn.isChecked():
            self.options += " -S"
            config['dispRO'] = True
            """        if self.keepdisplayRO.isChecked():
            self.options += " --turn-screen-off"
            """

        else:
            config['dispRO'] = False

        self.options += " -b " + str(int(self.dial.value())) + "K"
        config['bitrate'] = int(self.dial.value())
        self.progressBar.setValue(40)

        # self.myLine = startScrcpy(self.options)
        # self.connect(self.myLine, SIGNAL("update_terminal(QString)"), self.update_terminal)
        logging.debug("CONNECTION ESTABLISHED")
        self.progressBar.setValue(50)

        logging.debug("Flags passed to scrcpy engine : " + self.options)
        self.progressBar.setValue(75)

        # get additional flags from QLineEdit self.flaglineedit
        config['extra'] = self.flaglineedit.text()

        # show subwindows
        self.swipe_instance.init()  # show Swipe UI
        self.panel_instance.init()
        self.side_instance.init()
        # run scrcpy usng subprocess
        backup = po(
            increment + "scrcpy " +
            str(self.options) + " " + str(config['extra']),
            shell=True,
            stdin=PIPE,
            stdout=PIPE,
            stderr=STDOUT,
        )
        # StartScrcpy(options=self.options
        timef = time.time()
        eta = timef - timei
        print("SCRCPY is launched in", eta, "seconds")
        self.progressBar.setValue(100)

        with open(cfgpath + jsonf, 'w') as f:
            json.dump(config, f)
        logging.debug("Configuration file at {}".format(cfgpath + jsonf, "."))

        if self.notifChecker.isChecked():
            logging.warning("Launching notification auditor")
            # ------------
            # Begin notif auditor
            # --------
            import pystray
            from PIL import Image, ImageDraw

            def callback(icon):
                if platform.system() == "Windows":
                    logging.warning(
                        "Notif Auditor is experimental on Windows. If you wish to help out on this issue. Open a PR on github"
                    )
                    notif = po(
                        increment +
                        "adb shell dumpsys notification | findstr ticker ",
                        stdout=PIPE,
                        shell=True,
                    )
                else:
                    "Notif Auditor is experimental on Linux. If you wish to help out on this issue. Open a PR on github"
                    notif = po(
                        increment +
                        "adb shell dumpsys notification | grep ticker | cut -d= -f2",
                        stdout=PIPE,
                        shell=True,
                    )
                image = Image.new("RGBA", (128, 128), (255, 255, 255, 255))
                # loop this block --->
                var1 = notif.stdout.readlines()
                var2 = var1
                while True:
                    if platform.system() == "Windows":
                        logging.warning(
                            "Notif Auditor is experimental on Windows. If you wish to help out on this issue. Open a PR on github"
                        )
                        notif = po(
                            increment +
                            "adb shell dumpsys notification | findstr ticker ",
                            stdout=PIPE,
                            shell=True,
                        )
                    else:
                        "Notif Auditor is experimental on Linux. If you wish to help out on this issue. Open a PR on github"
                        notif = po(
                            increment +
                            "adb shell dumpsys notification | grep ticker | cut -d= -f2",
                            stdout=PIPE,
                            shell=True,
                        )
                    image = Image.new(
                        "RGBA", (128, 128), (255, 255, 255, 255))
                    # loop this block --->
                    var1 = notif.stdout.readlines()

                    # <----
                    if len(var1) > len(var2):
                        d = ImageDraw.Draw(image)
                        d.rectangle([0, 255, 128, 128], fill="green")
                        icon.icon = image
                        time.sleep(600)
                        var2 = var1

            image = Image.new("RGBA", (128, 128), (255, 255, 255, 255))

            icon = pystray.Icon("Test Icon 1", image)

            icon.visible = True
            icon.run(setup=callback)
            # End notif auditor


def bootstrap0():

    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
    QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()  # Create windwo
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # windoww = QtWidgets.QMainWindow()
    # windowww = QtWidgets.QMainWindow()
    prog = MyApp(window)

    # file = QFile(":/dark.qss")
    # file.open(QFile.ReadOnly | QFile.Text)
    # stream = QTextStream(file)
    # app.setStyleSheet(stream.readAll())
    splash_pix = QPixmap(":/res/ui/guiscrcpy-branding.png")
    splash = QtWidgets.QSplashScreen(splash_pix)
    splash.setMask(splash_pix.mask())
    splash.show()
    app.processEvents()

    # -------------------
    # chk ADB devices prehandle
    # -------------------
    adb_chk8 = po(increment + "adb devices", shell=True, stdout=PIPE)
    output8 = adb_chk8.stdout.readlines()
    try:
        needed_output8 = output8[1]
        deco8 = needed_output8.decode("utf-8")
        det8 = deco8.split("\t")
        logging.debug("ADB: {}".format(deco8))

    except IndexError:
        logging.error("ADB is not installed on your system")

    # ------------------
    app.processEvents()


    # panel = Panel(windoww)

    window.show()
    splash.hide()
    # windowww.show()
    # windoww.show()
    app.exec_()
    # appo.exec_()
    sys.exit()


if __name__ == "__main__":
    try:
        from guiscrcpy import __path__
        patz = list(__path__)[0]
        sys.path.append(patz)
        sys.path.append('')
    except ModuleNotFoundError:
        pass
    sys.path.append('')

    bootstrap0()


def bootstrap():
    from guiscrcpy import __path__
    patz1 = list(__path__)[0]
    sys.path.append(patz1)
    if (platform.system() == "Windows"):
        pythonexec = "python"
    else:
        pythonexec = "python3"
    ar = ""
    for i in sys.argv[1:]:
        ar += " " + i + " "
    bootstrap0()