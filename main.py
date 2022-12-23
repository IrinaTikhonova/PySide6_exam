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
from PySide6 import QtWidgets, QtCore, QtGui

from ui_form.detailed_info import Ui_MainWindow

from logic.threads import SystemInfo, ProcInfoThread, ServInfoThread, TaskSchedulerInfo


class Window(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initThread()  # инициализация потока
        self.initUi()
        self.initSignals()  # инициализация сигналов

    def initUi(self):  # красоту буду добавлять если успею
        self.setWindowTitle('Диспетчер задач')
        self.spinBoxTimeout = QtWidgets.QSpinBox()
        self.spinBoxTimeout.setValue(1)
        self.spinBoxTimeout.setMinimum(1)
        self.plainTextEditSysInfo = QtWidgets.QPlainTextEdit()
        self.plainTextEditSysInfo.setReadOnly(True)
        self.pushButtonMoreInfo = QtWidgets.QPushButton("Подробнее")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.spinBoxTimeout)
        layout.addWidget(self.plainTextEditSysInfo)
        layout.addWidget(self.pushButtonMoreInfo)

        self.setLayout(layout)

    def initThread(self):
        """
        Инициализация потока

        :return:
        """
        self.systemInfo = SystemInfo()
        self.systemInfo.start()

    def initSignals(self):
        """
        Инициализация сигналов

        :return:
        """
        self.pushButtonMoreInfo.clicked.connect(self.showDetailedInfo)
        self.spinBoxTimeout.valueChanged.connect(self.setTimeout)
        self.systemInfo.systemInfoReceived.connect(self.systemInfoReceivedHandle)

    def systemInfoReceivedHandle(self, sys_info):
        sys_info_str = [str(i) for i in sys_info]
        system_info = "\n".join(sys_info_str)
        self.plainTextEditSysInfo.appendPlainText(system_info)

    def setTimeout(self, value):
        """
        Установка частоты обновления информации в потоке с помощью Spinbox

        :param value:
        :return:
        """
        self.systemInfo.timeout = value

    def showDetailedInfo(self):
        """
        Слот для обработки сигнала - открытие дочернего окна с подробной информацией

        :return:
        """
        self.detailed = ChildWindow()
        self.detailed.show()

    def closeEvent(self, event):
        self.systemInfo.terminate()


class ChildWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initThreads()
        self.initSignals()
        self.Ui = Ui_MainWindow()
        self.Ui.setupUi(self)
        self.initTableModel()


    def initUi2(self):
        """
        Добавление табличной модели

        :return:
        """
        self.Ui.tableView.setModel(self.tableModel)
        self.Ui.tableView_2.setModel(self.tableModel2)
        self.Ui.tableView.resizeColumnsToContents()

    def initThreads(self):
        """
        Инициализация потоков

        :return:
        """
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
        self.procInfo.procInfoReceived.connect(self.procInfoReceivedHandle)
        self.servInfo.servInfoReceived.connect(self.servInfoReceivedHandle)
        self.taskPlan.taskSchedulerInfoReceived.connect(self.taskPlanReceivedHandle)


    def initTableModel(self) -> None:
        """
        Инициализация табличной модели

        :return: None
        """

        self.tableModel = QtGui.QStandardItemModel()

        self.tableModel2 = QtGui.QStandardItemModel()

        self.tableModel3 = QtGui.QStandardItemModel()

        # self.tableModel.dataChanged.connect(self.tableViewDataChanged)

    # def procInfoReceivedHandle(self, proc_info):
    #     self.tableModel.appendRow([QtGui.QStandardItem(str(i)) for i in proc_info])
    #     self.tableModel.setHorizontalHeaderLabels(["Id", "Имя", "ЦПУ", "Память", "Состояние"])

    def procInfoReceivedHandle(self, proc_info):
        self.tableModel.setRowCount(len(proc_info))
        for i, process in enumerate(proc_info):
            self.tableModel.appendRow([QtGui.QStandardItem(str(i)) for i in process])

        self.tableModel.setHorizontalHeaderLabels(["Id", "Имя", "ЦПУ", "Память", "Состояние"])



    def servInfoReceivedHandle(self, serv_info):
        self.tableModel2.appendRow([QtGui.QStandardItem(str(v)) for v in serv_info])
        self.tableModel2.setHorizontalHeaderLabels(["Имя", "Id", "Описание", "Тип запуска", "Путь"])



if __name__ == "__main__":
    app = QtWidgets.QApplication()

    window = Window()
    window.show()

    app.exec()
