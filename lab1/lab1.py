import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QLineEdit, QVBoxLayout, QGridLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen, QBrush, QFont
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QRectF

class DigitalClock(QLabel):
    """Digital Clock class"""
    def __init__(self):
        super().__init__()
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)
        self.update()

    def update(self):
        """Update the time"""
        time = QTime.currentTime()
        text = time.toString('hh:mm:ss')
        self.setText(text)

class AnalogClock(QWidget):
    def __init__(self):
        super().__init__()
        timer = QTimer(self)
        timer.timeout.connect(self.update)
        timer.start(1000)

    def paintEvent(self, event):
        """Painting the event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        rect = QRectF(0, 0, self.width(), self.height())
        painter.setViewport(rect.toRect())
        painter.setWindow(rect.toRect())
        self.drawClock(painter)

    def drawClock(self, painter):
        """Drawing the clock"""
        side = min(self.width(), self.height())
        painter.scale(side / 200.0, side / 200.0)
        painter.translate(100, 100)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.black))

        for i in range(12):
            painter.save()
            painter.rotate(30 * i)
            painter.drawRect(70, -2, 10, 4)
            painter.restore()

        for i in range(60):
            if i % 5 != 0:
                painter.save()
                painter.rotate(6 * i)
                painter.drawRect(82, -1, 4, 2)
                painter.restore()

        time = QTime.currentTime()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(Qt.black))

        painter.save()
        painter.rotate(30 * (time.hour() + time.minute() / 60.0))
        painter.drawRect(-4, -60, 8, 60)
        painter.restore()

        painter.save()
        painter.rotate(6 * (time.minute() + time.second() / 60.0))
        painter.drawRect(-3, -80, 6, 80)
        painter.restore()

        painter.setPen(QPen(Qt.black, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPoint(0, 0), 95, 95)

class Calculator(QMainWindow):
    """The calculator class"""
    def __init__(self):
        super().__init__()
        self.light_theme = True
        self.initUI()
        self.set_light_theme()
        
    def initUI(self):
        """Init UI of the window"""
        self.setWindowTitle('Calculator')
        self.setFixedSize(500, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #result box
        self.result_box = QLineEdit(self)
        self.result_box.setReadOnly(False)
        self.result_box.setAlignment(Qt.AlignRight)
        self.result_box.setMaxLength(15)
        self.result_box.keyPressEvent = self.new_keyPressEvent

        #main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.result_box)

        grid = QGridLayout()
        main_layout.addLayout(grid)

        #list of the buttons
        buttons = [
            ('7', self.add_digit),
            ('8', self.add_digit),
            ('9', self.add_digit),
            ('/', self.add_operator),
            ('4', self.add_digit),
            ('5', self.add_digit),
            ('6', self.add_digit),
            ('*', self.add_operator),
            ('1', self.add_digit),
            ('2', self.add_digit),
            ('3', self.add_digit),
            ('-', self.add_operator),
            ('0', self.add_digit),
            ('.', self.add_digit),
            ('=', self.calculate),
            ('+', self.add_operator),
        ]

        # here we are simply making a 'matrix' of these buttons
        row = 0
        col = 0

        for button_text, button_handler in buttons:
            button = QPushButton(button_text)
            button.clicked.connect(button_handler)
            grid.addWidget(button, row, col)

            col += 1
            if col == 4:
                col = 0
                row += 1

        #switch theme button
        self.theme_button = QPushButton('Switch Theme', self)
        self.theme_button.clicked.connect(self.switch_theme)
        main_layout.addWidget(self.theme_button)

        central_widget.setLayout(main_layout)

        self.light_theme = True
        self.set_light_theme()

        self.clock = AnalogClock()
        self.digital_clock = DigitalClock()
        self.digital_clock.hide()

        def switch_clock():
            """Switching the clock"""
            nonlocal self
            if self.clock.isVisible():
                self.clock.hide()
                self.digital_clock.show()
            else:
                self.clock.show()
                self.digital_clock.hide()

        self.clock_button = QPushButton('Switch Clock', self)
        self.clock_button.clicked.connect(switch_clock)
        main_layout.addWidget(self.clock)
        main_layout.addWidget(self.digital_clock)
        main_layout.addWidget(self.clock_button)

        central_widget.setLayout(main_layout)

        self.light_theme = True
        self.set_light_theme()        

    #communication by keyboard with the result box
    def new_keyPressEvent(self, event):
        """Event handling by the keyboard"""
        key = event.key()
        if key == Qt.Key_Enter or key == Qt.Key_Return:
            self.calculate()
        else:
            QLineEdit.keyPressEvent(self.result_box, event)

    def add_digit(self):
        """Adding digit to the result box"""
        digit = self.sender().text()
        current_text = self.result_box.text()

        if len(current_text) == 0 and digit == '0':
            return

        self.result_box.setText(current_text + digit)

    def add_operator(self):
        """Adding operator to the result box"""
        operator = self.sender().text()
        current_text = self.result_box.text()

        if len(current_text) == 0 or current_text[-1] in '+-*/':
            return

        self.result_box.setText(current_text + operator)

    def calculate(self):
        """Calculation of the formula"""
        try:
            result = eval(self.result_box.text())
            self.result_box.setText(str(result))
        except ZeroDivisionError:
            self.result_box.setText('Error! Division by zero')
        except Exception as e:
            self.result_box.setText('Error')

    def switch_theme(self):
        """Switching the theme between light and dark"""
        self.light_theme = not self.light_theme

        if self.light_theme:
            self.set_light_theme()
        else:
            self.set_dark_theme()

    def set_light_theme(self):
        """Setting light theme"""
        light_palette = QPalette()
        light_palette.setColor(QPalette.Window, QColor(255, 255, 255))
        light_palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Base, QColor(255, 255, 255))
        light_palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
        light_palette.setColor(QPalette.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Button, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.Link, QColor(0, 0, 255))
        light_palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        light_palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(light_palette)

    def set_dark_theme(self):
        """Setting dark theme"""
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        self.setPalette(dark_palette)

def main():
    """main function"""
    app = QApplication(sys.argv)
    calculator = Calculator()
    calculator.show()
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
