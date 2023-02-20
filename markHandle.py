import sys
import albumentations
import cv2
from PyQt5.QtCore import *
from PyQt5.QtXml import *
from marktype import *


class MarkHandle:
    def __init__(self):
        return

    def doHandleMark(self, markFileInfo, outDirPath, rotateAngle, rotateNums, grayColor, id_, paraDynamicBrightContrast: dict, paraDynamicHueSatLight: dict, paraDynamicGamma: dict):
        self.doParseMarkXml(markFileInfo)
        listMarkRotateInfo = []
        index: int = id_*(rotateNums+1)
        markRotateInfo: MarkRotateInfo = self.buildMarkRotateInfoFromMarkFileInfo(markFileInfo)
        markRotateInfo.id = index
        index += 1

        fileinfo = QFileInfo(markFileInfo.strPicPath)
        strPicBaseName = fileinfo.completeBaseName()
        strPicSuffix = fileinfo.suffix()

        strPicFileName = str(markRotateInfo.id+1)
        strPicFileName += "."
        strPicFileName += strPicSuffix
        strPicFilePath = outDirPath
        strPicFilePath += "/JPEGImages/"
        strPicFilePath += strPicFileName

        strXmlContent = self.doBuildMarkXml(markRotateInfo, strPicFileName, strPicFilePath, grayColor)
        markRotateInfo.strXmlContent = strXmlContent
        listMarkRotateInfo.append(markRotateInfo)

        for i in range(rotateNums):
            angle: float = rotateAngle*(i+1)
            markRotateInfo = self.doGenMarkRotateInfo(markFileInfo, angle, grayColor,paraDynamicBrightContrast, paraDynamicHueSatLight, paraDynamicGamma)
            markRotateInfo.id = index
            index += 1

            strPicFileName = str(markRotateInfo.id + 1)
            strPicFileName += "."
            strPicFileName += strPicSuffix
            strPicFilePath = outDirPath
            strPicFilePath += "/JPEGImages/"
            strPicFilePath += strPicFileName

            strXmlContent = self.doBuildMarkXml(markRotateInfo, strPicFileName, strPicFilePath, grayColor)
            markRotateInfo.strXmlContent = strXmlContent
            listMarkRotateInfo.append(markRotateInfo)

        strXmlOutDir = outDirPath
        strXmlOutDir += "/Annotations/"

        strPicOutDir = outDirPath
        strPicOutDir += "/JPEGImages/"

        for i in range(len(listMarkRotateInfo)):
            markRotateInfo = listMarkRotateInfo[i]
            strXmlFilePath = strXmlOutDir
            strXmlFilePath += "{0}.xml".format(str(markRotateInfo.id+1))
            strPicFilePath = strPicOutDir
            strPicFilePath += "{0}.{1}".format(str(markRotateInfo.id+1), strPicSuffix)
            aFile = QFile(strXmlFilePath)

            if aFile.open(QIODevice.WriteOnly | QIODevice.Text):
                strBytes = markRotateInfo.strXmlContent.encode("utf8")
                aFile.write(strBytes)
                aFile.close()
            cv2.imwrite(strPicFilePath, markRotateInfo.matRotate)
        return True

    def doGenMarkRotateInfo(self, markFileInfo: MarkFileInfo, rotateAngle: float, grayColor: int,
                            paraDynamicBrightContrast: dict, paraDynamicHueSatLight: dict, paraDynamicGamma: dict) -> MarkRotateInfo:
        markRotateInfo = MarkRotateInfo()

        image = cv2.imread(markFileInfo.strPicPath)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        transformed = albumentations.rotate(img=image, angle=rotateAngle, interpolation=cv2.INTER_LINEAR,
                                            border_mode=cv2.BORDER_CONSTANT)

        dynamicBrightContrast = paraDynamicBrightContrast["dynamicBrightContrast"]
        rangeBright = paraDynamicBrightContrast["rangeBright"]
        rangeContrast = paraDynamicBrightContrast["rangeContrast"]
        prop = paraDynamicBrightContrast["prop"]
        if dynamicBrightContrast:
            image = albumentations.RandomBrightnessContrast(brightness_limit=rangeBright, contrast_limit=rangeContrast,
                                                            brightness_by_max=True, p=prop)(image=transformed)["image"]
        else:
            image = transformed

        dynamicHueSatLight = paraDynamicHueSatLight["dynamicHueSatLight"]
        rangeHue = paraDynamicHueSatLight["rangeHue"]
        rangeSat = paraDynamicHueSatLight["rangeSat"]
        rangeLight = paraDynamicHueSatLight["rangeLight"]
        prop = paraDynamicHueSatLight["prop"]

        if grayColor > 0 and dynamicHueSatLight:
            image = albumentations.HueSaturationValue(hue_shift_limit=rangeHue, sat_shift_limit=rangeSat, val_shift_limit=rangeLight,
                                                      always_apply=False, p=prop)(image=image)["image"]

        dynamicGamma = paraDynamicGamma["dynamicGamma"]
        rangeGammmaLow = paraDynamicGamma["rangeGammmaLow"]
        rangGammaHigh = paraDynamicGamma["rangGammaHigh"]
        prop = paraDynamicGamma["prop"]

        if dynamicGamma:
            image = albumentations.RandomGamma(gamma_limit=(rangeGammmaLow, rangGammaHigh), eps=None, always_apply=False, p=prop)(image=image)["image"]

        markRotateInfo.matRotate = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        markRotateInfo.rotateAngle = rotateAngle

        markObject: MarkObject
        for i in range(len(markFileInfo.listMarkObject)):
            markObject = markFileInfo.listMarkObject[i]

            rows = len(transformed)
            cols = len(transformed[0])

            center_x = cols / 2.0
            center_y = rows / 2.0

            box_x0 = markObject.box_x0/cols
            box_y0 = markObject.box_y0/rows

            box_x1 = markObject.box_x1/cols
            box_y1 = markObject.box_y1/rows

            box: tuple = (box_x0, box_y0, box_x1, box_y1)
            result: tuple = albumentations.bbox_rotate(box, rotateAngle, "ellipse", rows, cols)

            box_x0 = result[0]
            box_y0 = result[1]
            box_x1 = result[2]
            box_y1 = result[3]

            markRotateObject = MarkObject()
            markRotateObject.box_x0 = int(box_x0*cols)
            markRotateObject.box_y0 = int(box_y0*rows)
            markRotateObject.box_x1 = int(box_x1*cols)
            markRotateObject.box_y1 = int(box_y1*rows)
            markRotateObject.objName = markObject.objName
            markRotateInfo.listRotateMarkObject.append(markRotateObject)

        return markRotateInfo



    def buildMarkRotateInfoFromMarkFileInfo(self, markFileInfo: MarkFileInfo) -> MarkRotateInfo:
        markRotateInfo = MarkRotateInfo()

        markRotateInfo.rotateAngle = 0.0

        markRotateInfo.matRotate = cv2.imread(markFileInfo.strPicPath)

        markObject: MarkObject
        for i in range(len(markFileInfo.listMarkObject)):
            markObject = MarkObject()
            markObject.objName = markFileInfo.listMarkObject[i].objName
            markObject.box_x0 = markFileInfo.listMarkObject[i].box_x0
            markObject.box_x1 = markFileInfo.listMarkObject[i].box_x1
            markObject.box_y0 = markFileInfo.listMarkObject[i].box_y0
            markObject.box_y1 = markFileInfo.listMarkObject[i].box_y1
            markRotateInfo.listRotateMarkObject.append(markObject)

        return markRotateInfo

    def doBuildMarkXml(self, markRotateInfo: MarkRotateInfo, file_name: str, file_path: str, gayColor: int) -> str:
        doc = QDomDocument("")
        root: QDomElement = doc.createElement("annotation")
        doc.appendChild(root)

        folder: QDomElement = doc.createElement("folder")
        root.appendChild(folder)
        folder_text: QDomText = doc.createTextNode("JPEGImages")
        folder.appendChild(folder_text)

        filename: QDomElement = doc.createElement("filename")
        root.appendChild(filename)
        filename_text: QDomText = doc.createTextNode(file_name)
        filename.appendChild(filename_text)

        path: QDomElement = doc.createElement("path")
        root.appendChild(path)
        path_text: QDomText = doc.createTextNode(file_path)
        path.appendChild(path_text)

        source: QDomElement = doc.createElement("source")
        root.appendChild(source)

        database: QDomElement = doc.createElement("database")
        database_text: QDomText = doc.createTextNode("Unknown")
        database.appendChild(database_text)
        source.appendChild(database)

        size: QDomElement = doc.createElement("size")
        root.appendChild(size)

        width: QDomElement = doc.createElement("width")
        cols = len(markRotateInfo.matRotate[0])
        width_text: QDomText = doc.createTextNode(str(cols))
        width.appendChild(width_text)
        size.appendChild(width)

        height: QDomElement = doc.createElement("height")
        rows = len(markRotateInfo.matRotate)
        height_text = doc.createTextNode(str(rows))
        height.appendChild(height_text)
        size.appendChild(height)

        depth: QDomElement = doc.createElement("depth")
        depth_text: QDomText
        if gayColor > 0:
            depth_text = doc.createTextNode("3")
        else:
            depth_text = doc.createTextNode("1")
        depth.appendChild(depth_text)
        size.appendChild(depth)

        segmented: QDomElement = doc.createElement("segmented")
        segmented_text: QDomText = doc.createTextNode("0")
        segmented.appendChild(segmented_text)
        root.appendChild(segmented)

        markObject: MarkObject

        for i in range(len(markRotateInfo.listRotateMarkObject)):
            markObject = markRotateInfo.listRotateMarkObject[i]
            object_: QDomElement = doc.createElement("object")
            root.appendChild(object_)

            name_: QDomElement = doc.createElement("name")
            name_text: QDomText = doc.createTextNode(markObject.objName)
            name_.appendChild(name_text)
            object_.appendChild(name_)

            pose: QDomElement = doc.createElement("pose")
            pose_text: QDomText = doc.createTextNode("Unspecified")
            pose.appendChild(pose_text)
            object_.appendChild(pose)

            truncated: QDomElement = doc.createElement("truncated")
            truncated_text: QDomText = doc.createTextNode("0")
            truncated.appendChild(truncated_text)
            object_.appendChild(truncated)

            difficult: QDomElement = doc.createElement("difficult")
            difficult_text: QDomText = doc.createTextNode("0")
            difficult.appendChild(difficult_text)
            object_.appendChild(difficult)

            bndbox: QDomElement = doc.createElement("bndbox")
            object_.appendChild(bndbox)

            xmin: QDomElement = doc.createElement("xmin")
            xmin_text: QDomText = doc.createTextNode(str(markObject.box_x0))
            xmin.appendChild(xmin_text)
            bndbox.appendChild(xmin)

            ymin: QDomElement = doc.createElement("ymin")
            ymin_text: QDomText = doc.createTextNode(str(markObject.box_y0))
            ymin.appendChild(ymin_text)
            bndbox.appendChild(ymin)

            xmax: QDomElement = doc.createElement("xmax")
            xmax_text: QDomText = doc.createTextNode(str(markObject.box_x1))
            xmax.appendChild(xmax_text)
            bndbox.appendChild(xmax)

            ymax: QDomElement = doc.createElement("ymax")
            ymax_text: QDomText = doc.createTextNode(str(markObject.box_y1))
            ymax.appendChild(ymax_text)
            bndbox.appendChild(ymax)

        return doc.toString()

    def doParseMarkXml(self, markFileInfo):
        doc: QDomDocument = QDomDocument("qdocument")
        file = QFile(markFileInfo.strXmlPath)

        if not file.open(QIODevice.ReadOnly):
            file.close()
            return False

        if not doc.setContent(file):
            file.close()
            return False

        file.close()

        docElem: QDomElement = doc.documentElement()
        subList: QDomNodeList = doc.elementsByTagName("object")
        count = subList.count()
        for index in range(count):
            node: QDomNode = subList.at(index)
            nList: QDomNodeList = node.childNodes()
            count2 = nList.count()
            markObject = MarkObject()
            for i in range(count2):
                subNode: QDomNode = nList.at(i)
                ele: QDomElement = subNode.toElement()
                if ele.nodeName() == "name":
                    markObject.objName = ele.text()
                    markFileInfo.listMarkObject.append(markObject)
                elif ele.nodeName() == "bndbox":
                    subNodeList: QDomNodeList
                    subNodeList = subNode.childNodes()
                    count3 = subNodeList.count()
                    for j in range(count3):
                        subSubNode: QDomNode = subNodeList.at(j)
                        subEle: QDomElement = subSubNode.toElement()
                        if subEle.nodeName() == "xmin":
                            markObject.box_x0 = int(subEle.text())
                        elif subEle.nodeName() == "ymin":
                            markObject.box_y0 = int(subEle.text())
                        elif subEle.nodeName() == "xmax":
                            markObject.box_x1 = int(subEle.text())
                        elif subEle.nodeName() == "ymax":
                            markObject.box_y1 = int(subEle.text())

        return True


markHandle = MarkHandle()
