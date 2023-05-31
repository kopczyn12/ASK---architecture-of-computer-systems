# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer
import pickle
import datetime
import copy
from threading import Timer
from time import sleep
import pyautogui as pag
from PyQt5.QtWidgets import QMessageBox
from pynput import keyboard

class Ui_MainWindow(object):

    def __init__(self):
        self.text_length = [x for x in range(1, 100)]
        self.instr_list = []
        self.instr_list_copy = []
        self.step_mode = False
        self.app_hour = "0"
        self.app_mins = "0"
        self.key_listener = keyboard.Listener(self.onPress)
        self.key_listener.start( )
        self.key_pressed = None
        self.timer = QTimer( )
        self.delay = 1000
        self.Error = False


    def onPress(self, key) :
        try:
            self.key_pressed = key.char
        except AttributeError:
            pass

    def setDate(self):
        now = datetime.datetime.now( )
        date = str(now)[0:10]
        time = str(now)[11:19]
        self.Date.setText(date)
        self.app_hour = time[0 :2]
        self.app_mins = time[3:5]
        secs = time[6:8]
        self.Hour.display(self.app_hour)
        self.Minute.display(self.app_mins)
        sleep(60 - int(secs))
        while True:
            self.app_mins = str(int(self.app_mins) +1)
            if int(self.app_hour) > 23:
                self.app_mins = "0"
            if int(self.app_mins) > 59:
                self.app_mins = "0"
                self.app_hour = str(int(self.app_hour) + 1)

            self.Hour.display(self.app_hour)
            self.Minute.display(self.app_mins)
            sleep(60)

    def updateDecimal(self, num, decimal, trig) :
        value = int(decimal.text( ))
        value = value + num if trig else value - num
        decimal.setText(str(value))

    def restart(self,index) :
        for i in range(8) :
            self.buttons[index][i].setText("0")
        self.dec[index].setText("0")

    def restartProgram(self):
        self.Msg.setText("-")
        self.Restart.setVisible(False)
        self.text_length = [x for x in range(1, 100)]
        self.textEdit.clear( )
        for instr in self.instr_list:
            num = self.text_length.pop(0)
            ins = instr[0]
            dest = instr[1]
            src = instr[2]
            dot = ", "

            try :
                if instr[2].isnumeric( ) : dot += "#"
            except AttributeError :
                pass

            self.printProgramLine(num, ins, dest, dot, src)

    def saveFile(self):
        self.turnOffStepMode( )
        file, _ = QtWidgets.QFileDialog.getSaveFileName( )
        if file:
            with open(file, 'wb') as f :
                pickle.dump(self.instr_list, f)
            f.close()
        self.Msg.setText("Program saved")

    def printProgramLine(self,num,instr,dest,dot,src):
        if src and dest :
            line = instr + " " + dest + dot + src
        elif src :
            line = instr + " " + src
        elif dest :
            line = instr + " " + dest
        else :
            line = instr

        if num < 10 :
            self.textEdit.append(str(str(num) + "  | " + line))
        else :
            self.textEdit.append(str(str(num) + "| " + line))

    def loadFile(self):
        self.turnOffStepMode()
        file , _ = QtWidgets.QFileDialog.getOpenFileName( )
        if file :
            with open(file, 'rb') as f:
                self.instr_list = pickle.load(f)
                self.restartProgram()
            f.close()
        self.Msg.setText("-")

    def clearProgram(self) :
        self.Msg.setText("-")
        self.instr_list = []
        self.text_length = [x for x in range(1, 100)]
        self.instr_list_copy = []
        self.turnOffStepMode()

    def handleError(self):
        if self.step_mode :
            self.turnOffStepMode( )
            self.Msg.setText("Step mode is stopped - an error occured")
            self.Restart.setVisible(True)

    def getBinary(self,x):
        bin = [0 for x in range(16)]
        for i in reversed(range(16)):
            buf = x
            k = x % 2
            bin[i] = k
            x = x // 2
            if buf == x: break
        return bin

    def operation(self, dst, bin_val):
        if dst[1] != 'X' :
            for i in range(8, 16) :
                if self.buttons[dst][i - 8].text( ) != str(bin_val[i]) : self.buttons[dst][i - 8].click( )
        else :
            for i in range(8) :
                if self.buttons[dst[0] + "H"][i].text( ) != str(bin_val[i]) : self.buttons[dst[0] + "H"][i].click( )
            for i in range(8, 16) :
                if self.buttons[dst[0] + "L"][i - 8].text( ) != str(bin_val[i]) : self.buttons[dst[0] + "L"][i - 8].click( )

    def MOV(self, dst, src):
        if src.isnumeric():
            out = self.getBinary(int(src))
            self.operation(dst,out)
        elif (dst[1] != 'X' and src[1] != 'X') or dst[1] == src[1] :
            out = []
            if dst[1] != 'X':
                out = [0 for _ in range(8)]
                for button in self.buttons[src] :
                    out.append(int(button.text( )))
            else:
                for button in self.buttons[src[0] + "H"] :
                    out.append(int(button.text( )))
                for button in self.buttons[src[0] + "L"] :
                    out.append(int(button.text( )))

            self.operation(dst,out)
        else :
            self.Msg.setText("MOV " + dst + "," + src + " - Error: sizes of registers are not equal")
            self.handleError()


    def ADD(self, dst, src):
        if src.isnumeric():
            out = int(self.dec[dst].text( )) + int(src)
            out = self.getBinary(out)
            self.operation(dst,out)

        elif (dst[1] != 'X' and src[1] != 'X') or dst[1] == src[1]:
            out = int(self.dec[dst].text( )) + int(self.dec[src].text( ))
            out = self.getBinary(out)
            self.operation(dst, out)

        else :
            self.Msg.setText("ADD " + dst + "," + src + " - Error: sizes of registers are not equal")
            self.handleError()

    def SUB(self, dst, src) :
        if src.isnumeric():
            out = int(self.dec[dst].text( )) - int(src)
            if out < 0 : out = out % 256
            out = self.getBinary(out)
            self.operation(dst, out)

        elif (dst[1] != 'X' and src[1] != 'X') or dst[1] == src[1]:
            out = int(self.dec[dst].text( )) - int(self.dec[src].text( ))
            if out < 0 : out = out % 256
            out = self.getBinary(out)
            self.operation(dst, out)

        else:
            self.Msg.setText("SUB " + dst + "," + src + " - Error: sizes of registers are not equal")
            self.handleError()

    def visible_mode(self) :
        if self.instr.currentIndex() > 2 :
            visible = False
        else:
            visible = True
        self.radio1.setVisible(visible)
        self.radio2.setVisible(visible)
        self.opt1.setVisible(visible)
        self.opt2.setVisible(visible)
        self.Decimal2.setVisible(visible)


    def addInstr(self) :
        if not self.step_mode:
            num = self.text_length.pop(0)
            instr = self.instr.currentText( )

            if self.instr.currentIndex() <= 2:
                src = self.opt1.currentText( ) if self.radio1.isChecked( ) else self.opt2.text( )
                dest = self.dest.currentText( )
            elif self.instr.currentIndex( ) == 3:
                src = self.dest.currentText()
                dest = None
            elif self.instr.currentIndex( ) == 4:
                src = None
                dest = self.dest.currentText()

            self.instr_list.append([instr, dest, src])

            dot = ", "
            if self.radio2.isChecked( ) : dot += "#"

            self.printProgramLine(num,instr,dest,dot,src)

    def exec(self):
        if self.instr_list and not self.step_mode:
            for instr in self.instr_list:
                if instr[0] == 'MOV': self.MOV(instr[1],  instr[2])
                elif instr[0] == 'ADD': self.ADD(instr[1], instr[2])
                elif instr[0] == 'SUB': self.SUB(instr[1], instr[2])


    def turnOffStepMode(self):
        if self.step_mode:
            self.timer.stop( )
        self.step_mode = False

    def step(self, curr_instr):
        dot = ", "
        try :
            if curr_instr[2].isnumeric( ) : dot += "#"
        except AttributeError :
            pass
        num = self.text_length.pop(0)
        instr = curr_instr[0]
        dest = curr_instr[1]
        src = curr_instr[2]

        self.printProgramLine(num,instr,dest,dot,src)

        if curr_instr[0] == 'MOV' :
            self.MOV(curr_instr[1], curr_instr[2])
        elif curr_instr[0] == 'ADD' :
            self.ADD(curr_instr[1], curr_instr[2])
        elif curr_instr[0] == 'SUB' :
            self.SUB(curr_instr[1], curr_instr[2])

        if not self.instr_list_copy :
            self.turnOffStepMode( )
        elif self.step_mode:
            self.timer.start(self.delay)

    def execStep(self):
        if self.instr_list_copy and self.step_mode:
            curr_instr = self.instr_list_copy.pop(0)
            self.step(curr_instr)

        elif self.instr_list :
            self.step_mode = True
            self.Msg.setText("Step mode is ON")
            self.instr_list_copy = copy.deepcopy(self.instr_list)
            self.text_length = [x for x in range(1, 100)]
            self.textEdit.setText("")
            curr_instr = self.instr_list_copy.pop(0)
            self.step(curr_instr)


    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1081, 659)
        font = QtGui.QFont()
        font.setPointSize(8)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Registers = QtWidgets.QLabel(self.centralwidget)
        self.Registers.setGeometry(QtCore.QRect(30, 10, 95, 24))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Registers.setFont(font)
        self.Registers.setObjectName("Registers")
        self.AXregister = QtWidgets.QLabel(self.centralwidget)
        self.AXregister.setGeometry(QtCore.QRect(110, 50, 91, 36))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.AXregister.setFont(font)
        self.AXregister.setObjectName("AXregister")
        self.AH = QtWidgets.QLabel(self.centralwidget)
        self.AH.setGeometry(QtCore.QRect(30, 102, 19, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.AH.setFont(font)
        self.AH.setObjectName("AH")
        self.AL = QtWidgets.QLabel(self.centralwidget)
        self.AL.setGeometry(QtCore.QRect(30, 145, 17, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.AL.setFont(font)
        self.AL.setObjectName("AL")
        self.BL = QtWidgets.QLabel(self.centralwidget)
        self.BL.setGeometry(QtCore.QRect(30, 281, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.BL.setFont(font)
        self.BL.setObjectName("BL")
        self.BX = QtWidgets.QLabel(self.centralwidget)
        self.BX.setGeometry(QtCore.QRect(110, 190, 91, 36))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.BX.setFont(font)
        self.BX.setObjectName("BX")
        self.BH = QtWidgets.QLabel(self.centralwidget)
        self.BH.setGeometry(QtCore.QRect(30, 239, 17, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.BH.setFont(font)
        self.BH.setObjectName("BH")
        self.CL = QtWidgets.QLabel(self.centralwidget)
        self.CL.setGeometry(QtCore.QRect(30, 428, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.CL.setFont(font)
        self.CL.setObjectName("CL")
        self.CX = QtWidgets.QLabel(self.centralwidget)
        self.CX.setGeometry(QtCore.QRect(110, 330, 81, 36))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.CX.setFont(font)
        self.CX.setObjectName("CX")
        self.CH = QtWidgets.QLabel(self.centralwidget)
        self.CH.setGeometry(QtCore.QRect(30, 386, 17, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.CH.setFont(font)
        self.CH.setObjectName("CH")
        self.DL = QtWidgets.QLabel(self.centralwidget)
        self.DL.setGeometry(QtCore.QRect(30, 565, 16, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.DL.setFont(font)
        self.DL.setObjectName("DL")
        self.DX = QtWidgets.QLabel(self.centralwidget)
        self.DX.setGeometry(QtCore.QRect(110, 470, 91, 37))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.DX.setFont(font)
        self.DX.setObjectName("DX")
        self.DH = QtWidgets.QLabel(self.centralwidget)
        self.DH.setGeometry(QtCore.QRect(30, 523, 18, 16))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.DH.setFont(font)
        self.DH.setObjectName("DH")
        self.buttons = {"AH" : [], "AL" : [], "BH" : [], "BL" : [], "CH" : [], "CL" : [], "DH" : [], "DL" : []}
        self.dec = {"AX" : 0, "BX": 0, "CX": 0, "DX" : 0, "AH" : 0, "AL" : 0, "BH" : 0, "BL" : 0, "CH" : 0, "CL" : 0, "DH" : 0, "DL" : 0, "opt": 0}


        self.iter1 = 0
        self.iter2 = 0
        self.iter3 = 0
        for key in self.buttons.keys( ) :
            for i in range(8) :
                self.buttons[key].append(QtWidgets.QPushButton(self.centralwidget))
                self.buttons[key][-1].setObjectName(str(key) + str(7 - self.iter2))
                if self.iter1 % 2 == 0 :
                    self.buttons[key][-1].setGeometry(
                        QtCore.QRect(60 + 20 * self.iter2, 100 + 140 * self.iter3, 21, 21))
                else :
                    self.buttons[key][-1].setGeometry(
                        QtCore.QRect(60 + 20 * self.iter2, 140 + 140 * self.iter3, 21, 21))
                self.iter2 += 1
            self.iter2 = 0
            if self.iter1 % 2 == 1 : self.iter3 += 1
            self.iter1 += 1

        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(410, 230, 251, 351))
        self.textEdit.setObjectName("textEdit")
        self.Program = QtWidgets.QLabel(self.centralwidget)
        self.Program.setGeometry(QtCore.QRect(410, 180, 91, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Program.setFont(font)
        self.Program.setObjectName("Program")
        self.restAH = QtWidgets.QPushButton(self.centralwidget)
        self.restAH.setGeometry(QtCore.QRect(230, 100, 51, 21))
        self.restAH.setObjectName("restAH")
        self.Komendy = QtWidgets.QLabel(self.centralwidget)
        self.Komendy.setGeometry(QtCore.QRect(400, 10, 121, 24))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Komendy.setFont(font)
        self.Komendy.setObjectName("Komendy")
        self.Clear = QtWidgets.QPushButton(self.centralwidget)
        self.Clear.setGeometry(QtCore.QRect(680, 350, 111, 28))
        self.Clear.setObjectName("Clear")
        self.Execute = QtWidgets.QPushButton(self.centralwidget)
        self.Execute.setGeometry(QtCore.QRect(680, 520, 111, 28))
        self.Execute.setObjectName("Execute")
        self.Save = QtWidgets.QPushButton(self.centralwidget)
        self.Save.setGeometry(QtCore.QRect(680, 260, 111, 28))
        self.Save.setObjectName("Save")
        self.Load = QtWidgets.QPushButton(self.centralwidget)
        self.Load.setGeometry(QtCore.QRect(680, 230, 111, 28))
        self.Load.setObjectName("Load")
        self.ExecuteStep = QtWidgets.QPushButton(self.centralwidget)
        self.ExecuteStep.setGeometry(QtCore.QRect(680, 550, 111, 28))
        self.ExecuteStep.setObjectName("ExecuteStep")
        self.Restart = QtWidgets.QPushButton(self.centralwidget)
        self.Restart.setGeometry(QtCore.QRect(680, 490, 111, 28))
        self.Restart.setObjectName("Restart")
        self.Restart.setVisible(False)
        self.opt1 = QtWidgets.QComboBox(self.centralwidget)
        self.opt1.setGeometry(QtCore.QRect(610, 71, 73, 21))
        self.opt1.setObjectName("opt1")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.opt1.addItem("")
        self.dest = QtWidgets.QComboBox(self.centralwidget)
        self.dest.setGeometry(QtCore.QRect(500, 100, 73, 22))
        self.dest.setObjectName("dest")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.dest.addItem("")
        self.Add = QtWidgets.QPushButton(self.centralwidget)
        self.Add.setGeometry(QtCore.QRect(710, 90, 81, 41))
        self.Add.setObjectName("Add")
        self.instr = QtWidgets.QComboBox(self.centralwidget)
        self.instr.setGeometry(QtCore.QRect(410, 100, 73, 22))
        self.instr.setObjectName("instr")
        self.instr.addItem("")
        self.instr.addItem("")
        self.instr.addItem("")
        self.instr.addItem("")
        self.instr.addItem("")
        self.opt2 = QtWidgets.QLineEdit(self.centralwidget)
        self.opt2.setGeometry(QtCore.QRect(610, 130, 71, 22))
        self.opt2.setObjectName("opt2")
        self.Decimal2 = QtWidgets.QLabel(self.centralwidget)
        self.Decimal2.setGeometry(QtCore.QRect(620, 110, 51, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.Decimal2.setFont(font)
        self.Decimal2.setObjectName("Decimal2")
        self.dec["AH"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["AH"].setGeometry(QtCore.QRect(290, 100, 71, 22))
        self.dec["AH"].setObjectName("DecAH")
        self.restAL = QtWidgets.QPushButton(self.centralwidget)
        self.restAL.setGeometry(QtCore.QRect(230, 140, 51, 21))
        self.restAL.setObjectName("restAL")
        self.dec["AL"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["AL"].setGeometry(QtCore.QRect(290, 140, 71, 22))
        self.dec["AL"].setObjectName("DecAL")
        self.restBH = QtWidgets.QPushButton(self.centralwidget)
        self.restBH.setGeometry(QtCore.QRect(230, 240, 51, 21))
        self.restBH.setObjectName("restBH")
        self.dec["BH"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["BH"].setGeometry(QtCore.QRect(290, 240, 71, 22))
        self.dec["BH"].setObjectName("DecBH")
        self.restBL = QtWidgets.QPushButton(self.centralwidget)
        self.restBL.setGeometry(QtCore.QRect(230, 280, 51, 21))
        self.restBL.setObjectName("restBL")
        self.dec["BL"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["BL"].setGeometry(QtCore.QRect(290, 280, 71, 22))
        self.dec["BL"].setObjectName("DecBL")
        self.restCH = QtWidgets.QPushButton(self.centralwidget)
        self.restCH.setGeometry(QtCore.QRect(230, 380, 51, 21))
        self.restCH.setObjectName("restCH")
        self.dec["CH"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["CH"].setGeometry(QtCore.QRect(290, 380, 71, 22))
        self.dec["CH"].setObjectName("DecCH")
        self.restCL = QtWidgets.QPushButton(self.centralwidget)
        self.restCL.setGeometry(QtCore.QRect(230, 420, 51, 21))
        self.restCL.setObjectName("restCL")
        self.dec["CL"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["CL"].setGeometry(QtCore.QRect(290, 420, 71, 22))
        self.dec["CL"].setObjectName("DecCL")
        self.restDH = QtWidgets.QPushButton(self.centralwidget)
        self.restDH.setGeometry(QtCore.QRect(230, 520, 51, 21))
        self.restDH.setObjectName("restDH")
        self.dec["DH"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["DH"].setGeometry(QtCore.QRect(290, 520, 71, 22))
        self.dec["DH"].setObjectName("DecDH")
        self.restDL = QtWidgets.QPushButton(self.centralwidget)
        self.restDL.setGeometry(QtCore.QRect(230, 560, 51, 21))
        self.restDL.setObjectName("restDL")
        self.dec["DL"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["DL"].setGeometry(QtCore.QRect(290, 560, 71, 22))
        self.dec["DL"].setObjectName("DecDL")
        self.radio1 = QtWidgets.QRadioButton(self.centralwidget)
        self.radio1.setGeometry(QtCore.QRect(585, 70, 20, 20))
        self.radio1.setText("")
        self.radio1.setObjectName("radio1")
        self.radio1.setChecked(True)
        self.radio2 = QtWidgets.QRadioButton(self.centralwidget)
        self.radio2.setGeometry(QtCore.QRect(585, 130, 20, 20))
        self.radio2.setText("")
        self.radio2.setObjectName("radio2")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(510, 190, 271, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(520, 20, 261, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setGeometry(QtCore.QRect(130, 20, 251, 16))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.dec["AX"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["AX"].setGeometry(QtCore.QRect(290, 60, 71, 22))
        self.dec["AX"].setObjectName("DecAX")
        self.dec["BX"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["BX"].setGeometry(QtCore.QRect(290, 200, 71, 22))
        self.dec["BX"].setObjectName("DecBX")
        self.dec["CX"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["CX"].setGeometry(QtCore.QRect(290, 340, 71, 22))
        self.dec["CX"].setObjectName("DecCX")
        self.dec["DX"] = QtWidgets.QLineEdit(self.centralwidget)
        self.dec["DX"].setGeometry(QtCore.QRect(290, 480, 71, 22))
        self.dec["DX"].setObjectName("DecDX")
        self.Decimal1 = QtWidgets.QLabel(self.centralwidget)
        self.Decimal1.setGeometry(QtCore.QRect(300, 40, 91, 36))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.Decimal1.setFont(font)
        self.Decimal1.setObjectName("Decimal1")
        font = QtGui.QFont( )
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)

        self.line_4 = QtWidgets.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(940, 20, 121, 21))
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.line_5 = QtWidgets.QFrame(self.centralwidget)
        self.line_5.setGeometry(QtCore.QRect(890, 190, 171, 21))
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        font = QtGui.QFont( )
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Hour = QtWidgets.QLCDNumber(self.centralwidget)
        self.Hour.setGeometry(QtCore.QRect(880, 500, 51, 41))
        font = QtGui.QFont( )
        font.setPointSize(30)
        font.setBold(True)
        font.setWeight(75)
        self.Hour.setFont(font)
        self.Hour.setSmallDecimalPoint(False)
        self.Hour.setDigitCount(2)
        self.Hour.setProperty("value", 15.0)
        self.Hour.setProperty("intValue", 15)
        self.Hour.setObjectName("Hour")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(940, 500, 16, 41))
        font = QtGui.QFont( )
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.Minute = QtWidgets.QLCDNumber(self.centralwidget)
        self.Minute.setGeometry(QtCore.QRect(960, 500, 51, 41))
        font = QtGui.QFont( )
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.Minute.setFont(font)
        self.Minute.setSmallDecimalPoint(False)
        self.Minute.setDigitCount(2)
        self.Minute.setProperty("value", 15.0)
        self.Minute.setProperty("intValue", 15)
        self.Minute.setObjectName("Minute")
        self.TimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.TimeLabel.setGeometry(QtCore.QRect(820, 450, 131, 24))
        font = QtGui.QFont( )
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.TimeLabel.setFont(font)
        self.TimeLabel.setObjectName("TimeLabel")
        self.line_6 = QtWidgets.QFrame(self.centralwidget)
        self.line_6.setGeometry(QtCore.QRect(880, 460, 191, 21))
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")

        self.Info= QtWidgets.QLabel(self.centralwidget)
        self.Info.setGeometry(QtCore.QRect(410, 580, 111, 16))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.Info.setFont(font)
        self.Info.setObjectName("Info")

        self.Msg= QtWidgets.QLabel(self.centralwidget)
        self.Msg.setGeometry(QtCore.QRect(440, 580, 400, 16))
        self.Msg.setStyleSheet('color: red')
        font = QtGui.QFont()
        font.setPointSize(6)
        #font.setBold(True)
        font.setWeight(75)
        self.Msg.setFont(font)
        self.Msg.setObjectName("Msg")

        self.Date = QtWidgets.QLabel(self.centralwidget)
        self.Date.setGeometry(QtCore.QRect(900, 560, 111, 16))
        font = QtGui.QFont( )
        font.setPointSize(12)
        self.Date.setFont(font)
        self.Date.setObjectName("Date")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1081, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)


        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.buttons["AH"][0].clicked.connect(
            lambda : self.buttons["AH"][0].setText("1") if self.buttons["AH"][0].text( ) == "0" else self.buttons["AH"][0].setText("0"))
        self.buttons["AH"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["AH"],int(self.buttons["AH"][0].text())))

        self.buttons["AH"][1].clicked.connect(
            lambda : self.buttons["AH"][1].setText("1") if self.buttons["AH"][1].text( ) == "0" else self.buttons["AH"][
                1].setText("0"))
        self.buttons["AH"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["AH"],int(self.buttons["AH"][1].text())))

        self.buttons["AH"][2].clicked.connect(
            lambda : self.buttons["AH"][2].setText("1") if self.buttons["AH"][2].text( ) == "0" else self.buttons["AH"][
                2].setText("0"))
        self.buttons["AH"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["AH"],int(self.buttons["AH"][2].text())))

        self.buttons["AH"][3].clicked.connect(
            lambda : self.buttons["AH"][3].setText("1") if self.buttons["AH"][3].text( ) == "0" else self.buttons["AH"][
                3].setText("0"))
        self.buttons["AH"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["AH"],int(self.buttons["AH"][3].text())))

        self.buttons["AH"][4].clicked.connect(
            lambda : self.buttons["AH"][4].setText("1") if self.buttons["AH"][4].text( ) == "0" else self.buttons["AH"][
                4].setText("0"))
        self.buttons["AH"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["AH"],int(self.buttons["AH"][4].text())))

        self.buttons["AH"][5].clicked.connect(
            lambda : self.buttons["AH"][5].setText("1") if self.buttons["AH"][5].text( ) == "0" else self.buttons["AH"][
                5].setText("0"))
        self.buttons["AH"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["AH"],int(self.buttons["AH"][5].text())))

        self.buttons["AH"][6].clicked.connect(
            lambda : self.buttons["AH"][6].setText("1") if self.buttons["AH"][6].text( ) == "0" else self.buttons["AH"][
                6].setText("0"))
        self.buttons["AH"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["AH"],int(self.buttons["AH"][6].text())))

        self.buttons["AH"][7].clicked.connect(
            lambda : self.buttons["AH"][7].setText("1") if self.buttons["AH"][7].text( ) == "0" else self.buttons["AH"][
                7].setText("0"))
        self.buttons["AH"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["AH"],int(self.buttons["AH"][7].text())))


        self.buttons["AL"][0].clicked.connect(
            lambda : self.buttons["AL"][0].setText("1") if self.buttons["AL"][0].text( ) == "0" else self.buttons["AL"][
                0].setText("0"))
        self.buttons["AL"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["AL"],int(self.buttons["AL"][0].text())))

        self.buttons["AL"][1].clicked.connect(
            lambda : self.buttons["AL"][1].setText("1") if self.buttons["AL"][1].text( ) == "0" else self.buttons["AL"][
                1].setText("0"))
        self.buttons["AL"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["AL"],int(self.buttons["AL"][1].text())))

        self.buttons["AL"][2].clicked.connect(
            lambda : self.buttons["AL"][2].setText("1") if self.buttons["AL"][2].text( ) == "0" else self.buttons["AL"][
                2].setText("0"))
        self.buttons["AL"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["AL"],int(self.buttons["AL"][2].text())))

        self.buttons["AL"][3].clicked.connect(
            lambda : self.buttons["AL"][3].setText("1") if self.buttons["AL"][3].text( ) == "0" else self.buttons["AL"][
                3].setText("0"))
        self.buttons["AL"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["AL"],int(self.buttons["AL"][3].text())))

        self.buttons["AL"][4].clicked.connect(
            lambda : self.buttons["AL"][4].setText("1") if self.buttons["AL"][4].text( ) == "0" else self.buttons["AL"][
                4].setText("0"))
        self.buttons["AL"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["AL"],int(self.buttons["AL"][4].text())))

        self.buttons["AL"][5].clicked.connect(
            lambda : self.buttons["AL"][5].setText("1") if self.buttons["AL"][5].text( ) == "0" else self.buttons["AL"][
                5].setText("0"))
        self.buttons["AL"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["AL"],int(self.buttons["AL"][5].text())))

        self.buttons["AL"][6].clicked.connect(
            lambda : self.buttons["AL"][6].setText("1") if self.buttons["AL"][6].text( ) == "0" else self.buttons["AL"][
                6].setText("0"))
        self.buttons["AL"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["AL"],int(self.buttons["AL"][6].text())))

        self.buttons["AL"][7].clicked.connect(
            lambda : self.buttons["AL"][7].setText("1") if self.buttons["AL"][7].text( ) == "0" else self.buttons["AL"][
                7].setText("0"))
        self.buttons["AL"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["AL"],int(self.buttons["AL"][7].text())))


        self.buttons["BH"][0].clicked.connect(
            lambda : self.buttons["BH"][0].setText("1") if self.buttons["BH"][0].text( ) == "0" else self.buttons["BH"][
                0].setText("0"))
        self.buttons["BH"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["BH"],int(self.buttons["BH"][0].text())))

        self.buttons["BH"][1].clicked.connect(
            lambda : self.buttons["BH"][1].setText("1") if self.buttons["BH"][1].text( ) == "0" else self.buttons["BH"][
                1].setText("0"))
        self.buttons["BH"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["BH"],int(self.buttons["BH"][1].text())))

        self.buttons["BH"][2].clicked.connect(
            lambda : self.buttons["BH"][2].setText("1") if self.buttons["BH"][2].text( ) == "0" else self.buttons["BH"][
                2].setText("0"))
        self.buttons["BH"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["BH"],int(self.buttons["BH"][2].text())))

        self.buttons["BH"][3].clicked.connect(
            lambda : self.buttons["BH"][3].setText("1") if self.buttons["BH"][3].text( ) == "0" else self.buttons["BH"][
                3].setText("0"))
        self.buttons["BH"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["BH"],int(self.buttons["BH"][3].text())))

        self.buttons["BH"][4].clicked.connect(
            lambda : self.buttons["BH"][4].setText("1") if self.buttons["BH"][4].text( ) == "0" else self.buttons["BH"][
                4].setText("0"))
        self.buttons["BH"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["BH"],int(self.buttons["BH"][4].text())))

        self.buttons["BH"][5].clicked.connect(
            lambda : self.buttons["BH"][5].setText("1") if self.buttons["BH"][5].text( ) == "0" else self.buttons["BH"][
                5].setText("0"))
        self.buttons["BH"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["BH"],int(self.buttons["BH"][5].text())))

        self.buttons["BH"][6].clicked.connect(
            lambda : self.buttons["BH"][6].setText("1") if self.buttons["BH"][6].text( ) == "0" else self.buttons["BH"][
                6].setText("0"))
        self.buttons["BH"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["BH"],int(self.buttons["BH"][6].text())))

        self.buttons["BH"][7].clicked.connect(
            lambda : self.buttons["BH"][7].setText("1") if self.buttons["BH"][7].text( ) == "0" else self.buttons["BH"][
                7].setText("0"))
        self.buttons["BH"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["BH"],int(self.buttons["BH"][7].text())))


        self.buttons["BL"][0].clicked.connect(
            lambda : self.buttons["BL"][0].setText("1") if self.buttons["BL"][0].text( ) == "0" else self.buttons["BL"][
                0].setText("0"))
        self.buttons["BL"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["BL"],int(self.buttons["BL"][0].text())))

        self.buttons["BL"][1].clicked.connect(
            lambda : self.buttons["BL"][1].setText("1") if self.buttons["BL"][1].text( ) == "0" else self.buttons["BL"][
                1].setText("0"))
        self.buttons["BL"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["BL"],int(self.buttons["BL"][1].text())))

        self.buttons["BL"][2].clicked.connect(
            lambda : self.buttons["BL"][2].setText("1") if self.buttons["BL"][2].text( ) == "0" else self.buttons["BL"][
                2].setText("0"))
        self.buttons["BL"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["BL"],int(self.buttons["BL"][2].text())))

        self.buttons["BL"][3].clicked.connect(
            lambda : self.buttons["BL"][3].setText("1") if self.buttons["BL"][3].text( ) == "0" else self.buttons["BL"][
                3].setText("0"))
        self.buttons["BL"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["BL"],int(self.buttons["BL"][3].text())))

        self.buttons["BL"][4].clicked.connect(
            lambda : self.buttons["BL"][4].setText("1") if self.buttons["BL"][4].text( ) == "0" else self.buttons["BL"][
                4].setText("0"))
        self.buttons["BL"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["BL"],int(self.buttons["BL"][4].text())))

        self.buttons["BL"][5].clicked.connect(
            lambda : self.buttons["BL"][5].setText("1") if self.buttons["BL"][5].text( ) == "0" else self.buttons["BL"][
                5].setText("0"))
        self.buttons["BL"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["BL"],int(self.buttons["BL"][5].text())))

        self.buttons["BL"][6].clicked.connect(
            lambda : self.buttons["BL"][6].setText("1") if self.buttons["BL"][6].text( ) == "0" else self.buttons["BL"][
                6].setText("0"))
        self.buttons["BL"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["BL"],int(self.buttons["BL"][6].text())))

        self.buttons["BL"][7].clicked.connect(
            lambda : self.buttons["BL"][7].setText("1") if self.buttons["BL"][7].text( ) == "0" else self.buttons["BL"][
                7].setText("0"))
        self.buttons["BL"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["BL"],int(self.buttons["BL"][7].text())))


        self.buttons["CH"][0].clicked.connect(
            lambda : self.buttons["CH"][0].setText("1") if self.buttons["CH"][0].text( ) == "0" else self.buttons["CH"][
                0].setText("0"))
        self.buttons["CH"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["CH"],int(self.buttons["CH"][0].text())))

        self.buttons["CH"][1].clicked.connect(
            lambda : self.buttons["CH"][1].setText("1") if self.buttons["CH"][1].text( ) == "0" else self.buttons["CH"][
                1].setText("0"))
        self.buttons["CH"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["CH"],int(self.buttons["CH"][1].text())))

        self.buttons["CH"][2].clicked.connect(
            lambda : self.buttons["CH"][2].setText("1") if self.buttons["CH"][2].text( ) == "0" else self.buttons["CH"][
                2].setText("0"))
        self.buttons["CH"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["CH"],int(self.buttons["CH"][2].text())))

        self.buttons["CH"][3].clicked.connect(
            lambda : self.buttons["CH"][3].setText("1") if self.buttons["CH"][3].text( ) == "0" else self.buttons["CH"][
                3].setText("0"))
        self.buttons["CH"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["CH"],int(self.buttons["CH"][3].text())))

        self.buttons["CH"][4].clicked.connect(
            lambda : self.buttons["CH"][4].setText("1") if self.buttons["CH"][4].text( ) == "0" else self.buttons["CH"][
                4].setText("0"))
        self.buttons["CH"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["CH"],int(self.buttons["CH"][4].text())))

        self.buttons["CH"][5].clicked.connect(
            lambda : self.buttons["CH"][5].setText("1") if self.buttons["CH"][5].text( ) == "0" else self.buttons["CH"][
                5].setText("0"))
        self.buttons["CH"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["CH"],int(self.buttons["CH"][5].text())))

        self.buttons["CH"][6].clicked.connect(
            lambda : self.buttons["CH"][6].setText("1") if self.buttons["CH"][6].text( ) == "0" else self.buttons["CH"][
                6].setText("0"))
        self.buttons["CH"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["CH"],int(self.buttons["CH"][6].text())))

        self.buttons["CH"][7].clicked.connect(
            lambda : self.buttons["CH"][7].setText("1") if self.buttons["CH"][7].text( ) == "0" else self.buttons["CH"][
                7].setText("0"))
        self.buttons["CH"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["CH"],int(self.buttons["CH"][7].text())))


        self.buttons["CL"][0].clicked.connect(
            lambda : self.buttons["CL"][0].setText("1") if self.buttons["CL"][0].text( ) == "0" else self.buttons["CL"][
                0].setText("0"))
        self.buttons["CL"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["CL"],int(self.buttons["CL"][0].text())))

        self.buttons["CL"][1].clicked.connect(
            lambda : self.buttons["CL"][1].setText("1") if self.buttons["CL"][1].text( ) == "0" else self.buttons["CL"][
                1].setText("0"))
        self.buttons["CL"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["CL"],int(self.buttons["CL"][1].text())))

        self.buttons["CL"][2].clicked.connect(
            lambda : self.buttons["CL"][2].setText("1") if self.buttons["CL"][2].text( ) == "0" else self.buttons["CL"][
                2].setText("0"))
        self.buttons["CL"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["CL"],int(self.buttons["CL"][2].text())))

        self.buttons["CL"][3].clicked.connect(
            lambda : self.buttons["CL"][3].setText("1") if self.buttons["CL"][3].text( ) == "0" else self.buttons["CL"][
                3].setText("0"))
        self.buttons["CL"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["CL"],int(self.buttons["CL"][3].text())))

        self.buttons["CL"][4].clicked.connect(
            lambda : self.buttons["CL"][4].setText("1") if self.buttons["CL"][4].text( ) == "0" else self.buttons["CL"][
                4].setText("0"))
        self.buttons["CL"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["CL"],int(self.buttons["CL"][4].text())))

        self.buttons["CL"][5].clicked.connect(
            lambda : self.buttons["CL"][5].setText("1") if self.buttons["CL"][5].text( ) == "0" else self.buttons["CL"][
                5].setText("0"))
        self.buttons["CL"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["CL"],int(self.buttons["CL"][5].text())))

        self.buttons["CL"][6].clicked.connect(
            lambda : self.buttons["CL"][6].setText("1") if self.buttons["CL"][6].text( ) == "0" else self.buttons["CL"][
                6].setText("0"))
        self.buttons["CL"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["CL"],int(self.buttons["CL"][6].text())))

        self.buttons["CL"][7].clicked.connect(
            lambda : self.buttons["CL"][7].setText("1") if self.buttons["CL"][7].text( ) == "0" else self.buttons["CL"][
                7].setText("0"))
        self.buttons["CL"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["CL"],int(self.buttons["CL"][7].text())))


        self.buttons["DH"][0].clicked.connect(
            lambda : self.buttons["DH"][0].setText("1") if self.buttons["DH"][0].text( ) == "0" else self.buttons["DH"][
                0].setText("0"))
        self.buttons["DH"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["DH"],int(self.buttons["DH"][0].text())))

        self.buttons["DH"][1].clicked.connect(
            lambda : self.buttons["DH"][1].setText("1") if self.buttons["DH"][1].text( ) == "0" else self.buttons["DH"][
                1].setText("0"))
        self.buttons["DH"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["DH"],int(self.buttons["DH"][1].text())))

        self.buttons["DH"][2].clicked.connect(
            lambda : self.buttons["DH"][2].setText("1") if self.buttons["DH"][2].text( ) == "0" else self.buttons["DH"][
                2].setText("0"))
        self.buttons["DH"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["DH"],int(self.buttons["DH"][2].text())))

        self.buttons["DH"][3].clicked.connect(
            lambda : self.buttons["DH"][3].setText("1") if self.buttons["DH"][3].text( ) == "0" else self.buttons["DH"][
                3].setText("0"))
        self.buttons["DH"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["DH"],int(self.buttons["DH"][3].text())))

        self.buttons["DH"][4].clicked.connect(
            lambda : self.buttons["DH"][4].setText("1") if self.buttons["DH"][4].text( ) == "0" else self.buttons["DH"][
                4].setText("0"))
        self.buttons["DH"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["DH"],int(self.buttons["DH"][4].text())))

        self.buttons["DH"][5].clicked.connect(
            lambda : self.buttons["DH"][5].setText("1") if self.buttons["DH"][5].text( ) == "0" else self.buttons["DH"][
                5].setText("0"))
        self.buttons["DH"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["DH"],int(self.buttons["DH"][5].text())))

        self.buttons["DH"][6].clicked.connect(
            lambda : self.buttons["DH"][6].setText("1") if self.buttons["DH"][6].text( ) == "0" else self.buttons["DH"][
                6].setText("0"))
        self.buttons["DH"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["DH"],int(self.buttons["DH"][6].text())))

        self.buttons["DH"][7].clicked.connect(
            lambda : self.buttons["DH"][7].setText("1") if self.buttons["DH"][7].text( ) == "0" else self.buttons["DH"][
                7].setText("0"))
        self.buttons["DH"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["DH"],int(self.buttons["DH"][7].text())))


        self.buttons["DL"][0].clicked.connect(
            lambda : self.buttons["DL"][0].setText("1") if self.buttons["DL"][0].text( ) == "0" else self.buttons["DL"][
                0].setText("0"))
        self.buttons["DL"][0].clicked.connect(lambda: self.updateDecimal(128, self.dec["DL"],int(self.buttons["DL"][0].text())))

        self.buttons["DL"][1].clicked.connect(
            lambda : self.buttons["DL"][1].setText("1") if self.buttons["DL"][1].text( ) == "0" else self.buttons["DL"][
                1].setText("0"))
        self.buttons["DL"][1].clicked.connect(lambda: self.updateDecimal(64, self.dec["DL"],int(self.buttons["DL"][1].text())))

        self.buttons["DL"][2].clicked.connect(
            lambda : self.buttons["DL"][2].setText("1") if self.buttons["DL"][2].text( ) == "0" else self.buttons["DL"][
                2].setText("0"))
        self.buttons["DL"][2].clicked.connect(lambda: self.updateDecimal(32, self.dec["DL"],int(self.buttons["DL"][2].text())))

        self.buttons["DL"][3].clicked.connect(
            lambda : self.buttons["DL"][3].setText("1") if self.buttons["DL"][3].text( ) == "0" else self.buttons["DL"][
                3].setText("0"))
        self.buttons["DL"][3].clicked.connect(lambda: self.updateDecimal(16, self.dec["DL"],int(self.buttons["DL"][3].text())))

        self.buttons["DL"][4].clicked.connect(
            lambda : self.buttons["DL"][4].setText("1") if self.buttons["DL"][4].text( ) == "0" else self.buttons["DL"][
                4].setText("0"))
        self.buttons["DL"][4].clicked.connect(lambda: self.updateDecimal(8, self.dec["DL"],int(self.buttons["DL"][4].text())))

        self.buttons["DL"][5].clicked.connect(
            lambda : self.buttons["DL"][5].setText("1") if self.buttons["DL"][5].text( ) == "0" else self.buttons["DL"][
                5].setText("0"))
        self.buttons["DL"][5].clicked.connect(lambda: self.updateDecimal(4, self.dec["DL"],int(self.buttons["DL"][5].text())))

        self.buttons["DL"][6].clicked.connect(
            lambda : self.buttons["DL"][6].setText("1") if self.buttons["DL"][6].text( ) == "0" else self.buttons["DL"][
                6].setText("0"))
        self.buttons["DL"][6].clicked.connect(lambda: self.updateDecimal(2, self.dec["DL"],int(self.buttons["DL"][6].text())))

        self.buttons["DL"][7].clicked.connect(
            lambda : self.buttons["DL"][7].setText("1") if self.buttons["DL"][7].text( ) == "0" else self.buttons["DL"][
                7].setText("0"))
        self.buttons["DL"][7].clicked.connect(lambda: self.updateDecimal(1, self.dec["DL"],int(self.buttons["DL"][7].text())))

        self.restAH.clicked.connect(lambda : self.restart("AH"))
        self.restAL.clicked.connect(lambda : self.restart("AL"))
        self.restBH.clicked.connect(lambda : self.restart("BH"))
        self.restBL.clicked.connect(lambda : self.restart("BL"))
        self.restCH.clicked.connect(lambda : self.restart("CH"))
        self.restCL.clicked.connect(lambda : self.restart("CL"))
        self.restDH.clicked.connect(lambda : self.restart("DH"))
        self.restDL.clicked.connect(lambda : self.restart("DL"))

        self.instr.activated.connect(lambda: self.visible_mode())

        self.Add.clicked.connect(
            lambda: self.addInstr()
        )

        self.Execute.clicked.connect(
            lambda : self.exec( )
        )

        self.ExecuteStep.clicked.connect(
            lambda : self.execStep( )
        )

        self.Restart.clicked.connect(
            lambda : self.restartProgram( )
        )

        self.Clear.clicked.connect(
            lambda: self.textEdit.clear( )
        )

        self.Clear.clicked.connect(
            lambda : self.clearProgram()
        )

        self.dec["AH"].textChanged.connect(
            lambda: self.dec["AX"].setText(str(int(self.dec["AH"].text())*256 + int(self.dec["AL"].text()))) )
        self.dec["AL"].textChanged.connect(
            lambda: self.dec["AX"].setText(str(int(self.dec["AH"].text())*256 + int(self.dec["AL"].text()))) )
        self.dec["BH"].textChanged.connect(
            lambda: self.dec["BX"].setText(str(int(self.dec["BH"].text())*256 + int(self.dec["BL"].text()))) )
        self.dec["BL"].textChanged.connect(
            lambda: self.dec["BX"].setText(str(int(self.dec["BH"].text())*256 + int(self.dec["BL"].text()))) )
        self.dec["CH"].textChanged.connect(
            lambda: self.dec["CX"].setText(str(int(self.dec["CH"].text())*256 + int(self.dec["CL"].text()))) )
        self.dec["CL"].textChanged.connect(
            lambda: self.dec["CX"].setText(str(int(self.dec["CH"].text())*256 + int(self.dec["CL"].text()))) )
        self.dec["DH"].textChanged.connect(
            lambda: self.dec["DX"].setText(str(int(self.dec["DH"].text())*256 + int(self.dec["DL"].text()))) )
        self.dec["DL"].textChanged.connect(
            lambda: self.dec["DX"].setText(str(int(self.dec["DH"].text())*256 + int(self.dec["DL"].text()))) )

        self.Save.clicked.connect(
            lambda: self.saveFile()
        )

        self.Load.clicked.connect(
            lambda: self.loadFile()
        )

        self.timer.timeout.connect(
            lambda: self.ExecuteStep.click()
        )

        global t
        t = Timer(0, self.setDate)
        t.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Registers.setText(_translate("MainWindow", "Registers"))
        self.AXregister.setText(_translate("MainWindow", "AX Register"))
        self.AH.setText(_translate("MainWindow", "AH"))
        self.AL.setText(_translate("MainWindow", "AL"))
        self.BL.setText(_translate("MainWindow", "BL"))
        self.BX.setText(_translate("MainWindow", "BX Register"))
        self.BH.setText(_translate("MainWindow", "BH"))
        self.CL.setText(_translate("MainWindow", "CL"))
        self.CX.setText(_translate("MainWindow", "CX Register"))
        self.CH.setText(_translate("MainWindow", "CH"))
        self.DL.setText(_translate("MainWindow", "DL"))
        self.DX.setText(_translate("MainWindow", "DX Register"))
        self.DH.setText(_translate("MainWindow", "DH"))
        for key in self.buttons.keys():
            for i in range(8):
                self.buttons[key][i].setText(_translate("MainWindow", "0"))

        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.Program.setText(_translate("MainWindow", "Program"))
        self.dec["AH"].setText(_translate("MainWindow", "0"))
        self.restAH.setText(_translate("MainWindow", "Reset"))
        self.Komendy.setText(_translate("MainWindow", "<html><head/><body><p>Instruction</p><p><br/></p></body></html>"))
        self.Clear.setText(_translate("MainWindow", "Clear"))
        self.Execute.setText(_translate("MainWindow", "Execute"))
        self.Save.setText(_translate("MainWindow", "Save to file"))
        self.Load.setText(_translate("MainWindow", "Load from file"))
        self.ExecuteStep.setText(_translate("MainWindow", "Step exec."))
        self.Restart.setText(_translate("MainWindow", "Show full program"))
        self.opt1.setItemText(0, _translate("MainWindow", "AH"))
        self.opt1.setItemText(1, _translate("MainWindow", "AL"))
        self.opt1.setItemText(2, _translate("MainWindow", "BH"))
        self.opt1.setItemText(3, _translate("MainWindow", "BL"))
        self.opt1.setItemText(4, _translate("MainWindow", "CH"))
        self.opt1.setItemText(5, _translate("MainWindow", "CL"))
        self.opt1.setItemText(6, _translate("MainWindow", "DH"))
        self.opt1.setItemText(7, _translate("MainWindow", "DL"))
        self.opt1.setItemText(8, _translate("MainWindow", "AX"))
        self.opt1.setItemText(9, _translate("MainWindow", "BX"))
        self.opt1.setItemText(10, _translate("MainWindow", "CX"))
        self.opt1.setItemText(11, _translate("MainWindow", "DX"))

        self.dest.setItemText(0, _translate("MainWindow", "AH"))
        self.dest.setItemText(1, _translate("MainWindow", "AL"))
        self.dest.setItemText(2, _translate("MainWindow", "BH"))
        self.dest.setItemText(3, _translate("MainWindow", "BL"))
        self.dest.setItemText(4, _translate("MainWindow", "CH"))
        self.dest.setItemText(5, _translate("MainWindow", "CL"))
        self.dest.setItemText(6, _translate("MainWindow", "DH"))
        self.dest.setItemText(7, _translate("MainWindow", "DL"))
        self.dest.setItemText(8, _translate("MainWindow", "AX"))
        self.dest.setItemText(9, _translate("MainWindow", "BX"))
        self.dest.setItemText(10, _translate("MainWindow", "CX"))
        self.dest.setItemText(11, _translate("MainWindow", "DX"))
        self.Add.setText(_translate("MainWindow", "Add"))
        self.instr.setItemText(0, _translate("MainWindow", "MOV"))
        self.instr.setItemText(1, _translate("MainWindow", "ADD"))
        self.instr.setItemText(2, _translate("MainWindow", "SUB"))
        self.opt2.setText(_translate("MainWindow", "0"))
        self.Decimal2.setText(_translate("MainWindow", "<html><head/><body><p>Decimal</p><p><br/></p></body></html>"))
        self.restAL.setText(_translate("MainWindow", "Reset"))
        self.dec["AL"].setText(_translate("MainWindow", "0"))
        self.restBH.setText(_translate("MainWindow", "Reset"))
        self.dec["BH"].setText(_translate("MainWindow", "0"))
        self.restBL.setText(_translate("MainWindow", "Reset"))
        self.dec["BL"].setText(_translate("MainWindow", "0"))
        self.restCH.setText(_translate("MainWindow", "Reset"))
        self.dec["CH"].setText(_translate("MainWindow", "0"))
        self.restCL.setText(_translate("MainWindow", "Reset"))
        self.dec["CL"].setText(_translate("MainWindow", "0"))
        self.restDH.setText(_translate("MainWindow", "Reset"))
        self.dec["DH"].setText(_translate("MainWindow", "0"))
        self.restDL.setText(_translate("MainWindow", "Reset"))
        self.dec["DL"].setText(_translate("MainWindow", "0"))
        self.dec["AX"].setText(_translate("MainWindow", "0"))
        self.dec["BX"].setText(_translate("MainWindow", "0"))
        self.dec["CX"].setText(_translate("MainWindow", "0"))
        self.dec["DX"].setText(_translate("MainWindow", "0"))
        self.Decimal1.setText(_translate("MainWindow", "<html><head/><body><p>Decimal</p><p><br/></p></body></html>"))
        self.label.setText(_translate("MainWindow", ":"))
        self.TimeLabel.setText(_translate("MainWindow", "<html><head/><body><p>Time<br/></p></body></html>"))
        self.Date.setText(_translate("MainWindow", "2021-03-27"))
        self.Info.setText(_translate("MainWindow", "<html><head/><body><p>Info:</p><p><br/></p></body></html>"))
        self.Msg.setText(_translate("MainWindow", "<html><head/><body><p>-</p><p><br/></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.setWindowTitle('Processor Simulator')
    MainWindow.show()
    sys.exit(app.exec_())