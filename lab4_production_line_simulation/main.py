import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QPushButton, QLabel, QGridLayout, QWidget, QDialog, QProgressBar, QLineEdit
from PyQt5.QtCore import QTimer, QCoreApplication, QDateTime
from PyQt5.QtGui import QFont
import random
import psutil

class LoginWindow(QDialog):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setWindowTitle('Login')
        self.setGeometry(50, 50, 400, 200)
        self.setFont(QFont('Arial', 12))

        self.layout = QGridLayout()

        self.username_input = QLineEdit()
        self.layout.addWidget(QLabel('Username:'), 0, 0)
        self.layout.addWidget(self.username_input, 0, 1)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.layout.addWidget(QLabel('Password:'), 1, 0)
        self.layout.addWidget(self.password_input, 1, 1)

        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button, 2, 1)

        self.setLayout(self.layout)
        

    def login(self):
        self.main_window.login(self.username_input.text())
        self.close()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Production Line Dispatcher')
        self.setGeometry(50, 50, 400, 200)
        self.setFont(QFont('Arial', 12))
        self.popup_shown = False
        self.presence_popup_shown = False

        self.layout = QGridLayout()
        self.layout.setSpacing(10)

        self.info_label = QLabel('Warning! Temperature above 90 degrees is dangerous!')
        self.layout.addWidget(self.info_label, 0, 0, 1, 2)

        self.temperature_label = QLabel('Temperature: ')
        self.layout.addWidget(self.temperature_label, 1, 0)

        self.temperature_bar = QProgressBar()
        self.temperature_bar.setMinimum(0)
        self.temperature_bar.setMaximum(150)
        self.layout.addWidget(self.temperature_bar, 1, 1)

        self.user_label = QLabel('Not logged in')
        self.layout.addWidget(self.user_label, 2, 0, 1, 2)

        self.fan_button = QPushButton('Cool down')
        self.fan_button.clicked.connect(self.open_fans)
        self.layout.addWidget(self.fan_button, 3, 0, 1, 2)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.layout)
        self.setCentralWidget(self.central_widget)

        self.logged_in = False
        self.presence_confirmed = False
        self.temperature = 70

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(2000)

        self.warning_dialog_timer = QTimer()
        self.warning_dialog_timer.setSingleShot(True)
        self.warning_dialog_timer.timeout.connect(self.close_warning_dialog)

        self.presence_timer = QTimer()
        self.presence_timer.setSingleShot(True)
        self.presence_timer.timeout.connect(self.logout_and_exit)

        self.warning_dialog = None
        self.presence_popup = None
        self.cpu_label = QLabel('CPU Utilization: ')
        self.layout.addWidget(self.cpu_label, 4, 0)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMinimum(0)
        self.cpu_bar.setMaximum(100)
        self.layout.addWidget(self.cpu_bar, 4, 1)

        self.cpu_popup_shown = False
        self.cpu_presence_popup_shown = False
        self.cpu_warning_dialog = None
        self.cpu_presence_popup = None
        self.cpu_warning_dialog_timer = QTimer()
        self.cpu_warning_dialog_timer.setSingleShot(True)
        self.cpu_warning_dialog_timer.timeout.connect(self.close_cpu_warning_dialog)
        self.cpu_presence_timer = QTimer()
        self.cpu_presence_timer.setSingleShot(True)
        self.cpu_presence_timer.timeout.connect(self.logout_and_exit)

        login_win = LoginWindow(self)
        login_win.exec_()


    def update(self):
        if not self.logged_in:
            return

        self.temperature += random.randint(-5, 10)
        self.temperature_label.setText(f'Temperature: {self.temperature} °C')
        self.temperature_bar.setValue(self.temperature)

        cpu_utilization = psutil.cpu_percent()
        self.cpu_label.setText(f'CPU Utilization: {cpu_utilization} %')
        self.cpu_bar.setValue(cpu_utilization)

        if cpu_utilization > 70 and not self.cpu_popup_shown:
            self.cpu_popup_shown = True
            self.cpu_warning_dialog = QMessageBox(self)
            self.cpu_warning_dialog.setWindowTitle('CPU utilization warning')
            self.cpu_warning_dialog.setIcon(QMessageBox.Warning)
            self.cpu_warning_dialog.setText('The CPU utilization is too high. Cool down the system!')
            self.cpu_warning_dialog.show()
            self.cpu_warning_dialog_timer.start(5000)

        if cpu_utilization > 70 and not self.cpu_presence_popup_shown and not self.cpu_warning_dialog:
            self.cpu_presence_popup_shown = True
            self.cpu_presence_popup = QMessageBox(self)
            self.cpu_presence_popup.setWindowTitle('Confirmation')
            self.cpu_presence_popup.setText('The CPU utilization is still high. Are you here? Confirm presence by clicking "Yes".')
            self.cpu_presence_popup.setStandardButtons(QMessageBox.Yes)
            self.cpu_presence_popup.buttonClicked.connect(self.check_cpu_presence_confirmation)
            self.cpu_presence_popup.show()
            self.cpu_presence_timer.start(10000)

        if cpu_utilization <= 70:
            self.reset_cpu_flags()

        if self.temperature > 90 and not self.popup_shown:
            self.popup_shown = True
            self.warning_dialog = QMessageBox(self)
            self.warning_dialog.setWindowTitle('Temperature warning')
            self.warning_dialog.setIcon(QMessageBox.Warning)
            self.warning_dialog.setText('The temperature is too high. Cool down the production!')
            self.warning_dialog.show()
            self.warning_dialog_timer.start(5000)

        if self.temperature > 90 and not self.presence_popup_shown and not self.warning_dialog:
            self.presence_popup_shown = True
            self.presence_popup = QMessageBox(self)
            self.presence_popup.setWindowTitle('Confirmation')
            self.presence_popup.setText('The temperature is still high. Are you here? Confirm presence by clicking "Yes".')
            self.presence_popup.setStandardButtons(QMessageBox.Yes)
            self.presence_popup.buttonClicked.connect(self.check_presence_confirmation)
            self.presence_popup.show()
            self.presence_timer.start(10000)

        if self.temperature <= 90:
            self.reset_flags()

        if self.temperature > 90:
            self.temperature_bar.setStyleSheet("QProgressBar { background-color: red; } QProgressBar::chunk { background-color: red; }")
        else:
            self.temperature_bar.setStyleSheet("QProgressBar { background-color: green; } QProgressBar::chunk { background-color: green; }")


    def check_cpu_presence_confirmation(self):
        if self.cpu_presence_popup.clickedButton().text() == '&Yes':
            self.cpu_presence_confirmed = True
            self.cpu_presence_popup_shown = False
            self.cpu_presence_popup.close()
            self.cpu_presence_popup = None
        else:
            self.logout_and_exit()

    def close_cpu_warning_dialog(self):
        if self.cpu_warning_dialog is not None:
            self.cpu_warning_dialog.close()
            self.cpu_warning_dialog = None

    def reset_cpu_flags(self):
        self.cpu_popup_shown = False
        self.cpu_presence_popup_shown = False
        self.cpu_presence_confirmed = False

    def check_presence_confirmation(self):
        if self.presence_popup.clickedButton().text() == '&Yes':
            self.presence_confirmed = True
            self.presence_popup_shown = False
            self.presence_popup.close()
            self.presence_popup = None
        else:
            self.logout_and_exit()

    def close_warning_dialog(self):
        if self.warning_dialog is not None:
            self.warning_dialog.close()
            self.warning_dialog = None

    def login(self, username):
        self.logged_in = True
        self.user_label.setText(f'Logged in as {username} at {QDateTime.currentDateTime().toString("MM-dd-yyyy h:mm AP")}')

    def logout_and_exit(self):
        if not self.presence_confirmed and self.presence_popup_shown:
            self.logout()
            QCoreApplication.instance().quit()
            with open('log.txt', 'w') as f:
                f.write(self.message_absence)

    def logout(self):
        self.logged_in = False
        self.presence_confirmed = False
        self.user_label.setText('Not logged in')

    def reset_flags(self):
        self.popup_shown = False
        self.presence_popup_shown = False
        self.presence_confirmed = False

    def open_fans(self):
        if self.temperature > 90:
            self.temperature -= 50
            self.temperature_bar.setValue(self.temperature)
            self.temperature_bar.setStyleSheet("QProgressBar { background-color: green; } QProgressBar::chunk { background-color: green; }")
            self.reset_flags()

        if psutil.cpu_percent() > 70:
            # Here we can't directly reduce CPU utilization as it is not directly under our control
            self.reset_cpu_flags()


def main():
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
