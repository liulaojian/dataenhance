class MarkObject:
    def __init__(self):
        self.objName = ""
        self.box_x0 = 0
        self.box_x1 = 0
        self.box_y0 = 0
        self.box_y1 = 0
        return


class MarkRotateInfo:
    def __init__(self):
        self.id = -1
        self.matRotate = None
        self.rotateAngle = 0.0
        self.strXmlContent = ""
        self.listRotateMarkObject = []
        return


class MarkFileInfo:
    def __init__(self):
        self.id = -1
        self.strPicPath = ""
        self.strXmlPath = ""
        self.bHandled = False
        self.listMarkObject = []
        return

