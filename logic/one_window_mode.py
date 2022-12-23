"""
Задача.
Разработать приложение для мониторинга нагрузки системы и системных
процессов (аналог диспетчера задач).
Обязательные функции в приложении:
    - Показ общих сведений о системе(в текстовом виде!):
    - Название процессора, количество ядер, текущая загрузка
    - Общий объём оперативной памяти, текущая загрузка оперативаной памяти
    - Количество, жестких дисков + информация по каждому(общий / занятый объём)
Обеспечить динамический выбор обновления  информации(1, 5, 10, 30 сек.)
Показ работающих процессов
Показ работающих служб
Показ задач, которые запускаются с помощью планировщика задач
"""
from PySide6 import QtWidgets, QtGui

from ui_form.omg import Ui_MainWindow

from logic.threads import SystemInfo, ProcInfoThread, ServInfoThread, TaskSchedulerInfo, DisksInfo


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initThreads()
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.initSignals()
        self.initModels()
        self.initUi2()


    def initUi2(self):
        """
        Добавление табличной модели

        :return:
        """
        self.Ui.processes_view.setModel(self.tableModel)
        self.Ui.services_view.setModel(self.tableModel2)
        self.Ui.tableView.setModel(self.tableModel3)
        self.Ui.tableView.resizeColumnsToContents()
        self.Ui.services_view.horizontalHeader().setStretchLastSection(True)
        self.Ui.treeView.setModel(self.treeModel)
        self.Ui.treeView.header().resizeSection(0, 200)
        self.Ui.treeView.expandAll()


    def initThreads(self):
        """
        Инициализация потока

        :return:
        """
        self.systemInfo = SystemInfo()
        self.systemInfo.start()
        self.procInfo = ProcInfoThread()
        self.procInfo.start()
        self.servInfo = ServInfoThread()
        self.servInfo.start()
        self.taskPlan = TaskSchedulerInfo()
        self.taskPlan.start()
        self.disksInfo = DisksInfo()
        self.disksInfo.start()

    def initSignals(self):
        """
        Инициализация сигналов

        :return:
        """

        self.Ui.spinBox.valueChanged.connect(self.setTimeoutForSysInfo)
        self.systemInfo.systemInfoReceived.connect(
            lambda sys_info: self.Ui.CPU_info.appendPlainText(str(sys_info)))
        self.Ui.spinBox_2.valueChanged.connect(self.setTimeout)
        self.Ui.action.triggered.connect(self.onExitPress)
        self.Ui.action_2.triggered.connect(self.showMinimized)
        self.Ui.action_3.triggered.connect(self.showMaximized)
        self.procInfo.procInfoReceived.connect(self.procInfoReceivedHandle)
        self.servInfo.servInfoReceived.connect(self.servInfoReceivedHandle)
        self.disksInfo.disksInfoReceived.connect(self.disksInfoReceivedHandle)
        self.taskPlan.taskSchedulerInfoReceived.connect(self.taskPlanReceivedHandle)

    def setTimeoutForSysInfo(self, value):
        """
        Установка частоты обновления информации в потоке с помощью Spinbox

        :param value:
        :return:
        """
        self.systemInfo.timeout = value
        self.disksInfo.timeout = value

    def setTimeout(self, value):
        self.procInfo.timeout = value
        self.servInfo.timeout = value
        self.taskPlan.timeout = value


    def initModels(self) -> None:
        """
        Инициализация табличной модели

        :return: None
        """

        self.tableModel = QtGui.QStandardItemModel()
        self.tableModel2 = QtGui.QStandardItemModel()
        self.tableModel3 = QtGui.QStandardItemModel()
        self.treeModel = QtGui.QStandardItemModel()

        # self.tableModel.dataChanged.connect(self.tableViewDataChanged)

    def procInfoReceivedHandle(self, proc_info):
        # self.tableModel.setRowCount(len(proc_info))
        for i, process in enumerate(proc_info):
            self.tableModel.appendRow([QtGui.QStandardItem(str(j)) for j in process])

        self.tableModel.setHorizontalHeaderLabels(["Id", "Имя", "ЦПУ", "Память", "Состояние"])

    def servInfoReceivedHandle(self, serv_info):
        # self.tableModel2.setRowCount(len(serv_info))
        for i, service in enumerate(serv_info):
            self.tableModel2.appendRow([QtGui.QStandardItem(v) for v in service])

        self.tableModel2.setHorizontalHeaderLabels(["Имя", "Id", "Описание", "Тип запуска", "Путь"])

    def disksInfoReceivedHandle(self, disks_list):

        self.treeModel.setHorizontalHeaderLabels(['Диск', 'Информация о памяти'])
        itemDisk = QtGui.QStandardItem(str(disks_list[0]))
        self.treeModel.appendRow(itemDisk)
        self.treeModel.setItem(0, 1, QtGui.QStandardItem('Наименование'))
        itemTotal = QtGui.QStandardItem('Общий объем памяти')
        itemDisk.appendRow(itemTotal)
        itemDisk.setChild(0, 1, QtGui.QStandardItem(str(disks_list[1])))

        itemUsed = QtGui.QStandardItem('Занятый объем памяти')
        itemDisk.appendRow(itemUsed)
        itemDisk.setChild(1, 1, QtGui.QStandardItem(str(disks_list[2])))

    def taskPlanReceivedHandle(self, tasks_plan):

        for i, task in enumerate(tasks_plan):
            self.tableModel3.appendRow([QtGui.QStandardItem(v) for v in task])

        self.tableModel3.setHorizontalHeaderLabels(["Путь", "Состояние", "Следующий запуск"])

    def closeEvent(self, event):
        self.systemInfo.terminate()
        self.disksInfo.terminate()
        self.procInfo.terminate()
        self.servInfo.terminate()
        self.taskPlan.terminate()


    def onExitPress(self):

        self.systemInfo.deleteLater()
        self.procInfo.deleteLater()
        self.servInfo.deleteLater()
        self.disksInfo.deleteLater()
        self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()