import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import random
import time

class Test1(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.timer = None
        self.start_time = None
        self.audio_played = False
        self.big_button_visible = False


    def startGame(self, test_approach=False):
        self.test_approach = test_approach
        self.main_window.clearLayout()

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_countdown()

    def start_countdown(self):
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
        delay = random.randint(1000, 5000)
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
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, self.startGame)
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

    def startGame(self, test_approach=False):
        self.test_approach = test_approach

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.start_countdown()

    def start_countdown(self):
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
        delay = random.randint(1000, 5000)
        QTimer.singleShot(delay, self.change_background_color_and_start_timer)

    def change_background_color_and_start_timer(self):
        self.background_color = 'red'
        self.setStyleSheet(f"background-color: {self.background_color};")
        self.color_changed = True
        self.start_time = time.time()
        self.timer.start()

    def stop_timer(self):
        if self.color_changed:
            elapsed_time = self.timer.elapsed()
            if self.test_approach:
                self.main_window.showTestResult(elapsed_time, self.startGame)
            else:
                self.main_window.showTestResult(elapsed_time)


class Test3(QGraphicsScene):
    pass

class Test4(QGraphicsScene):
    pass

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.test_id = None
        self.test_games = ["T1", "T2", "T3", "T4"]
        self.test_names = ["BODZIEC AUDIO", "BODZIEC VIDEO", "WPISYWANIE ZNAKÓW", "CIĄG RYTMICZNY"]
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
        menu_label = QLabel("CZAS REAKCJI\nMENU")
        menu_label.setFont(QFont("Arial", 30))
        menu_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(menu_label)

        buttons_layout = QVBoxLayout()

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        buttons_layout.addWidget(spacer)

        # Buttons
        test_dsc = ["Opis1\nTutaj zaraz będzie to i to\n tekst dolny", "opis testu 2", "opis testu 3\ntekst dolny", "opis tekstu 4"]
        for i in range(1, 5):
            button = QPushButton(f"{self.test_names[i-1]}")
            button.setFont(QFont('Arial', 30))
            button.clicked.connect(self.showTestScreen(self.test_names[i-1], test_dsc[i-1]))
            buttons_layout.addWidget(button)

        # Spacer
        buttons_layout.addWidget(spacer)

        # Exit button
        exit_button = QPushButton("EXIT")
        exit_button.setFont(QFont('Arial', 30))
        exit_button.clicked.connect(self.close_application)
        buttons_layout.addWidget(exit_button)

        main_layout.addLayout(buttons_layout)

    # Shows the chosen test with description
    def showTestScreen(self, test_name, test_dsc):
        def wrapped():
            self.clearLayout()
            self.test_id = self.test_names.index(test_name)

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
            next_button.clicked.connect(getattr(self, self.test_games[self.test_id]))
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
        result_label = QLabel(f"Reaction time: {reaction_time} ms")
        result_label.setFont(QFont('Arial', 30))
        result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(result_label)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

        if retry_callback:
            # Real attempt button
            real_attempt_button = QPushButton("REAL ATTEMPT")
            real_attempt_button.setFont(QFont('Arial', 30))
            real_attempt_button.clicked.connect(retry_callback)
            layout.addWidget(real_attempt_button, alignment=Qt.AlignCenter)

        # Back to menu button
        menu_button = QPushButton("MENU")
        menu_button.setFont(QFont('Arial', 30))
        menu_button.clicked.connect(self.showMenu)
        layout.addWidget(menu_button, alignment=Qt.AlignCenter)

        # Spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(spacer)

    def T1(self):
        self.clearLayout()

        minigame = Test1(self)
        minigame.startGame(True)

        self.setCentralWidget(minigame)

    def T2(self):
        self.clearLayout()

        minigame = Test2(self)
        minigame.startGame(True)

        self.setCentralWidget(minigame)

    def T3(self):
        pass

    def T4(self):
        pass

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
