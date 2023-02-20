from dlgpara_ui import Ui_DlgPara
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class DlgPara(QDialog, Ui_DlgPara):
    def __init__(self, parent=None):
        super(DlgPara, self).__init__(parent)
        self.setupUi(self)
        self.rotateNums = 0
        self.rotateAngle = 0.0
        self.garyColor = 0

        self.paraDynamicBrightContrast: dict = {"dynamicBrightContrast": True, "rangeBright": 0.2,
                                                "rangeContrast":  0.2, "prop": 1.0}

        self.paraDynamicHueSatLight: dict = {"dynamicHueSatLight": True, "rangeHue": 10, "rangeSat": 15,
                                             "rangeLight": 10, "prop": 0.5}

        self.paraDynamicGamma: dict = {"dynamicGamma": True, "rangeGammmaLow": 80, "rangGammaHigh": 120, "prop": 0.3}


        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)

        self.cmb_grayColor.addItem("灰度图")
        self.cmb_grayColor.setItemData(0, 0)

        self.cmb_grayColor.addItem("彩色图")
        self.cmb_grayColor.setItemData(1, 1)
        self.cmb_grayColor.setCurrentIndex(0)

        self.pushButton_Ok.clicked.connect(self.onOkClick)
        self.pushButton_Cancel.clicked.connect(self.onCancelClick)

        return

    def onOkClick(self):

        self.rotateAngle = self.spinBox_Angle.value()
        self.rotateNums = self.spinBox_Nums.value()

        index = self.cmb_grayColor.currentIndex()
        self.garyColor = self.cmb_grayColor.itemData(index)

        self.paraDynamicBrightContrast["dynamicBrightContrast"] = self.checkBox_BrightContrast.isChecked()
        self.paraDynamicBrightContrast["rangeBright"] = self.doubleSpinBox_Bright.value()
        self.paraDynamicBrightContrast["rangeContrast"] = self.doubleSpinBox_Contrast.value()
        self.paraDynamicBrightContrast["prop"] = self.doubleSpinBox_Prob_BC.value()

        self.paraDynamicHueSatLight["dynamicHueSatLight"] = self.checkBox_HueSB.isChecked()
        self.paraDynamicHueSatLight["rangeHue"] = self.spinBox_Hue.value()
        self.paraDynamicHueSatLight["rangeSat"] = self.spinBox_Saturation.value()
        self.paraDynamicHueSatLight["rangeLight"] = self.spinBox_Light.value()
        self.paraDynamicHueSatLight["prop"] = self.doubleSpinBox_Prob_HSB.value()

        if self.spinBox_GammaLow.value() >= self.spinBox_GammaHigh.value():
            QMessageBox.about(None, "警告", "Gamma低值不能大于等于Gamma高值")
            return
        self.paraDynamicGamma["dynamicGamma"] = self.checkBox_Gamma.isChecked()
        self.paraDynamicGamma["rangeGammmaLow"] = self.spinBox_GammaLow.value()
        self.paraDynamicGamma["rangGammaHigh"] = self.spinBox_GammaHigh.value()
        self.paraDynamicGamma["prop"] = self.doubleSpinBox_Prob_Gamma.value()

        self.accept()

        return

    def onCancelClick(self):
        self.reject()
        return
