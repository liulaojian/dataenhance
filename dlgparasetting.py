from dlgparasetting_ui import Ui_Dialog
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DlgParaSetting(QDialog, Ui_Dialog):
    def __init__(self, outDir: str, parent=None):
        super(DlgParaSetting, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)
        self.pushButton_OutDir.clicked.connect(self.onPushButton_OutDirClick)
        self.pushButton_Ok.clicked.connect(self.onPushButton_OkClick)
        self.pushButton_Cancle.clicked.connect(self.onPushButton_CancelClick)
        self.lineEdit_OutDir.setText(outDir)
        self.strOutDir = outDir

    def onPushButton_OutDirClick(self):
        sel_dir_str = QFileDialog.getExistingDirectory(None, "", self.strOutDir, QFileDialog.ShowDirsOnly)
        if sel_dir_str is not None:
            self.strOutDir = sel_dir_str
            self.lineEdit_OutDir.setText(self.strOutDir)
        return

    def onPushButton_OkClick(self):
        self.accept()
        return

    def onPushButton_CancelClick(self):
        self.reject()
        return
