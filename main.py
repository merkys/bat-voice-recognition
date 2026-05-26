import sys

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from configparser import ConfigParser
from Balso_Atradimas import *


# Get image path from command line or file dialog
if len(sys.argv) > 1:
    input_path = sys.argv[1]
else:
    # Create app just for file dialog
    app_temp = QApplication.instance()
    if app_temp is None:
        app_temp = QApplication(sys.argv)
    
    input_path, _ = QFileDialog.getOpenFileName(None, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
    
    if not input_path:
        print("No file selected")
        sys.exit(1)

arguments = ConfigParser()
arguments.read(os.path.join(os.path.dirname(__file__), 'args.ini'))

class ArgumentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isvestis")
        self.setMinimumSize(480, 360)
        layout = QVBoxLayout()

        self.warning = QLabel("Aargumentai bus pakeisti tik uždarius šį langą")
        layout.addWidget(self.warning)

        self.MinAukstisLabel = QLabel("minimalus paveikslėlio aukštis nuo kurio apdirbamas paveiklsėlis:")
        self.MinAukstis = QSpinBox(self)
        self.MinAukstis.setRange(0, 256)
        self.MinAukstis.setValue(arguments.getint('Arguments', 'MinAukstis'))
        self.MinAukstis.setSuffix(" px")
        layout.addWidget(self.MinAukstisLabel)
        layout.addWidget(self.MinAukstis)

        self.MaxAukstisLabel = QLabel("maksimalus paveikslėlio aukštis nuo kurio apdirbamas paveiklsėlis (negali būti mažesnis už minimalią vertę):")
        self.MaxAukstis = QSpinBox(self)
        self.MaxAukstis.setRange(0, 256)
        self.MaxAukstis.setValue(arguments.getint('Arguments', 'MaxAukstis'))
        self.MaxAukstis.setSuffix(" px")
        layout.addWidget(self.MaxAukstisLabel)
        layout.addWidget(self.MaxAukstis)

        self.MinRegionoDydisLabel = QLabel("Minimalus regiono dydis, kad būtų fiksuojama koordinatės:")
        self.MinRegionoDydis = QSpinBox(self)
        self.MinRegionoDydis.setValue(arguments.getint('Arguments', 'MinRegionoDydis'))
        self.MinRegionoDydis.setSuffix(" px")
        layout.addWidget(self.MinRegionoDydisLabel)
        layout.addWidget(self.MinRegionoDydis)


        self.setLayout(layout)
    def closeEvent(self, event):
        arguments.set('Arguments', 'MinAukstis', str(self.MinAukstis.value()))
        arguments.set('Arguments', 'MaxAukstis', str(self.MaxAukstis.value()))
        arguments.set('Arguments', 'AukscioTolerancija', str(self.MinRegionoDydis.value()))
        with open(os.path.join(os.path.dirname(__file__), 'args.ini'), 'w') as args:
            arguments.write(args)
        event.accept

class Error_NoImage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Įvyko klaida")
        self.setMinimumSize(480, 360)

        layout = QVBoxLayout()
        self.ErrorLabel = QLabel("Įvyko klaida, nerastas paveikslėlis")
        layout.addWidget(self.ErrorLabel)
        self.setLayout(layout)

class OutputWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Isvestis")
        self.setMinimumSize(640, 500)

        layout = QHBoxLayout()
        
        # Image on the left
        self.ImageLabel = QLabel(self)
        self.ImageLabel.setMinimumSize(400, 400)
        layout.addWidget(self.ImageLabel)
        
        # Scrollable coordinates list on the right
        coords_layout = QVBoxLayout()
        coords_label = QLabel("Koordinatės:")
        coords_layout.addWidget(coords_label)
        
        self.CoordinatesText = QTextEdit(self)
        self.CoordinatesText.setReadOnly(True)
        self.CoordinatesText.setMinimumWidth(200)
        coords_layout.addWidget(self.CoordinatesText)
        
        layout.addLayout(coords_layout)
        self.setLayout(layout)
        
        self.refreshtimer = QTimer(self)
        self.refreshtimer.timeout.connect(self.refresh_image)
        self.refreshtimer.start(1000)
        self.refresh_image()
        
    def refresh_image(self):
        try:
            self.OutputImage = QPixmap(os.path.join(os.path.dirname(__file__), "BWlygmuo.png"))
            self.ImageLabel.setPixmap(self.OutputImage)
        except:
            pass
        
        # Load and display coordinates while preserving scroll position
        try:
            with open(os.path.join(os.path.dirname(__file__), "output.txt"), 'r') as f:
                new_text = f.read()
            
            # Only update if text has changed
            if self.CoordinatesText.toPlainText() != new_text:
                scrollbar = self.CoordinatesText.verticalScrollBar()
                scroll_pos = scrollbar.value()
                
                self.CoordinatesText.setText(new_text)
                
                scrollbar.setValue(scroll_pos)
        except:
            self.CoordinatesText.setText("No coordinates available")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("siksnosparniu balsu atpazinimas")
        self.setMinimumSize(640, 480)
        self.ArgWindow = ArgumentWindow()
        self.OutWindow = OutputWindow()
        self.ErrorWindow = None
        Toolbar = QToolBar("Main Toolbar")
        self.addToolBar(Toolbar)
        Toolbar_Argument_Button = QAction("Argumentai", self)
        Toolbar_Argument_Button.triggered.connect(self.Show_Argument_window)
        Toolbar.addAction(Toolbar_Argument_Button)

        Toolbar_Output_Button = QAction("Ribu Radimas", self)
        Toolbar_Output_Button.triggered.connect(self.Ribu_Radimas)
        Toolbar.addAction(Toolbar_Output_Button)

        Toolbar_Output_Button = QAction("Isvestis", self)
        Toolbar_Output_Button.triggered.connect(self.Show_Output_window)
        Toolbar.addAction(Toolbar_Output_Button)



        ImageLabel = QLabel(self)
        InputImage = QPixmap(input_path)
        ImageLabel.setPixmap(InputImage)
        self.setCentralWidget(ImageLabel)
    def Show_Error_Window(self):
        self.ErrorWindow = Error_NoImage()
        self.ErrorWindow.show()

    def Show_Argument_window(self, checked):
        self.ArgWindow.show()
    
    def Show_Output_window(self, checked):
        output = Balsu_atpazinimas(input_path)
        if output == -1:
            self.Show_Error_Window()
        else:
            self.OutWindow.show()
    
    def Ribu_Radimas(self, checked):
        output = RaskRibas(input_path)
        if output == -1:
            self.Show_Error_Window()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
