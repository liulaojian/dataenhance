from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from dataenhance import MainWindow


class MarkHandleThread(QThread):
    resultHandleInfo = pyqtSignal(str)
    resultHandleFinish = pyqtSignal(str)

    def __init__(self, mainwin: MainWindow, parent=None):
        super(MarkHandleThread, self).__init__(parent)
        self.mainWindow: MainWindow = mainwin
        return

    def run(self):
        if self.mainWindow is not None:
            self.mainWindow.doMarkHandle()
        return
