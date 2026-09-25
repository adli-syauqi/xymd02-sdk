from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton, QLineEdit, QComboBox, QHBoxLayout, QGridLayout, QGroupBox, QMessageBox #type: ignore
from PySide6.QtCore import Qt, QThreadPool #type: ignore
from sensor import Sensor
from database import Db
import time
import os
import sys
import random

os.environ["QT_API"] = "PySide6"

from matplotlib.backends.backend_qtagg import FigureCanvas #type: ignore
from matplotlib.figure import Figure #type: ignore

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        self.reading = False
        
        self.setWindowTitle("XY-MD02 Driver")

        container = QWidget()
        self.setCentralWidget(container)
        
        top_container = QWidget()
        mid_container = QWidget()
        bottom_container = QWidget()
    
        layout = QVBoxLayout(container)
        
        layout.addWidget(top_container)
        layout.addWidget(mid_container)
        layout.addWidget(bottom_container)
        
        top_layout = QVBoxLayout(top_container)
        mid_layout = QVBoxLayout(mid_container)
        bottom_layout = QVBoxLayout(bottom_container)
        
        top_box = QGroupBox("")
        mid_box = QGroupBox("")
        bottom_box = QGroupBox("")
    
        top_box.setLayout(top_layout) 
        mid_box.setLayout(mid_layout) 
        bottom_box.setLayout(bottom_layout) 
        
        layout.addWidget(top_box)
        layout.addWidget(mid_box)
        layout.addWidget(bottom_box)
                
        # top box (com - baudrate - connect)
        top_title = QLabel("Connect Parameters")
        
        top_content = QWidget()
        
        top_layout.addWidget(top_title)
        top_layout.addWidget(top_content)
        
        top_content_layout = QGridLayout(top_content)
        
        com_label = QLabel("COM: ")
        self.com_lineedit = QLineEdit("COM16") # default com16
        
        baudrate_label = QLabel("Baud Rate: ")        
        self.baudrate_combobox = QComboBox()
        self.baudrate_combobox.addItems(['9600', '14400', '19200'])
        
        device_id_label = QLabel("Device ID: ")
        self.device_id_lineedit = QLineEdit("1") # default 1

        # connect = False

        connect_label = QLabel("")
        self.connect_button = QPushButton("Disconnected")
        self.connect_button.setCheckable(True)
        self.connect_button.setStyleSheet("""
            QPushButton:checked {
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:!checked {
                background-color: #f44336;
                color: white;
            }
        """)
        
        self.connect_button.toggled.connect(self.connect_on_toggled)
        
        top_content_layout.addWidget(com_label, 0, 0)
        top_content_layout.addWidget(self.com_lineedit, 1, 0)
        top_content_layout.addWidget(baudrate_label, 0, 1)
        top_content_layout.addWidget(self.baudrate_combobox, 1, 1)
        top_content_layout.addWidget(device_id_label, 0, 2)
        top_content_layout.addWidget(self.device_id_lineedit, 1, 2)
        top_content_layout.addWidget(connect_label, 0, 3)
        top_content_layout.addWidget(self.connect_button, 1, 3)
        
        # mid box (id - baudrate - temp_correction - hum_correction - apply)
        mid_title = QLabel("Modify Parameters")
        mid_content = QWidget()
        
        mid_layout.addWidget(mid_title)
        mid_layout.addWidget(mid_content)
        
        mid_content_layout = QGridLayout(mid_content)
                
        changeid_label = QLabel("Device ID (1-257): ")
        self.changeid_lineedit = QLineEdit("1")
        
        changebr_label = QLabel("Baud Rate: ")
        self.changebr_combobox = QComboBox()
        self.changebr_combobox.addItems(['9600', '14400', '19200'])
        
        changetc_label = QLabel("Temperature Correction (-10 - 10): ")
        self.changetc_lineedit = QLineEdit("0")
        
        changehc_label = QLabel("Humidity Correction (-10 - 10)")
        self.changehc_lineedit = QLineEdit("0")
        
        apply_label = QLabel("")
        self.apply_button = QPushButton("Apply")
        self.apply_button.setCheckable(True)
        self.apply_button.toggled.connect(self.modify_on_toggled)
        
        
        mid_content_layout.addWidget(changeid_label, 0, 0)
        mid_content_layout.addWidget(self.changeid_lineedit, 1, 0)
        mid_content_layout.addWidget(changebr_label, 0, 1)
        mid_content_layout.addWidget(self.changebr_combobox, 1, 1)
        mid_content_layout.addWidget(changetc_label, 0, 2)
        mid_content_layout.addWidget(self.changetc_lineedit, 1, 2)
        mid_content_layout.addWidget(changehc_label, 0, 3)
        mid_content_layout.addWidget(self.changehc_lineedit, 1, 3)
        mid_content_layout.addWidget(apply_label, 0, 4)
        mid_content_layout.addWidget(self.apply_button, 1, 4)
        
        # bottom
        bottom_title = QLabel("Output")
        bottom_content = QWidget()
        
        bottom_layout.addWidget(bottom_title)
        bottom_layout.addWidget(bottom_content)
        
        bottom_content_layout = QHBoxLayout(bottom_content)
        
        bottom_left_content_layout = QWidget()
        bottom_mid_content_layout = QWidget()
        bottom_right_content_layout = QWidget()
        
        bottom_content_layout.addWidget(bottom_left_content_layout)
        bottom_content_layout.addWidget(bottom_mid_content_layout)
        bottom_content_layout.addWidget(bottom_right_content_layout)
        
        bottom_left_content_layout_layout = QVBoxLayout(bottom_left_content_layout)
        
        self.text_temp = QLabel("Temperature: ")
        self.text_hum = QLabel("Humidity: ")
        self.text_device_id = QLabel("Device ID: ")
        self.text_baudrate = QLabel("Baud rate: ")
        self.text_temp_cor = QLabel("Temperature Correction: ")
        self.text_hum_cor = QLabel("Humidity Correction: ")
        
        bottom_left_content_layout_layout.addWidget(self.text_temp)
        bottom_left_content_layout_layout.addWidget(self.text_hum)
        bottom_left_content_layout_layout.addWidget(self.text_device_id)
        bottom_left_content_layout_layout.addWidget(self.text_baudrate)
        bottom_left_content_layout_layout.addWidget(self.text_temp_cor)
        bottom_left_content_layout_layout.addWidget(self.text_hum_cor)
        
        bottom_mid_content_layout_layout = QVBoxLayout(bottom_mid_content_layout)
        self.temp_graph = MplCanvas(self, width=2, height=2, dpi=100)
        self.temp_graph.axes.set_ylabel("Temperature (°C)")
        self.temp_graph.figure.tight_layout()
        self.temp_graph.axes.set_ylim(25, 30)
        bottom_mid_content_layout_layout.addWidget(self.temp_graph)
        
        bottom_right_content_layout_layout = QVBoxLayout(bottom_right_content_layout)
        self.hum_graph = MplCanvas(self, width=2, height=2, dpi=100)
        self.hum_graph.axes.set_ylabel("Humidity (RH)")
        self.hum_graph.figure.tight_layout()
        self.hum_graph.axes.set_ylim(60, 70)
        bottom_right_content_layout_layout.addWidget(self.hum_graph)
        
        n_data = 50
        self.temp_xdata = list(range(n_data))
        self.temp_ydata = [0 for i in range(n_data)]
        self.hum_xdata = list(range(n_data))
        self.hum_ydata = [0 for i in range(n_data)]
        self.show()

    def connect_on_toggled(self, checked):
        if checked:
            connect_port = self.com_lineedit.text()
            connect_baudrate = int(self.baudrate_combobox.currentText())
            self.device_id = int(self.device_id_lineedit.text())
            
            self.sensor = Sensor(connect_port=connect_port, connect_baudrate=connect_baudrate)
            self.connect_button.setText("Connected")
            
            self.database = Db()
            
            self.reading = True
            self.threadpool.start(self.running)

        else:
            self.reading = False
            self.sensor.disconnect()
            self.connect_button.setText("Disconnected")
            
            self.database.close_db()
            
    def running(self):
        while(self.reading == True):
            self.sensor.read(self.device_id)
            self.text_temp.setText("Temperature: " + str(self.sensor.temperature)) 
            self.text_hum.setText("Humidity: " + str(self.sensor.humidity))
            self.text_device_id.setText("Device ID: " + str(self.sensor.device_address)) 
            self.text_baudrate.setText("Baud rate: " + str(self.sensor.baudrate)) 
            self.text_temp_cor.setText("Temperature Correction: " + str(self.sensor.temp_correction)) 
            self.text_hum_cor.setText("Humidity Correction: " + str(self.sensor.hum_correction))
            self.temp_update_plot(data=self.sensor.temperature)
            self.hum_update_plot(data=self.sensor.humidity)
            
            self.database.insert_log(self.sensor.temperature, self.sensor.humidity)
            time.sleep(1)
            
    def modify_on_toggled(self, checked):
        # self.apply_button.clicked.connect(lambda: QMessageBox.information(self, 'info', 'Change applied, power cycle the sensor and reconnect!'))
        changeid = int(self.changeid_lineedit.text())
        changebr = int(self.changebr_combobox.currentText())
        changetc = int(self.changetc_lineedit.text())
        changehc = int(self.changehc_lineedit.text())
        
        if self.reading:
            self.reading = False
            self.sensor.modify(changeid=changeid, changebr=changebr, changetc=changetc, changehc=changehc, deviceid=int(self.device_id_lineedit.text()))        
            self.apply_button.clicked.connect(lambda: QMessageBox.information(self, 'info', 'Change applied, power cycle the sensor and reconnect!'))
        else:
            self.sensor = Sensor(connect_port=self.com_lineedit.text(), connect_baudrate=int(self.baudrate_combobox.currentText()))
            self.sensor.modify(changeid=changeid, changebr=changebr, changetc=changetc, changehc=changehc, deviceid=int(self.device_id_lineedit.text()))        
            self.apply_button.clicked.connect(lambda: QMessageBox.information(self, 'info', 'Change applied, power cycle the sensor and reconnect!'))
            self.sensor.disconnect() 

    def temp_update_plot(self, data):
        # Drop off the first y element, append a new one.
        self.temp_ydata = self.temp_ydata[1:] + [data]
        self.temp_graph.axes.cla()  # Clear the canvas.
        self.temp_graph.axes.plot(self.temp_xdata, self.temp_ydata, 'r')
        self.temp_graph.axes.set_ylabel("Temperature (°C)")
        self.temp_graph.figure.tight_layout()
        self.temp_graph.axes.set_ylim(25, 30)
        # Trigger the canvas to update and redraw.
        self.temp_graph.draw()

    def hum_update_plot(self, data):
        # Drop off the first y element, append a new one.
        self.hum_ydata = self.hum_ydata[1:] + [data]
        self.hum_graph.axes.cla()  # Clear the canvas.
        self.hum_graph.axes.plot(self.hum_xdata, self.hum_ydata, 'r')
        self.hum_graph.axes.set_ylabel("Humidity (RH)")
        self.hum_graph.figure.tight_layout()
        self.hum_graph.axes.set_ylim(60, 70)
        # Trigger the canvas to update and redraw.
        self.hum_graph.draw()
        
app = QApplication()

window = MainWindow()
window.show()

app.exec()
