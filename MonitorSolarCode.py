from PyQt5 import QtCore, QtGui, QtWidgets
import sys
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
from MonitorSolar import Ui_MainWindow
import paho.mqtt.client as mqqt
import json
import pyqtgraph as pg
from PyQt5.QtCore import QTime, QTimer
import numpy as np
from time import *
from unidecode import unidecode
import mysql.connector
import csv
mydb = mysql.connector.connect(
host="34.143.207.104",
user="student",
password="student",
database="ProjectSolar"
)


class myclass(Ui_MainWindow):
    def __init__(self) -> None:
        super().setupUi(MainWindow)
        self.client = mqqt.Client()
        addr = "34.143.207.104"
        port = 8883
        self.client.connect(addr, port)
        self.client.on_message = self.on_message
        self.client.subscribe("inno/ProjectSolar/Sensor")
        # self.client.subscribe("inno/ProjectSolar/qTime")
        self.client.loop_start()

        self.data = {}
        self.data2 = {}
        self.data3 = {}
        self.gca()
        self.update_graph()
        self.yy = 0
        self.mytimer=QtCore.QTimer()
        self.mytimer.setInterval(1000)
        self.mytimer.timeout.connect(self.positionY)
        self.mytimer.start()

        self.timex=QTimer()
        self.timex.start(1000)
        self.timex.timeout.connect(self.update_time)
        self.timex.start()

    def gca(self):
        self.Xaxis.sliderReleased.connect(self.positionY)
        self.pushButton_3.clicked.connect(self.calender)
        self.Xaxis.sliderReleased.connect(self.positionX)
        

    def update_time(self):
        current_time = QTime.currentTime()
        time_string = current_time.toString("hh:mm:ss")
        self.time.setText(unidecode(time_string))

    def positionX(self):
        self.data2["ganX"] = self.Xaxis.value()
        self.jsout = json.dumps(self.data2)
        self.client.publish("inno/ProjectSolar/ganX", self.jsout)

    
    def positionY(self):
        self.yy += 1
        if self.yy > 180 :
            self.resety()       
        xy = str(self.yy)
        hour = QTime.currentTime().hour()
        if  hour > 18 or hour < 6 :
            self.stopsolar()
        self.PoY.setText(xy)
        self.data3["ganY"] = xy

        self.jsout = json.dumps(self.data3)
        self.client.publish("inno/ProjectSolar/ganY", self.jsout)

    def readsql(self):
        mycursor = mydb.cursor()
        sql = "SELECT * FROM ProjectSolar.ProjectSolar WHERE day LIKE %s"
        datet = ("%"+self.eng_num+"%",)
        mycursor.execute(sql,datet)
        myresult = mycursor.fetchall()
        with open("D:/Electronic Engineering/InnoProjec/CSVDATA.CSV", mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in mycursor.description])
            for row in myresult:
                writer.writerow(row)
    def stopsolar(self):
        self.yy = 0
        return

    def resety(self):
        self.yy = 0
        return

    def on_message(self,client,userdata,message):
        tp = str(message.topic)
        self.stms = str(message.payload.decode("utf-8"))
        self.data = json.loads(self.stms)
        print(self.data)
        self.Shader.display(self.data["shader"])
        self.humid.display(self.data["humid"])
        self.Temp.display(self.data["temp"])

        self.x = np.append(self.x[1:],self.x[-1]+1)
        self.y1 = np.append(self.y1[1:],float(self.data["temp"]))
        self.y2 = np.append(self.y2[1:],float(self.data["humid"]))
        self.y3 = np.append(self.y3[1:],float(self.data["shader"]))

        self.dataline1.setData(self.x,self.y1)
        self.dataline2.setData(self.x,self.y2)
        self.dataline3.setData(self.x,self.y3)
    
    def update_graph(self):
        self.mygraph1 = pg.PlotWidget(self.centralwidget)
        self.mygraph1.setAutoVisible(y = True)
        self.mygraph1.setGeometry(QtCore.QRect(10,600,371,211))
        self.dataline1 = self.mygraph1.plot()
        self.x = np.arange(0,100)
        self.y1 = np.zeros(100)
        
        self.mygraph2 = pg.PlotWidget(self.centralwidget)
        self.mygraph2.setAutoVisible(y = True)
        self.mygraph2.setGeometry(QtCore.QRect(410,600,371,211))
        self.dataline2 = self.mygraph2.plot()
        self.x = np.arange(0,100)
        self.y2 = np.zeros(100)

        self.mygraph3 = pg.PlotWidget(self.centralwidget)
        self.mygraph3.setAutoVisible(y = True)
        self.mygraph3.setGeometry(QtCore.QRect(810,600,371,211))
        self.dataline3 = self.mygraph3.plot()
        self.x = np.arange(0,100)
        self.y3 = np.zeros(100)

    def calender(self):
        self.text = self.calendar.selectedDate()
        self.qdate = self.text
        self.str = self.qdate.toString("dd/M/yyyy")
        self.label_4.setText(str(unidecode(self.str)))
        thia_num = self.str
        self.eng_num = unidecode(thia_num)
        print(self.eng_num)
        self.readsql()


if __name__ == "__main__":
    ui = myclass()
    MainWindow.show()
    sys.exit(app.exec_())
