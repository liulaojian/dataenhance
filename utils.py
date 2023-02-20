from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class CUtils:
    def __init__(self):

        return

    def GetYMDHMS(self) -> str:
        time = QDateTime
        time = QDateTime.currentDateTime()
        year: int = time.date().year()
        month: int = time.date().month()
        day: int = time.date().day()
        hour: int = time.time().hour()
        min: int = time.time().minute()
        sec: int = time.time().second()

        strOut: str = '%d-%d-%d_%d-%d-%d' % (year, month, day, hour, min, sec)
        return strOut


Utils = CUtils()

