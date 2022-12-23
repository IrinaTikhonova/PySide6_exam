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

from ui_form.all_in_one import Ui_MainWindow

from logic.threads import SystemInfo, ProcInfoThread, ServInfoThread, TaskSchedulerInfo


class Window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initThreads()
        self.initSignals()
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.initUi2()
        self.initTableModel()
        self.initSignals()


    def initUi2(self):
        """
        Добавление табличной модели

        :return:
        """
        self.Ui.processes_view.setModel(self.tableModel)
        self.Ui.services_view.setModel(self.tableModel2)
        # self.Ui.p.resizeColumnsToContents()

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

    def initSignals(self):
        """
        Инициализация сигналов

        :return:
        """

        self.Ui.spinBox.valueChanged.connect(self.setTimeoutForSysInfo)
        self.systemInfo.systemInfoReceived.connect(
            lambda sys_info: self.Ui.CPU_info.appendPlainText(str(sys_info)))
        self.Ui.spinBox_2.valueChanged.connect(self.setTimeout)
        self.Ui.action_2.connect(self.onExitPress)
        self.procInfo.procInfoReceived.connect(self.procInfoReceivedHandle)
        self.servInfo.servInfoReceived.connect(self.servInfoReceivedHandle)
        self.taskPlan.taskSchedulerInfoReceived.connect(self.taskPlanReceivedHandle)

    def setTimeoutForSysInfo(self, value):
        """
        Установка частоты обновления информации в потоке с помощью Spinbox

        :param value:
        :return:
        """
        self.systemInfo.timeout = value

    def setTimeout(self, value):
        self.procInfo.timeout = value
        self.servInfo.timeout = value

    def closeEvent(self, event):
        self.systemInfo.terminate()


    def initTableModel(self) -> None:
        """
        Инициализация табличной модели

        :return: None
        """

        self.tableModel = QtGui.QStandardItemModel()

        self.tableModel2 = QtGui.QStandardItemModel()

        # self.tableModel.dataChanged.connect(self.tableViewDataChanged)

    def procInfoReceivedHandle(self, proc_info):
        self.tableModel.setRowCount(len(proc_info))
        for i, process in enumerate(proc_info):
            self.tableModel.appendRow([QtGui.QStandardItem(str(j)) for j in process])

        self.tableModel.setHorizontalHeaderLabels(["Id", "Имя", "ЦПУ", "Память", "Состояние"])


    def servInfoReceivedHandle(self, serv_info):
        self.tableModel2.appendRow([QtGui.QStandardItem(str(v)) for v in serv_info])
        self.tableModel2.setHorizontalHeaderLabels(["Имя", "Id", "Описание", "Тип запуска", "Путь"])

    def closeEvent(self, event):
        self.systemInfo.terminate()
        self.procInfo.terminate()
        self.servInfo.terminate()

    def onExitPress(self):

        self.systemInfo.deleteLater()
        self.procInfo.deleteLater()
        self.servInfo.deleteLater()
        self.close()

    # def taskPlanReceivedHandle(self, list_tasks):
    #     self.Ui.tableWidget.setRowCount(len(list_tasks))
    #     for i, task in enumerate(list_tasks):
    #         task_name, task_path, task_state, task_next_run_time = task
    #         self.Ui.tableWidget.setItem(i, 0, QTableWidgetItem(task_name))
    #         self.Ui.tableWidget.setItem(i, 2, QTableWidgetItem(task_state))
    #         self.Ui.tableWidget.setItem(i, 1, QTableWidgetItem(task_next_run_time))
    #         self.Ui.tableWidget.setItem(i, 3, QTableWidgetItem(task_path))



if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()