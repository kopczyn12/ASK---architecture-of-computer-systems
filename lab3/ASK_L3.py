import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import random
import time

min_delay = 1000
max_delay = 3000

class Test1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.timer = None
        self.start_time = None
        self.audio_played = False
        self.big_button_visible = False

    def startGame(self, test_approach=True):
        self.test_approach = test_approach
        self.main_window.clearLayout()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_countdown()

    def start_countdown(self):
        # Spacer
        spacer_top = QWidget()
        spacer_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(spacer_top)

        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont('Arial', 50))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.countdown_label)

        # Spacer
        spacer_bottom = QWidget()
        spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(spacer_bottom)

        QTimer.singleShot(0, lambda: self.update_countdown(3))

    def update_countdown(self, count):
        if count > 0:
            self.countdown_label.setText(str(count))
            QTimer.singleShot(1000, lambda: self.update_countdown(count - 1))
        else:
            self.layout().removeWidget(self.countdown_label)  # Usuń countdown_label z layoutu
            self.countdown_label.deleteLater()  # Usuń obiekt countdown_label
            self.start_reaction_test()

    def start_reaction_test(self):
        if not self.big_button_visible:
            self.big_button_visible = True
            self.big_button = QPushButton("PRESS!")
            self.big_button.setFont(QFont('Arial', 100))
            self.big_button.clicked.connect(self.stop_timer)
            self.layout().addWidget(self.big_button, alignment=Qt.AlignCenter)
            # Spacer
            spacer_bottom = QWidget()
            spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout().addWidget(spacer_bottom)

        self.timer = QElapsedTimer()
        delay = random.randint(min_delay, max_delay)
        QTimer.singleShot(delay, self.play_audio_and_start_timer)

    def play_audio_and_start_timer(self):
        # Create a QMediaPlayer instance
        self.player = QMediaPlayer()

        # Set the media source (audio file) and play it
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("beep.wav")))
        self.player.play()

        self.audio_played = True
        self.start_time = time.time()
        self.timer.start()

    def stop_timer(self):
        if self.audio_played:
            elapsed_time = self.timer.elapsed()
            self.player.stop()
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, 1)
            else:
                self.main_window.showTestResult(elapsed_time)

class Test2(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.timer = None
        self.start_time = None
        self.big_button_visible = False
        self.background_color = 'white'
        self.color_changed = False

    def startGame(self, test_approach):
        self.test_approach = test_approach

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_countdown()

    def start_countdown(self):
        # Spacer
        spacer_top = QWidget()
        spacer_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(spacer_top)

        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont('Arial', 50))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.countdown_label)

        # Spacer
        spacer_bottom = QWidget()
        spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(spacer_bottom)

        QTimer.singleShot(0, lambda: self.update_countdown(3))

    def update_countdown(self, count):
        if count > 0:
            self.countdown_label.setText(str(count))
            QTimer.singleShot(1000, lambda: self.update_countdown(count - 1))
        else:
            self.layout().removeWidget(self.countdown_label)  # Usuń countdown_label z layoutu
            self.countdown_label.deleteLater()  # Usuń obiekt countdown_label
            self.start_reaction_test()

    def start_reaction_test(self):
        if not self.big_button_visible:
            self.big_button_visible = True
            self.big_button = QPushButton("PRESS!")
            self.big_button.setFont(QFont('Arial', 100))
            self.big_button.clicked.connect(self.stop_timer)
            self.layout().addWidget(self.big_button, alignment=Qt.AlignCenter)
            # Spacer
            spacer_bottom = QWidget()
            spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.layout().addWidget(spacer_bottom)

        self.timer = QElapsedTimer()
        delay = random.randint(min_delay, max_delay)
        QTimer.singleShot(delay, self.change_background_color_and_start_timer)

    def change_background_color_and_start_timer(self):
        self.big_button.setStyleSheet("background-color : red")
        self.color_changed = True
        self.start_time = time.time()
        self.timer.start()

    def stop_timer(self):
        if self.color_changed:
            elapsed_time = self.timer.elapsed()
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, 2)
            else:
                self.main_window.showTestResult(elapsed_time)

class Test3(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.timer = None
        self.start_time = None
        self.big_button_visible = False
        self.color_changed = False
        self.matched = False

    def startGame(self, test_approach):
        self.test_approach = test_approach

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_countdown()

    def start_countdown(self):
        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont('Arial', 50))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.countdown_label)

        QTimer.singleShot(0, lambda: self.update_countdown(3))

    def update_countdown(self, count):
        if count > 0:
            self.countdown_label.setText(str(count))
            QTimer.singleShot(1000, lambda: self.update_countdown(count - 1))
        else:
            self.layout().removeWidget(self.countdown_label)
            self.countdown_label.deleteLater()
            self.start_color_label_and_button()

    def start_color_label_and_button(self):
        self.color_label = QLabel(" ")
        self.color_label.setFont(QFont('Arial', 50))
        self.color_label.setAlignment(Qt.AlignCenter)
        self.layout().addWidget(self.color_label)

        self.big_button = QPushButton("PRESS!")
        self.big_button.setFont(QFont('Arial', 100))
        self.layout().addWidget(self.big_button, alignment=Qt.AlignCenter)

        QTimer.singleShot(1500, self.show_mismatched_label)

    def show_mismatched_label(self):
        colors = ['red', 'blue', 'green', 'yellow']
        color_name = random.choice(colors)
        color_value = random.choice([c for c in colors if c != color_name])

        if color_name == 'red':
            self.color_label.setText('CZERWONY')
        elif color_name == 'blue':
            self.color_label.setText('NIEBIESKI')
        elif color_name == 'green':
            self.color_label.setText('ZIELONY')
        elif color_name == 'yellow':
            self.color_label.setText('ŻÓŁTY')

        self.color_label.setStyleSheet(f"color : {color_value};")

        QTimer.singleShot(1500, self.show_random_label)

    def show_random_label(self):
        colors = ['red', 'blue', 'green', 'yellow']
        color_name = random.choice(colors)
        color_value = random.choice(colors)

        if color_name == 'red':
            self.color_label.setText('CZERWONY')
        elif color_name == 'blue':
            self.color_label.setText('NIEBIESKI')
        elif color_name == 'green':
            self.color_label.setText('ZIELONY')
        elif color_name == 'yellow':
            self.color_label.setText('ŻÓŁTY')


        self.color_label.setStyleSheet(f"color : {color_value};")

        if color_name == color_value:
            self.start_timer_and_enable_button()
        else:
            QTimer.singleShot(1500, self.show_random_label)

    def start_timer_and_enable_button(self):
        self.matched = True
        self.big_button.clicked.connect(self.stop_timer)
        self.timer = QElapsedTimer()
        self.timer.start()

    def stop_timer(self):
        elapsed_time = self.timer.elapsed()
        if self.matched:
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, 3)
            else:
                self.main_window.showTestResult(elapsed_time)

class Test4(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.timer = None
        self.start_time = None
        self.pulse_count = 0
        self.timer_stopped = False

    def startGame(self, test_approach):
        self.test_approach = test_approach

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.big_button = QPushButton("PRESS!")
        self.big_button.setFont(QFont('Arial', 100))
        self.layout().addWidget(self.big_button, alignment=Qt.AlignCenter)

        # Spacer
        spacer_bottom = QWidget()
        spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().addWidget(spacer_bottom)

        self.start_countdown()

    def start_countdown(self):
        # Spacer
        spacer_top = QWidget()
        spacer_top.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().insertWidget(0, spacer_top)

        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont('Arial', 50))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.layout().insertWidget(1, self.countdown_label)

        # Spacer
        spacer_bottom = QWidget()
        spacer_bottom.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout().insertWidget(2, spacer_bottom)

        self.start_time = time.time()
        self.timer = QElapsedTimer()
        self.timer.start()

        QTimer.singleShot(0, lambda: self.update_countdown(3))

    def update_countdown(self, count):
        if count > 0:
            self.countdown_label.setText(str(count))
            QTimer.singleShot(1000, lambda: self.update_countdown(count - 1))
        else:
            self.layout().removeWidget(self.countdown_label)
            self.countdown_label.deleteLater()
            QTimer.singleShot(1000, self.pulse_button)  # Start pulsing after the countdown

    def pulse_button(self):
        if self.pulse_count < 2 and not self.timer_stopped:
            self.big_button.setStyleSheet("background-color : red")
            QTimer.singleShot(50, lambda: self.set_button_white())
        elif self.pulse_count == 2 and not self.timer_stopped:
            self.big_button.setStyleSheet("background-color : red")
            QTimer.singleShot(50, lambda: self.set_button_white(True))
        else:
            QTimer.singleShot(50, lambda: self.set_button_white())

    def set_button_white(self, enable_button=False):
        self.big_button.setStyleSheet("background-color : white")
        self.pulse_count += 1
        if enable_button:
            self.big_button.clicked.connect(self.stop_timer)
        QTimer.singleShot(950, self.pulse_button)

    def stop_timer(self):
        if self.timer is not None:
            self.timer_stopped = True
            elapsed_time = self.timer.elapsed() - 7000
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, 4)
            else:
                self.main_window.showTestResult(elapsed_time)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.test_id = None
        self.test_names = ["REAKCJA AUDIO", "REAKCJA VIDEO", "DOPASOWANIE KOLOR-TEKST", "CIĄG RYTMICZNY"] # Minigames names
        self.test_approach = None
        self.reactions = ['', '', '', '']
        self.minigame = None
        self.showFullScreen()
        self.showMenu()

    def showMenu(self):
        self.clearLayout()
        self.test_id = None

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(100, 100, 100, 100)
        central_widget.setLayout(main_layout)

        # Menu label
        menu_label = QLabel("CZAS REAKCJI\nMENU\n")
        menu_label.setFont(QFont("Arial", 50))
        menu_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(menu_label)

        # Tests results
        results_label = QLabel("\n".join(
            [f"{name}: {result} ms" for name, result in zip(self.test_names, self.reactions) if result != '']))
        results_label.setFont(QFont("Arial", 30))
        results_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(results_label)

        buttons_layout = QVBoxLayout()

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        buttons_layout.addWidget(spacer)

        # Buttons
        test_dsc = ["\nTest mierzy szybkość reakcji na bodźce słuchowe."
                    "\nPrzed rozpoczęciem testu odbędzie się odliczanie."
                    "\nWynik testu próbnego nie jest zapisywany"
                    "\nWciśnij przycisk START aby rozpocząć."
                    "\n\nUżytkownik będzie miał za zadanie jak najszybsze wciśnięcie przycisku"
                    "\nPRESS po usłyszeniu sygnału dźwiękowego.",

                    "\nTest mierzy szybkość reakcji na bodźce wzrokowe."
                    "\nPrzed rozpoczęciem testu odbędzie się odliczanie."
                    "\nWynik testu próbnego nie jest zapisywany"
                    "\nWciśnij przycisk START aby rozpocząć."
                    "\n\nUżytkownik będzie miał za zadanie jak najszybsze wciśnięcie przycisku"
                    "\nPRESS po zmianie jego koloru na czerwony.",

                    "\nTest mierzy szybkość reakcji na zmiany wizualne"
                    "\nPrzed rozpoczęciem testu odbędzie się odliczanie."
                    "\nWynik testu próbnego nie jest zapisywany"
                    "\nWciśnij przycisk START aby rozpocząć."
                    "\n\nUżytkownik będzie miał za zadanie jak najszybsze wciśnięcie przycisku"
                    "\nPRESS gdy kolor tekstu pokryje się z wyświetlaną nazwą.",

                    "\nTest mierzy zdolność użytkownika do wyczucia rytmu"
                    "\nPrzed rozpoczęciem testu odbędzie się odliczanie."
                    "\nWynik testu próbnego nie jest zapisywany"
                    "\nWciśnij przycisk START aby rozpocząć."
                    "\n\nUżytkownik będzie miał za zadanie dokończyć ciąg "
                    "\nrytmiczny wyznaczony przez 3 czerwone mignięcia guzika PRESS"
                    "\n(trzeba kliknąć PRESS w momencie gdy guzik miałby znów zmienić kolor)."]

        for i in range(1, 5):
            button = QPushButton(f"{self.test_names[i-1]}")
            button.setFont(QFont('Arial', 30))
            button.clicked.connect(self.showTestScreen(self.test_names[i-1], test_dsc[i-1]))
            buttons_layout.addWidget(button)

        # Spacer
        buttons_layout.addWidget(spacer)

        # Exit button
        exit_button = QPushButton("WYJŚCIE")
        exit_button.setFont(QFont('Arial', 30))
        exit_button.clicked.connect(self.close_application)
        buttons_layout.addWidget(exit_button)

        main_layout.addLayout(buttons_layout)

    # Shows the chosen test with description
    def showTestScreen(self, test_name, test_dsc):
        def wrapped():
            self.clearLayout()
            self.test_id = self.test_names.index(test_name)
            self.test_approach = True

            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout()
            central_widget.setLayout(layout)

            # Spacer
            spacer1 = QWidget()
            spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(spacer1)

            # Test name
            test_label = QLabel(test_name)
            test_label.setFont(QFont('Arial', 30))
            test_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(test_label)

            # Test description
            dsc_label = QLabel(test_dsc)
            dsc_label.setFont(QFont('Arial', 30))
            dsc_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(dsc_label)

            # Spacer
            spacer2 = QWidget()
            spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(spacer2)

            # Moving on to the test attempt
            next_button = QPushButton("START")
            next_button.setFont(QFont('Arial', 30))
            next_button.clicked.connect(self.runTest)
            layout.addWidget(next_button, alignment=Qt.AlignCenter)

            # Back to menu button
            menu_button = QPushButton("MENU")
            menu_button.setFont(QFont('Arial', 30))
            menu_button.clicked.connect(self.showMenu)
            layout.addWidget(menu_button, alignment=Qt.AlignCenter)

            # Spacer
            spacer3 = QWidget()
            spacer3.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(spacer3)


        return wrapped

    def showTestResult(self, reaction_time, retry_callback=None):
        self.clearLayout()
        self.test_approach = False


        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Test name
        test_label = QLabel(self.test_names[self.test_id])
        test_label.setFont(QFont('Arial', 30))
        test_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(test_label)

        # Test result
        result_label = QLabel(f"Czas reakcji: {reaction_time} ms")
        result_label.setFont(QFont('Arial', 30))
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        if retry_callback:
            # Real attempt button
            self.test_id = retry_callback - 1
            real_attempt_button = QPushButton("PRAWDZIWY TEST")
            real_attempt_button.setFont(QFont('Arial', 30))
            real_attempt_button.clicked.connect(self.runTest)
            layout.addWidget(real_attempt_button, alignment=Qt.AlignCenter)
        else:
            # Repeat button
            self.reactions[self.test_id] = reaction_time
            repeat_button = QPushButton("POWTÓRZ TEST")
            repeat_button.setFont(QFont('Arial', 30))
            repeat_button.clicked.connect(self.runTest)
            layout.addWidget(repeat_button, alignment=Qt.AlignCenter)

        # Back to menu button
        menu_button = QPushButton("MENU")
        menu_button.setFont(QFont('Arial', 30))
        menu_button.clicked.connect(self.showMenu)
        layout.addWidget(menu_button, alignment=Qt.AlignCenter)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

    def runTest(self):
        self.clearLayout()

        tests = []
        test1, test2, test3, test4 = Test1(self), Test2(self), Test3(self), Test4(self)
        tests.append(test1)
        tests.append(test2)
        tests.append(test3)
        tests.append(test4)

        self.minigame = tests[self.test_id]

        if self.test_approach:
            self.minigame.startGame(True)
        else:
            self.minigame.startGame(False)

        self.setCentralWidget(self.minigame)

    def clearLayout(self):
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.deleteLater()

    def close_application(self):
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
