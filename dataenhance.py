import sys
import os
from mainwindow import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from marktype import *
from markHandle import *
from dlgpara import *
from utils import *
from markHandleThread import *
from dlgparasetting import *


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.pushButton_OpenDir.clicked.connect(self.onOpenDirClick)
        self.pushButton_Handle.clicked.connect(self.onDataHandleClick)

        self.timer = QTimer()
        self.timer.timeout.connect(self.timerFun)
        self.listMarkFileInfo = []

        self.tableView.verticalHeader().setVisible(False)
        self.theModel = QStandardItemModel(1, 4, self)
        self.theSelection = QItemSelectionModel(self.theModel)
        self.tableView.setModel(self.theModel)
        self.tableView.setSelectionModel(self.theSelection)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.theModel.setHorizontalHeaderLabels(["id", "图片路径", "xml路径", "是否处理"])

        self.labelInfo = QLabel("", self)
        self.statusbar.addWidget(self.labelInfo)

        self.actionParaSetting.triggered.connect(self.onActionParaSetting)

        self.strIniFilePath = os.getcwd()
        self.strIniFilePath += "/dataenhance.ini"
        self.iniSetting = QSettings(self.strIniFilePath, QSettings.IniFormat)
        self.outDir = self.iniSetting.value("Data/OutDir")

        print(QStyleFactory.keys())
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        if self.outDir is None:
            self.outDir = os.getcwd()

        self.nowRotateAngle = 0.0
        self.nowRotateNums = 0
        self.nowGrayColor = 0
        self.nowOutDirPath = ""
        self.nowDynamicBrightContrast: dict = {}

        self.nowDynamicHueSatLight: dict = {}

        self.nowDynamicGamma: dict = {}

        self.markHandleThead: MarkHandleThread = None
        return



    def onActionParaSetting(self):
        dlg = DlgParaSetting(self.outDir)
        ret = dlg.exec()

        if ret != QDialog.Accepted:
            return

        self.outDir = dlg.strOutDir

        self.iniSetting.beginGroup("Data")
        self.iniSetting.setValue("OutDir", self.outDir)
        self.iniSetting.endGroup()
        return

    def onOpenDirClick(self):
        cur_path = os.getcwd() #QCoreApplication.applicationDirPath()
        sel_dir_str = QFileDialog.getExistingDirectory(None, "", cur_path, QFileDialog.ShowDirsOnly)
        if sel_dir_str is not None:
            cur_dir = QDir(sel_dir_str)
            file_list = cur_dir.entryList(QDir.Dirs | QDir.NoDotDot)
            findAnnotations = False
            findJPEGImages = False
            for file_str in file_list:
                if file_str.find("Annotations") >= 0:
                    findAnnotations = True
                elif file_str.find("JPEGImages") >= 0:
                    findJPEGImages = True
            if not findAnnotations or not findJPEGImages:
                QMessageBox.about(None, "警告", "选择的目录不是标注文件目录")
                return
            strAnnotationsDir = sel_dir_str
            strAnnotationsDir += "/Annotations"
            print(strAnnotationsDir)
            dirAnnotations = QDir(strAnnotationsDir)
            filtersAnnotations = ["*.xml"]
            dirAnnotations.setNameFilters(filtersAnnotations)
            dirAnnotations.setFilter(QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot)
            xmlFileList = dirAnnotations.entryList()

            strJPEGDir = sel_dir_str
            strJPEGDir += "/JPEGImages"
            print(strJPEGDir)
            dirJPEG = QDir(strJPEGDir)
            filtersJPEG = ["*.png", "*.jpg"]
            dirJPEG.setNameFilters(filtersJPEG)
            dirJPEG.setFilter(QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot)
            picFileList = dirJPEG.entryList()

            self.listMarkFileInfo.clear()

            m_id = 0
            for picFile in picFileList:
                fileInfo = QFileInfo(picFile)
                strBaseName = fileInfo.completeBaseName()
                strXmlFile = strBaseName+".xml"
                if strXmlFile in xmlFileList:
                    markFileInfo = MarkFileInfo()
                    markFileInfo.id = m_id
                    markFileInfo.strPicPath = strJPEGDir
                    markFileInfo.strPicPath += "/"
                    markFileInfo.strPicPath += picFile

                    markFileInfo.strXmlPath = strAnnotationsDir
                    markFileInfo.strXmlPath += "/"
                    markFileInfo.strXmlPath += strXmlFile

                    self.listMarkFileInfo.append(markFileInfo)
                    m_id += 1
        self.timer.start(100)
        return

    def onDataHandleClick(self):
        if len(self.listMarkFileInfo) == 0:
            return

        if self.markHandleThead is not None:
            if self.markHandleThead.isRunning():
                QMessageBox.about(None, "警告", "上次任务还未完成")
                return
            else:
                self.markHandleThead = None

        dlg = DlgPara()

        ret = dlg.exec()

        if ret != QDialog.Accepted:
            return

        self.nowRotateAngle = dlg.rotateAngle
        self.nowRotateNums = dlg.rotateNums
        self.nowGrayColor = dlg.garyColor

        self.nowDynamicBrightContrast = dlg.paraDynamicBrightContrast

        self.nowDynamicHueSatLight = dlg.paraDynamicHueSatLight

        self.nowDynamicGamma = dlg.paraDynamicGamma

        self.nowOutDirPath = self.BuildOutDir()  #"E:/code_python/dataenhance"

        self.markHandleThead = MarkHandleThread(self)

        self.markHandleThead.resultHandleInfo.connect(self.handleMarkResults)
        self.markHandleThead.resultHandleFinish.connect(self.handleMarkFinish)
        self.markHandleThead.start()
        self.labelInfo.setText("开始处理...")
        return

    def handleMarkResults(self, info: str):
        strInfo = "正在处理:"
        strInfo += info
        self.labelInfo.setText(strInfo)
        return

    def handleMarkFinish(self, info: str):
        self.labelInfo.setText(info)
        result = QMessageBox.question(None, "", "是否打开处理后的目录")
        if result == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.nowOutDirPath))
        return

    def doMarkHandle(self):
        if len(self.listMarkFileInfo) == 0:
            return

        for i in range(len(self.listMarkFileInfo)):
            markHandle.doHandleMark(self.listMarkFileInfo[i], self.nowOutDirPath, self.nowRotateAngle,
                                    self.nowRotateNums, self.nowGrayColor, i, self.nowDynamicBrightContrast, self.nowDynamicHueSatLight, self.nowDynamicGamma)
            self.markHandleThead.resultHandleInfo.emit(self.listMarkFileInfo[i].strPicPath)
        self.markHandleThead.resultHandleFinish.emit("")
        return

    def BuildOutDir(self) -> str:

        curPath = self.outDir #os.getcwd() #QCoreApplication.applicationDirPath()
        curPath = curPath.replace('\\', '/')

        strYMDHMS = Utils.GetYMDHMS()

        strOutDirName = "lens_"
        strOutDirName += strYMDHMS

        strOutDirPath = curPath
        strOutDirPath += "/"
        strOutDirPath += strOutDirName

        outdir = QDir(strOutDirPath)
        if not outdir.exists():
            curdir = QDir(curPath)
            curdir.mkdir(strOutDirName)

        outdir.mkdir("Annotations")
        outdir.mkdir("JPEGImages")

        return strOutDirPath



    def refresh(self):
        self.theModel.removeRows(0, self.theModel.rowCount())

        for i in range(len(self.listMarkFileInfo)):
            aItem = QStandardItem(str(self.listMarkFileInfo[i].id))
            self.theModel.setItem(i, 0, aItem)
            aItem = QStandardItem(self.listMarkFileInfo[i].strPicPath)
            self.theModel.setItem(i, 1, aItem)
            aItem = QStandardItem(self.listMarkFileInfo[i].strXmlPath)
            self.theModel.setItem(i, 2, aItem)
            if self.listMarkFileInfo[i].bHandled:
                aItem = QStandardItem("已处理")
            else:
                aItem = QStandardItem("未处理")
            self.theModel.setItem(i, 3, aItem)
        return

    def timerFun(self):
        self.timer.stop()
        self.refresh()
        return


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
