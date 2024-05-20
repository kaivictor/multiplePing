from multiplePing_UI_ui import Ui_MainWindow
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


class MainProcess(QMainWindow, Ui_MainWindow):
    pingResultReady = Signal(list)

    def __init__(self):
        super(MainProcess, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("MutilPing")
        self.setFixedSize(self.width(), self.height())
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.init_function()
        self.executor = concurrent.futures.ThreadPoolExecutor()
        self.futures = []

    def init_function(self):
        self.StartPushButton.setDisabled(False)
        self.StartPushButton.clicked.connect(self.start_ping)
        self.masksNumberSpinBox.setValue(24)
        self.masksNumberSpinBox.valueChanged.connect(self.inputCheck)
        self.segmentLineEdit.textChanged.connect(self.inputCheck)
        self.pingResultReady.connect(self.handle_ping_result)

    def inputCheck(self):
        if self.masksNumberSpinBox.value() < 1:
            self.masksNumberSpinBox.setValue(1)
        if self.masksNumberSpinBox.value() > 32:
            self.masksNumberSpinBox.setValue(32)
        if re.match(r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$', self.segmentLineEdit.text()):
            self.StartPushButton.setDisabled(False)
        else:
            self.StartPushButton.setDisabled(True)

    def start_ping(self):
        self.StartPushButton.setDisabled(True)
        ip = self.segmentLineEdit.text()
        subnet_mask_bits = self.masksNumberSpinBox.value()
        # 停止之前的查询
        for future in self.futures:
            future.cancel()
        # results = self.ping_ip_ranges(ip, subnet_mask_bits)
        future = self.executor.submit(self.ping_ip_ranges, ip, subnet_mask_bits)
        self.futures = [future]

    def ping_ip_ranges(self, ip, subnet_mask_bits, group_size=50):
        ip_network = ipaddress.ip_network(f"{ip}/{subnet_mask_bits}", strict=False)
        ips = list(ip_network.hosts())

        results = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in range(0, len(ips), group_size):
                group_ips = ips[i:i+group_size]
                print(f"正在ping {i+1}-{i+group_size}个IP地址...")
                futures = {executor.submit(self.ping, ip): ip for ip in group_ips}  # Use a dictionary to track IP -> future mapping
                for future in concurrent.futures.as_completed(futures):
                    ip = futures[future]  # Retrieve IP corresponding to the completed future
                    result = future.result()
                    results[ip] = {"ip": str(ip), "result": result}

        # Sort results based on IP address
        sorted_results = [results[ip]['result'] for ip in sorted(results.keys(), key=lambda x: int(ipaddress.IPv4Address(x)))]
        # return sorted_results
        self.pingResultReady.emit(sorted_results)
        for result in sorted_results:
            print(f"IP地址: {result[0]}, Ping结果: {'成功' if result[1] else '失败'}")

    def ping(self, ip):
        result = subprocess.run(f'ping {str(ip)} -n 1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return ip, result.returncode == 0

    def handle_ping_result(self, sorted_results):
        self.displayResult(sorted_results)
        self.inputCheck()

    def displayResult(self, results):
        self.resultTreeWidget.clear()
        self.resultTreeWidget.setHeaderLabels(["状态", "IP", "存活"])
        self.resultTreeWidget.setColumnWidth(0, 50)
        for i, result in enumerate(results):
            # results = [{"ip": str, "result": bool}]
            ip = result[0]
            is_alive = result[1]

            tree_widget_item = QTreeWidgetItem(self.resultTreeWidget)
            tree_widget_item.setText(0, "")
            tree_widget_item.setText(1, str(ip))
            tree_widget_item.setText(2, str(is_alive))

            # 设置单元格颜色
            if is_alive:
                tree_widget_item.setBackground(0, QBrush(QColor(0, 255, 0)))
            else:
                tree_widget_item.setBackground(0, QBrush(QColor(255, 0, 0)))
            self.resultTreeWidget.setItemWidget(tree_widget_item, 0, QLabel(""))

        # 设置表格行和列大小、表头标签等


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ping_app = MainProcess()
    ping_app.show()
    sys.exit(app.exec_())
