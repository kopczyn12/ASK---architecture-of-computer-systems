import sys
import re
from PyQt5.QtWidgets import *
from PyQt5 import QtGui


class Window(QMainWindow) :
    vulgarism_list = [line.rstrip( ) for line in open('grubianstwa.txt')]
    message = []

    def __init__(self) :
        super(Window, self).__init__( )
        self.setGeometry(700, 300, 400, 150)
        self.win = QWidget(self)
        self.setCentralWidget(self.win)
        self.mainLayout = QVBoxLayout( )
        self.gridLayout = QGridLayout( )
        self.win.setLayout(self.mainLayout)
        self.setWindowTitle("RS-232")
        self.app_open = False
        self.app2_open = False
        self.label = QLabel("Transmisja - RS232", self)
        self.label.move(140, 5)
        self.label.resize(150, 50)

        self.button0 = QPushButton('Nadawca', self)
        self.button0.clicked.connect(self.button0_action)
        self.button0.resize(140, 60)
        self.button0.move(50, 50)

        self.button1 = QPushButton('Odbiorca', self)
        self.button1.clicked.connect(self.button1_action)
        self.button1.resize(140, 60)
        self.button1.move(200, 50)

        self.show( )

    def button0_action(self) :
        if not self.app_open :
            self.app = childWindow(self)
            self.app_open = True
        else :
            self.app.close_window( )
            self.app_open = False

    def button1_action(self) :
        if not self.app2_open :
            self.app2 = childWindowreciv(self)
            self.app2_open = True
        else :
            self.app2.close_window( )
            self.app2_open = False

    def close(self) :
        sys.exit( )

    def closeEvent(self, QCloseEvent) :
        QCloseEvent.ignore( )
        self.close( )


class childWindow(QDialog) :
    def __init__(self, parent=None) :
        super(childWindow, self).__init__( )
        self.setGeometry(200, 300, 500, 500)
        self.win = QWidget(self)
        self.parent = parent
        self.setWindowTitle("Nadawca")
        self.label = QLabel("Tekst do wyslania", self)
        self.label.move(200, 0)
        self.label.setFont(QtGui.QFont('SansSerif', 9, weight=10))
        self.label.resize(300, 100)

        self.textedit = QTextEdit("", self)
        self.textedit.move(50, 80)
        self.textedit.setFont(QtGui.QFont('SansSerif', 9))
        self.textedit.resize(400, 100)

        self.label2 = QLabel("Wysylane wiadomosci", self)
        self.label2.move(180, 160)
        self.label2.setFont(QtGui.QFont('SansSerif', 9, weight=10))
        self.label2.resize(400, 100)

        self.textedit2 = QTextEdit("", self)
        self.textedit2.move(50, 250)
        self.textedit2.setFont(QtGui.QFont('SansSerif', 9))
        self.textedit2.resize(400, 100)
        self.textedit2.setDisabled(True)

        self.button0 = QPushButton('Wyslij', self)
        self.button0.clicked.connect(self.button0_action)
        self.button0.resize(80, 50)
        self.button0.move(160, 400)

        self.button1 = QPushButton('Reset', self)
        self.button1.clicked.connect(self.button1_action)
        self.button1.resize(80, 50)
        self.button1.move(260, 400)
        self.show( )

    def button0_action(self) :
        self.textedit2.setText("")

        text = self.textedit.toPlainText( )
        for word in Window.vulgarism_list:
            stars = "".join("*" for _ in word)
            text = text.replace(word, stars)

        Window.message = []

        for ascii in text:
            bin_ascii = str(bin(int(ord(ascii))))[2:]
            if len(bin_ascii) > 7:
                self.textedit2.clear()
                self.textedit2.append("Tekst zawiera niedozwolone znaki")
                Window.message = []
                break
            pad = ""
            for _ in range(8 - len(bin_ascii)):
                pad += "0"
            bin_ascii = pad + bin_ascii
            bin_frame = "0" + bin_ascii + "11"
            Window.message.append(bin_frame)
            self.textedit2.append(bin_frame)

        self.textedit2.setEnabled(True)

    def button1_action(self) :
        self.textedit.clear( )
        self.textedit2.clear( )
        self.textedit2.setDisabled(True)

    def close(self) :
        self.destroy( )

    def closeEvent(self, QCloseEvent) :
        QCloseEvent.ignore( )
        self.close( )

    def close_window(self) :
        self.destroy( )


class childWindowreciv(QDialog) :
    def __init__(self, parent=None) :
        super(childWindowreciv, self).__init__( )
        self.setGeometry(1100, 300, 500, 250)
        self.win = QWidget(self)
        self.parent = parent
        self.setWindowTitle("Odbiorca")

        self.label = QLabel("Odebrany tekst", self)
        self.label.resize(100, 50)
        self.label.move(200, 15)

        self.button0 = QPushButton('Odbierz', self)
        self.button0.clicked.connect(self.button0_action)
        self.button0.resize(80, 50)
        self.button0.move(200, 180)

        self.textedit = QTextEdit("", self)
        self.textedit.move(50, 60)
        self.textedit.setFont(QtGui.QFont('SansSerif', 9))
        self.textedit.resize(400, 100)
        self.textedit.setDisabled(True)

        self.show( )

    def button0_action(self) :
        self.textedit.setDisabled(False)
        message = ""
        if Window.message is not []:
            for frame in Window.message :
                ascii_bin = frame[1 :-2]
                ascii_dec = 0
                power = 7
                for bit in ascii_bin :
                    ascii_dec += int(bit) * (2 ** power)
                    power -= 1
                message += chr(ascii_dec)
            self.textedit.setText(message)
        else:
            self.textedit.setText("Blad komunikacji lub nic nie wyslano")


    def close(self) :
        self.destroy( )

    def closeEvent(self, QCloseEvent) :
        QCloseEvent.ignore( )
        self.close( )

    def close_window(self) :
        self.destroy( )


if __name__ == '__main__' :
    app = QApplication(sys.argv)
    GUI = Window( )
    sys.exit(app.exec( ))