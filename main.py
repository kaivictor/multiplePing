from multiplePing_UI_ui import Ui_MainWindow
from process import MainProcess
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

import re
import ipaddress
import subprocess
import concurrent.futures
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ping_app = MainProcess()
    ping_app.show()
    sys.exit(app.exec())