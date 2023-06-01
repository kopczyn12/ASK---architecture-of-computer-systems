# Michał Kopczyński 184817
# Maksymilian Terebus 181595
# ACiR VI sem
# ASK L6 (szachy)
import sys
import copy
import sqlite3
import os
import ast
import resources
import json
import xml.etree.ElementTree as ET
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from server import main as server_main
import socket
import threading
import subprocess
import random
import re


class ChessAI:
    def __init__(self, board, board_pieces, turn):
        self.board = board
        self.board_pieces = board_pieces
        self.turn = turn
        self.start = None
        self.move = None
        self.randMove()

    def randMove(self):
        best_eval = None
        best_moves = []

        for row in range(8):
            for col in range(8):
                figure = self.board[row][col]
                if figure != '':
                    is_white = figure.islower()
                    if (is_white and self.turn == 1) or (not is_white and self.turn == -1):
                        self.board_pieces[row][col].highlightMoves(col, row)

                        for move in window.scene.highlighted:  # Skipping non movable pieces
                            if move == [] or move == [col, row]:
                                continue

                            evaluation = self.evalMove(move)
                            if best_eval is None or (self.turn == 1 and evaluation > best_eval) \
                                    or (self.turn == -1 and evaluation < best_eval):
                                best_eval = evaluation
                                best_moves = [([col, row], move)]  # New list with best moves
                            elif evaluation == best_eval:
                                best_moves.append(([col, row], move))  # Adding the move to the list

        # Random choice of best move (if there are many best moves)
        best_start, best_move = random.choice(best_moves)

        self.start = best_start
        self.move = best_move

        self.board_pieces[best_start[1]][best_start[0]].highlightMoves(best_start[0], best_start[1])
        window.scene.draw_board()


        # Waiting before making a move
        QTimer.singleShot(1000, lambda: self.makeMove())

    def makeMove(self):
        figure = self.board[self.start[1]][self.start[0]]
        self.board[self.start[1]][self.start[0]] = ''
        self.board[self.move[1]][self.move[0]] = figure
        window.scene.highlighted = [[]]
        window.scene.AIchoice = self.move
        window.scene.draw_board()

        # Waiting before ending the turn
        QTimer.singleShot(1000, window.clock.endTurn)

        return self.board

    def evalMove(self, move):
        piece_values = {
            'P': 1, 'p': -1,
            'N': 3, 'n': -3,
            'B': 3, 'b': -3,
            'R': 5, 'r': -5,
            'Q': 9, 'q': -9,
            'K': 100, 'k': -100
        }

        captured_piece = self.board[move[1]][move[0]]
        if captured_piece == '':
            return 0
        else:
            return piece_values[captured_piece]


class Client:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.sock.connect((self.ip, self.port))
        # print(f"Successfully connected to server at {self.ip}:{self.port}\n")

    def send_message(self, message=""):
        if message:
            self.sock.send(message.encode())

    def receive_message(self, message_received):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if not message:
                    break
                else:
                    message_received.emit(message)

            except:
                break

    def start(self):
        self.connect()

        send = threading.Thread(target=self.send_message)
        receive = threading.Thread(target=self.receive_message)

        receive.start()
        send.start()

        receive.join()
        send.join()

        self.sock.close()


class ClientThread(QThread):
    message_received = pyqtSignal(str)

    def __init__(self, client):
        QThread.__init__(self)
        self.client = client

    def run(self):
        self.client.connect()

        send = threading.Thread(target=self.client.send_message)
        receive = threading.Thread(target=self.client.receive_message, args=(self.message_received,))

        receive.start()
        send.start()

        receive.join()
        send.join()

        self.client.sock.close()



class ChessBoard(QGraphicsScene):
    def __init__(self, players):
        super().__init__()
        self.setSceneRect(-220, 0, 1200, 800)
        self.theme = [QColor(255, 255, 255), QColor(0, 0, 0), QBrush(Qt.lightGray)]
        self.setBackgroundBrush(self.theme[2])
        self.highlighted = [[]]
        self.AIchoice = []
        self.pieces_matrix = []
        self.piece_moved = False
        self.players = players
        # print("Game type: ", self.players)
        self.replay_timer = None
        self.replay_on = False
        self.turn_label = None
        self.w_king_checked = False
        self.b_king_checked = False

        # Getting starting theme from config
        try:
            with open("config.json", "r") as f:
                config = json.load(f)

                if config.get("theme_classic", False):
                    self.theme = [QColor(255, 255, 255), QColor(0, 0, 0), QBrush(Qt.lightGray)]
                elif config.get("theme_coffee", False):
                    self.theme = [QColor(185, 156, 107), QColor(87, 65, 47), QBrush(Qt.darkGray)]
                elif config.get("theme_aqua", False):
                    self.theme = [QColor(240, 255, 255), QColor(0, 0, 139), QBrush(Qt.darkCyan)]

        except FileNotFoundError:
            pass

        # Connecting to database to get the init turn and board state
        database = sqlite3.connect('game_history.db')
        cursor = database.cursor()

        # The most recent turn
        cursor.execute('SELECT * FROM game_states ORDER BY id DESC LIMIT 1')
        game_state = cursor.fetchone()

        self.turn = game_state[1]
        self.my_turn = game_state[1]
        self.current_figures = ast.literal_eval(game_state[2])  # From string back to matrix

        database.close()

        self.board_history = [copy.deepcopy(self.current_figures)]

        # Drawing board
        self.draw_board()

        # RMB-click menu
        self.context_menu = QMenu()
        self.theme1_action = QAction("Classic", self)
        self.theme2_action = QAction("Coffee", self)
        self.theme3_action = QAction("Aqua", self)
        self.context_menu.addAction(self.theme1_action)
        self.context_menu.addAction(self.theme2_action)
        self.context_menu.addAction(self.theme3_action)

        self.theme1_action.triggered.connect(lambda: self.changeTheme(QColor(255, 255, 255),
                                                                      QColor(0, 0, 0),
                                                                      QBrush(Qt.lightGray)))
        self.theme2_action.triggered.connect(lambda: self.changeTheme(QColor(185, 156, 107),
                                                                      QColor(87, 65, 47),
                                                                      QBrush(Qt.darkGray)))
        self.theme3_action.triggered.connect(lambda: self.changeTheme(QColor(240, 255, 255),
                                                                      QColor(0, 0, 139),
                                                                      QBrush(Qt.darkCyan)))

    def draw_board(self):
        self.clear()
        self.setBackgroundBrush(self.theme[2])
        self.pieces_matrix = []

        # Checking if castling happened
        self.handleCastling()

        # Checking if en passant happened
        self.handleEnPassant()

        # Drawing the board
        counter = None
        for row in range(8):
            pieces_row = []
            for col in range(8):
                x = col * 100
                y = row * 100

                # Creating white and black tiles
                if (row + col) % 2 == 0:
                    tile_color = self.theme[0]
                else:
                    tile_color = self.theme[1]
                tile = Tile(x, y, 100, tile_color)

                if [col, row] in self.highlighted:
                    tile.color = Qt.green
                if [col, row] == self.AIchoice:
                    tile.color = Qt.red

                self.addItem(tile)

                # Creating black and white pieces
                figure = self.current_figures[row][col]
                if figure != '':
                    piece = ChessPiece(x, y, 80, figure)
                    pieces_row.append(piece)
                    self.addItem(piece)
                else:
                    pieces_row.append(None)
            self.pieces_matrix.append(pieces_row)

            # Adding labels once every row changes
            if counter != row:
                counter = row
                # 1-8 labels
                value_label = QGraphicsTextItem(str(8 - row))
                value_label.setFont(QFont("Times New Roman", 30))
                value_label.setPos(-60, row * 100 + 10)
                self.addItem(value_label)
                # a-h labels
                letter_label = QGraphicsTextItem(chr(97 + row))
                letter_label.setFont(QFont("Times New Roman", 30))
                letter_label.setPos(row * 100 + 30, 810)
                self.addItem(letter_label)

        # Adding the label to show the turn
        turn_label = QGraphicsTextItem()
        if self.turn == 1 and self.w_king_checked:
            turn_label.setPlainText("WHITE TURN (CHECK)")
        elif self.turn == 1:
            turn_label.setPlainText("WHITE TURN")
        elif self.turn == -1 and self.b_king_checked:
            turn_label.setPlainText("BLACK TURN (CHECK)")
        elif self.turn == -1:
            turn_label.setPlainText("BLACK TURN")
        elif self.turn == 2:
            turn_label.setPlainText("WHITE LOST!")
        elif self.turn == -2:
            turn_label.setPlainText("BLACK LOST!")

        if self.turn == self.my_turn and self.players != 3:
            turn_label.setPlainText(turn_label.toPlainText() + " [YOU]")

        elif self.turn != self.my_turn and self.players != 2 and self.turn not in [-2, 2]:
            turn_label.setPlainText(turn_label.toPlainText() + " [AI]")
        elif self.players == 3 and self.turn not in [-2, 2]:
            turn_label.setPlainText(turn_label.toPlainText() + " [AI]")



        turn_label.setFont(QFont("Times New Roman", 30))
        turn_label.setPos(200, -100)
        self.addItem(turn_label)

    def replay(self):
        # If the timer is already running, do nothing
        if self.replay_timer and self.replay_timer.isActive():
            return

        # Resetting and stopping the clock
        self.replay_on = True
        window.clock.timer.stop()
        window.clock.time_start = QTime.currentTime()

        # Opening the database with game history
        database = sqlite3.connect('game_history.db')
        cursor = database.cursor()
        cursor.execute('SELECT * FROM game_states')
        game_states = cursor.fetchall()

        # Creating replay timer
        self.replay_timer = QTimer(self)
        self.replay_timer.timeout.connect(self.update_board)
        self.replay_timer.start(1000)

        # Iterating the game states
        self.game_states = iter(game_states)
        self.current_game_state = next(self.game_states, None)  # The first game state

        # Making player able to move a piece after replay
        self.piece_moved = False
        database.close()

        # Moving AI after replay
        if window.scene.players == 3 or (window.scene.players == 1 and window.scene.turn == -1):
            window.clock.chessBot()

    def update_board(self):
        # Stopping the timer when there are no more game states
        if self.current_game_state is None:
            self.replay_timer.stop()
            return

        # Replaying game history
        turn_id, turn, board, time_taken = self.current_game_state
        self.turn = turn
        self.current_figures = ast.literal_eval(board)
        self.highlighted = [[]]
        self.AIchoice = []
        self.draw_board()

        # Replay label
        replay_label = QGraphicsTextItem("REPLAY")
        replay_label.setFont(QFont("Times New Roman", 30))
        replay_label.setPos(200, -200)
        self.addItem(replay_label)

        # Getting the next game state
        self.current_game_state = next(self.game_states, None)

        # Making the game playable again
        if self.current_game_state is None:
            self.removeItem(replay_label)
            window.clock.timer.start(1)

        # After replay, resetting the clock
        window.clock.time_start = QTime.currentTime()
        self.replay_on = False

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.context_menu.exec(event.screenPos())

        super().mousePressEvent(event)

    def changeTheme(self, color1, color2, brush):
        self.theme = [color1, color2, brush]
        self.draw_board()

    def handleCastling(self):
        # Previous board state
        board = self.board_history[len(self.board_history) - 2]

        if board[7][4] == 'k' and self.current_figures[7][6] == 'k':  # White small castling
            self.current_figures[7][7] = ''
            self.current_figures[7][5] = 'r'
        elif board[7][4] == 'k' and self.current_figures[7][2] == 'k':  # White big castling
            self.current_figures[7][0] = ''
            self.current_figures[7][3] = 'r'
        elif board[0][4] == 'K' and self.current_figures[0][6] == 'K':  # Black small castling
            self.current_figures[0][7] = ''
            self.current_figures[0][5] = 'R'
        elif board[0][4] == 'K' and self.current_figures[0][2] == 'K':  # Black big castling
            self.current_figures[0][0] = ''
            self.current_figures[0][3] = 'R'

    def handleEnPassant(self):
        if len(self.board_history) < 3:
            return
        # Previous board states
        board_1 = self.board_history[len(self.board_history) - 3]  # 2 turns ago
        board_2 = self.board_history[len(self.board_history) - 2]  # 1 turn ago
        board_3 = self.current_figures  # present

        for col in range(8):
            # En passant for whites, upper part of board
            if board_1[1][col] == 'P' and board_2[3][col] == 'P' and board_3[2][col] == 'p':
                self.current_figures[3][col] = ''
            # En passant for blacks, upper part of board
            if board_1[6][col] == 'p' and board_2[4][col] == 'p' and board_3[5][col] == 'P':
                self.current_figures[4][col] = ''

    def pawnPromotion(self):
        def promote_pawn(row, piece):
            index = self.current_figures[row].index(piece)

            # Highlighting the promoted pawn
            window.scene.highlighted = [[index, row]]
            window.scene.draw_board()

            # A dialog with a choice
            dialog = PromotionDialog()
            if dialog.exec_() == QDialog.Accepted:
                promoted_figure = dialog.result
                if self.turn == 1:  # Whites turn
                    self.current_figures[row][index] = promoted_figure.lower()
                elif self.turn == -1:
                    self.current_figures[row][index] = promoted_figure.upper()

        if 'p' in self.current_figures[0]:
            promote_pawn(0, 'p')

        if 'P' in self.current_figures[7]:
            promote_pawn(7, 'P')


class PromotionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setFixedSize(200, 500)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.result = None

        vbox = QVBoxLayout()

        queen_icon = None
        knight_icon = None
        bishop_icon = None
        rook_icon = None

        # Choosing the right set of icons
        if window.scene.turn == 1:  # White figures
            queen_icon = QIcon(':/textures_128/q2.png')
            knight_icon = QIcon(':/textures_128/n2.png')
            bishop_icon = QIcon(':/textures_128/b2.png')
            rook_icon = QIcon(':/textures_128/r2.png')
        elif window.scene.turn == -1:  # Black figures
            queen_icon = QIcon(':/textures_128/Q.png')
            knight_icon = QIcon(':/textures_128/N.png')
            bishop_icon = QIcon(':/textures_128/B.png')
            rook_icon = QIcon(':/textures_128/R.png')

        queen_button = QPushButton()
        queen_button.setIcon(queen_icon)
        queen_button.setIconSize(QSize(100, 100))
        queen_button.clicked.connect(lambda: self.accept('q'))

        knight_button = QPushButton()
        knight_button.setIcon(knight_icon)
        knight_button.setIconSize(QSize(100, 100))
        knight_button.clicked.connect(lambda: self.accept('n'))

        bishop_button = QPushButton()
        bishop_button.setIcon(bishop_icon)
        bishop_button.setIconSize(QSize(100, 100))
        bishop_button.clicked.connect(lambda: self.accept('b'))

        rook_button = QPushButton()
        rook_button.setIcon(rook_icon)
        rook_button.setIconSize(QSize(100, 100))
        rook_button.clicked.connect(lambda: self.accept('r'))

        vbox.addWidget(queen_button)
        vbox.addWidget(knight_button)
        vbox.addWidget(bishop_button)
        vbox.addWidget(rook_button)

        self.setLayout(vbox)

    def accept(self, figure):
        self.result = figure
        super().accept()


class Tile(QGraphicsItem):
    def __init__(self, x, y, size, color):
        super().__init__()
        self.rect = QRectF(x, y, size, size)
        self.color = color
        self.highlighted = False

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.fillRect(self.rect, self.color)
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        painter.drawRect(self.rect)


class ChessPiece(QGraphicsItem):
    def __init__(self, x, y, size, figure):
        super().__init__()
        self.trueX = x + 50
        self.trueY = y + 50
        self.y = int(y / 100)
        self.x = int(x / 100)
        self.rect = QRectF(x + (100 - size) / 2, y + (100 - size) / 2, size, size)
        self.figure = figure
        self.setZValue(1)
        self.setAcceptHoverEvents(True)
        self.offset = self.rect.center()

        # Loading graphics from resources.py
        if figure.isupper():
            image_path = f":/textures_128/{figure}.png"
        elif figure.islower():
            image_path = f":/textures_128/{figure}2.png"
        else:
            raise ValueError(f'Invalid figure: {figure}')
        self.img = QImage(image_path)

        # Resizing image to fit the bounding rectangle
        self.img = self.img.scaled(int(self.rect.width()), int(self.rect.height()),
                                   Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget=None):
        painter.drawImage(self.rect, self.img)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not window.scene.piece_moved \
                and ((window.scene.turn == 1 and self.figure.islower())
                     or (window.scene.turn == -1 and self.figure.isupper()))\
                and not (window.scene.turn != window.scene.my_turn and window.scene.players == 2):
            self.setCursor(Qt.ClosedHandCursor)
            self.offset = self.rect.center()
            window.scene.highlighted = [[]]
            window.scene.AIchoice = []

    def mouseMoveEvent(self, event):
        if not window.scene.piece_moved and event.buttons() == Qt.LeftButton \
                and ((window.scene.turn == 1 and self.figure.islower())
                     or (window.scene.turn == -1 and self.figure.isupper()))\
                and not (window.scene.turn != window.scene.my_turn and window.scene.players == 2):
            self.setZValue(2)
            self.setPos(event.scenePos() - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.setZValue(1)

            # Real relative move
            x, y = self.pos().x(), self.pos().y()

            # Relative integer matrix move
            x = int((x - (x + 50) % 100 + 50) / 100)
            y = int((y - (y + 50) % 100 + 50) / 100)

            self.setPos(x * 100, y * 100)
            self.setCoordinates(x, y)

            window.scene.draw_board()

    def hoverEnterEvent(self, event):
        is_valid_piece = (window.scene.turn == 1 and self.figure.islower()) \
                         or (window.scene.turn == -1 and self.figure.isupper())

        if not window.scene.piece_moved and is_valid_piece:
            self.setCursor(Qt.OpenHandCursor)
        else:
            self.unsetCursor()

    def hoverLeaveEvent(self, event):
        self.unsetCursor()

    def printPosition(self):
        print(self.x, self.y)

    # Moving a piece to specific coordinates if possible, function returns True if move was valid and piece was set
    def setCoordinates(self, moveX, moveY, promotion=False):
        piece_set = False

        wantedX = int(self.x + moveX)
        wantedY = int(self.y + moveY)

        # Doing a highlight
        if wantedX == int(self.x) and wantedY == int(self.y):  # No moving, highlighting tiles
            self.highlightMoves(wantedX, wantedY, True)

        else:  # Moving, no visible highlight

            # Highlighting own possible moves
            self.highlightMoves(self.x, self.y, True)

            # Moving a piece if the move is valid
            if [wantedX, wantedY] in window.scene.highlighted:
                if window.scene.piece_moved:
                    return
                piece_set = True
                window.scene.piece_moved = True

                # Empty current field
                window.scene.current_figures[int(self.y)][int(self.x)] = ''

                self.x += moveX
                self.y += moveY

                # Place a figure in its destination field
                window.scene.current_figures[int(self.y)][int(self.x)] = self.figure

                # Promoting pawns if possible
                if not promotion:
                    window.scene.pawnPromotion()

                # Saving current board to the history before the turn ends
                # (a deep copy to get the matrix, not the whole object)
                window.scene.board_history.append(copy.deepcopy(window.scene.current_figures))

            window.scene.highlighted = [[]]
            window.scene.AIchoice = []

        # Returns true if a piece was successfully set
        return piece_set

    # Checking if a move is valid (for destination field)
    def checkMove(self, wantedX, wantedY, board=None):
        # 0 - invalid move (out of board or attacking won pieces)
        # 1 - attacking
        # 2 - empty space

        if board == None:
            board = window.scene.current_figures

        # Checking bounds of the board
        if wantedX < 0 or wantedX > 7 or wantedY < 0 or wantedY > 7:
            return 0  # invalid move

        # Logic values
        upper1 = board[int(self.y)][int(self.x)].isupper()
        upper2 = board[wantedY][wantedX].isupper()
        lower1 = board[int(self.y)][int(self.x)].islower()
        lower2 = board[wantedY][wantedX].islower()

        # Go back to your old position, don't attack yourself
        if upper1 and upper2 or lower1 and lower2:
            return 0  # invalid move
        # Go there if empty space or opponent
        elif board[wantedY][wantedX] != '':
            return 1  # attack move
        else:
            return 2  # moving to free space

    def highlightEnPassant(self, col, row):
        board = window.scene.board_history[len(window.scene.board_history) - 2]
        board_now = window.scene.current_figures

        # White pawns en passant
        if row == 3 and board_now[row][col] == 'p':
            # Left en passant
            if col - 1 >= 0 and row - 2 >= 0 and board[row - 2][col - 1] == 'P' and board_now[row][col - 1] == 'P':
                window.scene.highlighted.append([col - 1, row - 1])  # Highlighting gets x, y and not row, col
            # Right en passant
            if col + 1 <= 7 and row - 2 >= 0 and board[row - 2][col + 1] == 'P' and board_now[row][col + 1] == 'P':
                window.scene.highlighted.append([col + 1, row - 1])

        # Black pawns en passant
        if row == 4 and board_now[row][col] == 'P':
            # Left en passant
            if col - 1 >= 0 and row + 2 <= 7 and board[row + 2][col - 1] == 'p' and board_now[row][col - 1] == 'p':
                window.scene.highlighted.append([col - 1, row + 1])  # Highlighting gets x, y and not row, col
            # Right en passant
            if col + 1 <= 7 and row + 2 <= 7 and board[row + 2][col + 1] == 'p' and board_now[row][col + 1] == 'p':
                window.scene.highlighted.append([col + 1, row + 1])

    # Adding castling to highlighted moves if possible, then returning the logic value if castling is possible
    def highlightCastling(self, col, row):
        smallCastling = True
        bigCastling = True
        king = 'k'
        rook = 'r'

        # If a king is checked there is no castling
        if window.scene.turn == 1 and window.scene.w_king_checked:
            return
        elif window.scene.turn == -1 and window.scene.b_king_checked:
            return

        # Changing figures to black (uppercase) if the chosen row is 0
        if row == 0:
            king = king.upper()
            rook = rook.upper()

        # Checking if king and rooks haven't moved the whole game
        for board in window.scene.board_history:
            if board[row][col] != king:
                smallCastling = False
                bigCastling = False
                break  # Both castlings already impossible, no need to check more
            elif board[row][7] != rook and smallCastling:
                smallCastling = False
                if not bigCastling:  # Ending loop if another castling already is impossible
                    break
            elif board[row][0] != rook and bigCastling:
                bigCastling = False
                if not smallCastling:
                    break

        board = window.scene.current_figures

        # To not get index out of bounds
        if col + 2 > 7:
            return

        # Checking if there are no pieces between kings and rooks
        if board[row][col + 1] != '' or board[row][col + 2] != '':
            smallCastling = False
        if board[row][col - 1] != '' or board[row][col - 2] != '' or board[row][col - 3]:
            bigCastling = False

        # Highlighting possible castling
        if smallCastling:
            window.scene.highlighted.append([col + 2, row])  # Highlighted point is x, y
        if bigCastling:
            window.scene.highlighted.append([col - 2, row])

        if smallCastling or bigCastling:
            return True
        else:
            return False

    # Highlighting moves for a chosen chess piece
    def highlightMoves(self, wantedX, wantedY, checking=False):
        if (window.scene.turn == 1 and self.figure.isupper()) or (window.scene.turn == -1 and self.figure.islower()):
            checking = False

        w_king_checked = window.scene.w_king_checked
        b_king_checked = window.scene.b_king_checked
        king_checked = False
        # if (w_king_checked and window.scene.turn == 1) or (b_king_checked and window.scene.turn == -1):
        #     king_checked = True

        window.scene.highlighted = [[wantedX, wantedY]]

        # Black pawn
        if self.figure == 'P' and not king_checked:
            self.highlightEnPassant(wantedX, wantedY)
            move_range = 2 if self.y == 1 else 1
            if self.checkMove(wantedX, wantedY + 1) == 2:
                window.scene.highlighted.append([wantedX, wantedY + 1])
                if move_range == 2 and self.checkMove(wantedX, wantedY + 2) == 2:
                    window.scene.highlighted.append([wantedX, wantedY + 2])
            if self.checkMove(wantedX - 1, wantedY + 1) == 1:
                window.scene.highlighted.append([wantedX - 1, wantedY + 1])
            if self.checkMove(wantedX + 1, wantedY + 1) == 1:
                window.scene.highlighted.append([wantedX + 1, wantedY + 1])

        # Lower pawn
        elif self.figure == 'p' and not king_checked:
            self.highlightEnPassant(wantedX, wantedY)
            move_range = 2 if self.y == 6 else 1
            if self.checkMove(wantedX, wantedY - 1) == 2:
                window.scene.highlighted.append([wantedX, wantedY - 1])
                if move_range == 2 and self.checkMove(wantedX, wantedY - 2) == 2:
                    window.scene.highlighted.append([wantedX, wantedY - 2])
            if self.checkMove(wantedX - 1, wantedY - 1) == 1:
                window.scene.highlighted.append([wantedX - 1, wantedY - 1])
            if self.checkMove(wantedX + 1, wantedY - 1) == 1:
                window.scene.highlighted.append([wantedX + 1, wantedY - 1])

        # Kings
        elif (self.figure == 'K' and not w_king_checked) or (self.figure == 'k' and not b_king_checked):
            self.highlightCastling(wantedX, wantedY)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == dy == 0:
                        continue
                    if self.checkMove(wantedX + dx, wantedY + dy) in [1, 2]:
                        window.scene.highlighted.append([wantedX + dx, wantedY + dy])

        # Queens
        elif (self.figure == 'Q' or self.figure == 'q') and not king_checked:
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]
            for dx, dy in moves:
                x, y = wantedX, wantedY
                while True:
                    x, y = x + dx, y + dy
                    if self.checkMove(x, y) == 2:
                        window.scene.highlighted.append([x, y])
                    elif self.checkMove(x, y) == 1:
                        window.scene.highlighted.append([x, y])
                        break
                    else:
                        break

        # Bishops
        elif (self.figure == 'B' or self.figure == 'b') and not king_checked:
            moves = [(1, 1), (-1, -1), (-1, 1), (1, -1)]
            for dx, dy in moves:
                x, y = wantedX, wantedY
                while True:
                    x, y = x + dx, y + dy
                    if self.checkMove(x, y) == 2:
                        window.scene.highlighted.append([x, y])
                    elif self.checkMove(x, y) == 1:
                        window.scene.highlighted.append([x, y])
                        break
                    else:
                        break

        # Rooks
        elif (self.figure == 'R' or self.figure == 'r') and not king_checked:
            moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dx, dy in moves:
                x, y = wantedX, wantedY
                while True:
                    x, y = x + dx, y + dy
                    if self.checkMove(x, y) == 2:
                        window.scene.highlighted.append([x, y])
                    elif self.checkMove(x, y) == 1:
                        window.scene.highlighted.append([x, y])
                        break
                    else:
                        break

        # Knights
        elif (self.figure == 'N' or self.figure == 'n') and not king_checked:
            window.scene.highlighted += [[x, y] for x, y in [(wantedX - 2, wantedY + 1), (wantedX - 2, wantedY - 1),
                                                             (wantedX + 2, wantedY + 1), (wantedX + 2, wantedY - 1),
                                                             (wantedX - 1, wantedY - 2), (wantedX + 1, wantedY - 2),
                                                             (wantedX - 1, wantedY + 2), (wantedX + 1, wantedY + 2)]
                                         if self.checkMove(x, y) != 0]

        else:
            window.scene.highlighted = [[]]
            window.scene.AIchoice = []

        if checking:
            # print("Checking highlighted move")
            # Filtering for check mechanics
            filtered_highlighted_moves = []
            current_figs = copy.deepcopy(window.scene.current_figures)

            for move in window.scene.highlighted:
                if move == []:
                    break
                # print("Checking for move: ", move)
                new_x, new_y = move

                # Apply the move on the string matrix
                # print(self.x, self.y)
                future_figs = copy.deepcopy(current_figs)
                buffer = future_figs[self.y][self.x]
                future_figs[self.y][self.x] = ''
                future_figs[new_y][new_x] = buffer

                # print("Made a move")
                #
                # # Print the future_figs matrix
                # print("future_figs matrix:")
                # for row in future_figs:
                #     print(row)
                # print()

                # Create a ChessPiece matrix based on the updated string matrix
                future_board = []
                for row in range(8):
                    pieces_row = []
                    for col in range(8):
                        figure = future_figs[row][col]
                        if figure != '':
                            piece = ChessPiece(col * 100, row * 100, 80, figure)
                            pieces_row.append(piece)
                        else:
                            pieces_row.append(None)
                    future_board.append(pieces_row)

                # Check if the king is checked after the move
                w_check, b_check = self.checkCheck(future_board, True)
                if (window.scene.turn == 1 and not w_check) or (window.scene.turn == -1 and not b_check):
                    # print("Move valid, adding")
                    filtered_highlighted_moves.append(move)
                else:
                    # print("Not adding a move - invalid")
                    pass

            # Update the highlighted moves with the filtered ones
            window.scene.highlighted = filtered_highlighted_moves

    def checkCheck(self, board, checking=False):
        # print("Checking check")
        w_king = None
        b_king = None

        white_checked = False
        black_checked = False

        for row in board:
            for piece in row:
                if isinstance(piece, ChessPiece) and piece.figure == 'k':
                    w_king = [piece.x, piece.y]
                if isinstance(piece, ChessPiece) and piece.figure == 'K':
                    b_king = [piece.x, piece.y]

        for row in board:
            for piece in row:
                if isinstance(piece, ChessPiece) and piece.figure.isupper() \
                        and window.scene.turn == 1:  # Check for white king
                    piece.highlightMoves(piece.x, piece.y, True)
                    if w_king in window.scene.highlighted:
                        if not checking:
                            window.scene.w_king_checked = True
                        else:
                            white_checked = True
                        # print("Checked white king")
                elif isinstance(piece, ChessPiece) and piece.figure.islower() \
                        and window.scene.turn == -1:  # Check for black king
                    piece.highlightMoves(piece.x, piece.y, True)
                    if b_king in window.scene.highlighted:
                        if not checking:
                            window.scene.b_king_checked = True
                        else:
                            black_checked = True
                        # print("Checked black king")

        return white_checked, black_checked



class AnalogClock(QWidget):
    secondHand = QPolygon([
        QPoint(90, 0),
        QPoint(-1, -3),
        QPoint(-1, 3)])

    msecHand = QPolygon([
        QPoint(90, 0),
        QPoint(-1, -2),
        QPoint(-1, 2)])

    msecColor = QColor(127, 0, 127)
    secondColor = QColor(195, 0, 0)
    secondsColor = QColor(0, 100, 250)

    def __init__(self):
        super(AnalogClock, self).__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1)
        self.time_start = QTime.currentTime()
        self.resize(600, 600)
        self.elapsed_time = 0
        self.move(1000, 0)
        self.setMouseTracking(True)
        self.setCursor(Qt.OpenHandCursor)
        self.time_limit = 30

        # Time limit from config file
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                self.time_limit = int(config.get("time_per_turn", ""))

        except FileNotFoundError:
            pass

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        time = QTime.currentTime()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200, side / 200)

        # Drawing millisecond hand
        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.msecColor)
        painter.save()
        painter.rotate(-90)
        painter.rotate(3.6 * (time.msec() - self.time_start.msec()) / 10)  # Full circle every second
        painter.drawConvexPolygon(AnalogClock.msecHand)
        painter.restore()

        # Drawing every fifth line red
        painter.setPen(AnalogClock.secondColor)
        for i in range(12):
            if i == 3:
                painter.drawLine(80, 0, 98, 0)  # 30 seconds line
            else:
                painter.drawLine(90, 0, 98, 0)

            painter.rotate(30.0)

        # Drawing second lines red
        painter.setPen(AnalogClock.secondsColor)
        for j in range(60):
            if (j % 5) != 0:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        # Drawing second hand
        painter.rotate(-90)
        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.secondColor)
        painter.save()
        painter.rotate(6 * (time.second() - self.time_start.second() + (time.msec() - self.time_start.msec()) / 1000))
        painter.drawConvexPolygon(AnalogClock.secondHand)
        painter.restore()

        # Drawing circle at the center of the clock
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.secondColor)
        painter.drawEllipse(-4, -4, 8, 8)

        # Difference of starting time and current time in seconds
        self.elapsed_time = self.time_start.msecsTo(time) / 1000.0

        # End of time
        if self.elapsed_time >= self.time_limit:
            self.timer.stop()  # stop the timer
            window.scene.turn = window.scene.turn * 2
            window.scene.draw_board()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            self.endTurn()

    def endTurn(self):
        if window.scene.piece_moved:
            # Changing the turn
            if window.client:
                window.client.send_message(str(copy.deepcopy(window.scene.current_figures)))
            window.scene.turn = -window.scene.turn
            window.scene.highlighted = [[]]
            window.scene.AIchoice = []
            window.scene.piece_moved = False

            # Resetting the check status after the turn ends
            if window.scene.turn == 1:
                window.scene.b_king_checked = False
            elif window.scene.turn == -1:
                window.scene.w_king_checked = False

            self.time_start = QTime.currentTime()

            # Saving current board state to history (beginning of the next turn)
            database = sqlite3.connect('game_history.db')
            cursor = database.cursor()

            # Inserting the current state of the board, turn number and which side it is
            board = str(window.scene.current_figures)
            turn = window.scene.turn
            time_taken = self.elapsed_time
            insert_statement = 'INSERT INTO game_states(turn_side, board_state, time_taken) VALUES (?, ?, ?)'
            cursor.execute(insert_statement, (turn, board, time_taken))

            # Execute a SELECT statement to retrieve all the rows and columns from the table
            cursor.execute('SELECT * FROM game_states')

            # Fetch all the rows and store them in a variable
            rows = cursor.fetchall()

            # Commiting changes and closing the connection
            database.commit()
            database.close()

            # Checking if the king is checked
            piece = ChessPiece(0, 0, 0, 'p')
            piece.checkCheck(window.scene.pieces_matrix)

            # Drawing the board
            window.scene.draw_board()

            # AI making the move if possible
            self.chessBot()

        else:
            pass

    def chessBot(self):
        # Making a move as AI
        if (window.scene.players == 1 and window.scene.turn == -1) or window.scene.players == 3:
            # board = copy.deepcopy(window.scene.current_figures)
            chessbot = ChessAI(window.scene.current_figures, window.scene.pieces_matrix, window.scene.turn)
            # new_board = chessbot.makeMove()

            # Ending AI turn
            # window.scene.current_figures = new_board
            window.scene.piece_moved = True
            window.scene.draw_board()

        else:
            window.scene.highlighted = [[]]
            window.scene.draw_board()

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        if event.buttons() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

    def hoverLeaveEvent(self, event):
        self.unsetCursor()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess Board")

        # Central widget and layout
        self.central_widget = QWidget(self)
        self.layout = QHBoxLayout(self.central_widget)
        self.client = None
        self.client_thread = None

        self.menu_dialog()

    # Actuall received message handle
    def on_message_received(self, data):
        messages = data.split('\n')
        for message in messages:
            # Remove trailing newlines
            message = message.strip()
            if not message:
                continue
            # print(f"{message}")
            if message in ["-1", "1"]:
                window.scene.my_turn = int(message)
                self.clock.timer.stop()
                self.clock.time_start = QTime.currentTime()
                # print("window.scene.my_turn: ", window.scene.my_turn)
            elif message == "refresh":
                # print("window.scene.my_turn (refresh): ", window.scene.my_turn)
                self.clock.timer.start()
                self.clock.time_start = QTime.currentTime()
                self.scene.draw_board()
                self.scene.update()
            else:
                pattern = r"\[\[.*\]\]"
                result = re.search(pattern, message)
                if result:
                    matrix_str = result.group()
                    self.scene.current_figures = ast.literal_eval(matrix_str)
                    self.scene.turn = -self.scene.turn
                    self.clock.time_start = QTime.currentTime()
                    self.scene.highlighted = [[]]
                    self.scene.draw_board()
                    self.scene.update()

    def menu_dialog(self):
        # Left side of menu
        self.left_menu_widget = QWidget(self)
        self.left_menu_layout = QVBoxLayout(self.left_menu_widget)

        # IP address
        self.ip_address_label = QLabel("IP address:")
        self.ip_address_label.setFont(QFont("Times New Roman", 20))
        self.ip_address_textbox = QLineEdit()
        self.ip_address_textbox.setFont(QFont("Times New Roman", 20))
        self.ip_address_textbox.setPlaceholderText("xxx.xxx.xxx.xxx")
        self.left_menu_layout.addWidget(self.ip_address_label)
        self.left_menu_layout.addWidget(self.ip_address_textbox)

        # Port
        self.port_label = QLabel("Port:")
        self.port_label.setFont(QFont("Times New Roman", 20))
        self.port_textbox = QLineEdit()
        self.port_textbox.setFont(QFont("Times New Roman", 20))
        self.port_textbox.setPlaceholderText("xxxxx")
        self.left_menu_layout.addWidget(self.port_label)
        self.left_menu_layout.addWidget(self.port_textbox)

        # Number of players
        self.player_label = QLabel("Choose players")
        self.player_label.setFont(QFont("Times New Roman", 20))
        self.one_player_button = QRadioButton("1 player")
        self.one_player_button.setFont(QFont("Times New Roman", 20))
        self.two_player_button = QRadioButton("2 players")
        self.two_player_button.setFont(QFont("Times New Roman", 20))
        self.ai_player_button = QRadioButton("AI vs AI")
        self.ai_player_button.setFont(QFont("Times New Roman", 20))
        self.left_menu_layout.addWidget(self.player_label)
        self.left_menu_layout.addWidget(self.one_player_button)
        self.left_menu_layout.addWidget(self.two_player_button)
        self.left_menu_layout.addWidget(self.ai_player_button)
        self.one_player_button.setChecked(True)

        # Start and Load buttons
        self.start_button = QPushButton("Start new game")
        self.start_button.setFont(QFont("Times New Roman", 20))
        self.start_button.clicked.connect(self.new_game)
        self.load_button = QPushButton("Load game")
        self.load_button.setFont(QFont("Times New Roman", 20))
        self.load_button.clicked.connect(self.load_game)
        self.left_menu_layout.addWidget(self.start_button)
        self.left_menu_layout.addWidget(self.load_button)

        # Right side of menu
        self.right_menu_widget = QWidget(self)
        self.right_menu_layout = QVBoxLayout(self.right_menu_widget)

        # Default theme
        theme_label = QLabel("Default theme:")
        theme_label.setFont(QFont("Times New Roman", 20))
        self.classic_button = QRadioButton("Classic")
        self.classic_button.setFont(QFont("Times New Roman", 20))
        self.coffee_button = QRadioButton("Coffee")
        self.coffee_button.setFont(QFont("Times New Roman", 20))
        self.aqua_button = QRadioButton("Aqua")
        self.aqua_button.setFont(QFont("Times New Roman", 20))
        self.right_menu_layout.addWidget(theme_label)
        self.right_menu_layout.addWidget(self.classic_button)
        self.right_menu_layout.addWidget(self.coffee_button)
        self.right_menu_layout.addWidget(self.aqua_button)
        self.classic_button.setChecked(True)

        # Time per turn
        time_label = QLabel("Time per turn:")
        time_label.setFont(QFont("Times New Roman", 20))
        self.time_textbox = QLineEdit()
        self.time_textbox.setFont(QFont("Times New Roman", 20))
        self.time_textbox.setText("30")
        self.right_menu_layout.addWidget(time_label)
        self.right_menu_layout.addWidget(self.time_textbox)

        # Saving history to xml on exit
        self.save_history_checkbox = QCheckBox("Save history to XML")
        self.save_history_checkbox.setFont(QFont("Times New Roman", 20))
        self.save_history_checkbox.setChecked(True)
        self.right_menu_layout.addWidget(self.save_history_checkbox)

        # Restore to default
        self.restore_button = QPushButton("Restore settings")
        self.restore_button.setFont(QFont("Times New Roman", 20))
        self.restore_button.clicked.connect(self.restore_settings)
        self.right_menu_layout.addWidget(self.restore_button)

        # Add left and right menus to main layout
        self.layout.addWidget(self.left_menu_widget)
        self.layout.addWidget(self.right_menu_widget)

        # Set central widget for the dialog
        self.setCentralWidget(self.central_widget)

        # Loading states from config file
        self.load_config()

    def new_game(self):
        # Saving changes to the config file
        self.save_config()

        # Deleting any existing database
        if os.path.exists("game_history.db"):
            os.remove("game_history.db")
            # print("New game - deleted existing database, creating a new one")

        # Connecting to the database
        database = sqlite3.connect('game_history.db')
        cursor = database.cursor()

        # Creating a new table if there isn't one
        if os.stat('game_history.db').st_size == 0:
            cursor.execute('''
                               CREATE TABLE game_states(
                               id INTEGER PRIMARY KEY,
                               turn_side INTEGER,
                               board_state TEXT,
                               time_taken FLOAT
                               )
                               ''')

            # Inserting the current state of the board, turn number and which side it is
            board = str([['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
                         ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
                         ['', '', '', '', '', '', '', ''],
                         ['', '', '', '', '', '', '', ''],
                         ['', '', '', '', '', '', '', ''],
                         ['', '', '', '', '', '', '', ''],
                         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
                         ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']])
            insert_statement = 'INSERT INTO game_states(turn_side, board_state, time_taken) VALUES (?, ?, ?)'
            cursor.execute(insert_statement, (1, board, 0))

        else:
            pass

        database.commit()
        database.close()

        if self.one_player_button.isChecked():
            self.start_game(1)
        elif self.two_player_button.isChecked():
            self.start_game(2)
        elif self.ai_player_button.isChecked():
            self.start_game(3)

    def load_game(self):
        # Saving changes to the config file
        self.save_config()

        # Can't load a game without history
        if not os.path.exists("game_history.db"):
            # print("Game history files not found.")
            return

        # Running the game
        if self.one_player_button.isChecked():
            self.start_game(1)
        elif self.two_player_button.isChecked():
            self.start_game(2)
        elif self.ai_player_button.isChecked():
            self.start_game(3)

    def start_game(self, players_number):
        # Removing the menu
        self.layout.removeWidget(self.left_menu_widget)
        self.layout.removeWidget(self.right_menu_widget)

        # Normal game drawing
        central_widget = QWidget(self)
        layout = QGridLayout(central_widget)

        self.view = QGraphicsView(self)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scene = ChessBoard(players_number)
        self.view.setScene(self.scene)
        self.view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)  # Scaling

        # Starting server
        if players_number == 2:
            # Printing given IP and mask
            ip_address = self.ip_address_textbox.text()
            port = self.port_textbox.text()
            # print("Starting game with IP address:", ip_address, "and port:", port)

            # Connecting with server
            self.client = Client(ip_address, port)
            self.client_thread = ClientThread(self.client)
            self.client_thread.message_received.connect(window.on_message_received)
            self.client_thread.start()

        # A separate widget with a vertical layout
        widget = QWidget(self)
        vlayout = QVBoxLayout(widget)
        vlayout.setAlignment(Qt.AlignCenter)

        # Notation label and input line
        self.chess_notation_label = QLabel("CHESS NOTATION:")
        self.chess_notation_label.setFont(QFont("Times New Roman", 30))
        self.chess_notation_input = QLineEdit()
        self.chess_notation_input.setFont(QFont("Times New Roman", 30))
        self.chess_notation_input.returnPressed.connect(self.process_chess_notation)
        vlayout.addWidget(self.chess_notation_label, alignment=Qt.AlignCenter)
        vlayout.addWidget(self.chess_notation_input, alignment=Qt.AlignCenter)

        # Clock
        self.clock_view = QGraphicsView(self)
        self.clock_scene = QGraphicsScene()
        self.clock = AnalogClock()
        self.time_limit_label = QLabel(f"Time limit: {self.clock.time_limit}s")
        self.time_limit_label.setFont(QFont("Times New Roman", 30))
        self.clock_scene.addWidget(self.clock)
        self.clock_view.setScene(self.clock_scene)
        self.clock_view.setRenderHint(QPainter.Antialiasing)
        self.clock_view.setFixedSize(603, 603)
        self.clock_view.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        vlayout.addWidget(self.clock_view, alignment=Qt.AlignCenter)
        vlayout.addWidget(self.time_limit_label, alignment=Qt.AlignCenter)

        # Exit button
        self.exit_button = QPushButton("Exit")
        self.exit_button.setFont(QFont("Times New Roman", 30))
        self.exit_button.clicked.connect(self.exit)
        vlayout.addWidget(self.exit_button, alignment=Qt.AlignCenter)

        # Replay button
        self.replay_button = QPushButton("Replay")
        self.replay_button.setFont(QFont("Times New Roman", 30))
        self.replay_button.clicked.connect(self.replay_moves)
        vlayout.addWidget(self.replay_button, alignment=Qt.AlignCenter)

        # Main layout
        layout.addWidget(self.view, 0, 0)  # Chessboard
        layout.addWidget(widget, 0, 1)  # Label, notation, clock and buttons
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        # Handling AI battle
        if players_number == 3:
            self.scene.turn = -1
            self.scene.piece_moved = True
            self.clock.endTurn()

        self.setCentralWidget(central_widget)
        self.showFullScreen()

    def exit(self):
        # Checking if saving to xml
        try:
            with open("config.json", "r") as f:
                config = json.load(f)

                if not config.get("save_xml", False):
                    # print("Not saving history to xml")
                    self.close()
                    return
        except FileNotFoundError:
            pass

        database = sqlite3.connect('game_history.db')
        cursor = database.cursor()

        cursor.execute('SELECT * FROM game_states')

        game_states = cursor.fetchall()

        root = ET.Element("game_history")

        for game_state in game_states:
            game_state_element = ET.SubElement(root, "game_state")
            game_state_element.set("id", str(game_state[0]))
            turn_side_element = ET.SubElement(game_state_element, "turn_side")
            turn_side_element.text = str(game_state[1])
            board_state_element = ET.SubElement(game_state_element, "board_state")
            board_state_element.text = game_state[2]
            time_taken_element = ET.SubElement(game_state_element, "time_taken")
            time_taken_element.text = str(game_state[3])

        tree = ET.ElementTree(root)
        indent_xml(tree.getroot())
        tree.write("game_hist.xml", encoding="utf-8", xml_declaration=True, method="xml")
        database.close()

        # Printing the xml
        # print("Saved the game history as xml file")
        # Load the XML file
        tree = ET.parse('game_hist.xml')
        root = tree.getroot()

        for game_state in root.findall('game_state'):
            state_id = game_state.get('id')
            turn_side = game_state.find('turn_side').text
            board_state = game_state.find('board_state').text.strip()
            time_taken = game_state.find('time_taken').text
            rows = ast.literal_eval(board_state)
            # print(f'\nTurn number ID: {state_id}')
            # print(f'Turn side: {turn_side}')
            # print(f'Time taken: {time_taken}s')
            # print(f'Board state:')
            # for row in rows:
            #     print(row)

        self.close()

    def replay_moves(self):
        window.scene.replay()
        return

    def save_config(self):
        config = {
            "ip_address": self.ip_address_textbox.text(),
            "port": self.port_textbox.text(),
            "players_1": self.one_player_button.isChecked(),
            "players_2": self.two_player_button.isChecked(),
            "players_ai": self.ai_player_button.isChecked(),
            "theme_classic": self.classic_button.isChecked(),
            "theme_coffee": self.coffee_button.isChecked(),
            "theme_aqua": self.aqua_button.isChecked(),
            "time_per_turn": self.time_textbox.text(),
            "save_xml": self.save_history_checkbox.isChecked()
        }

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    def load_config(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)

                self.one_player_button.setChecked(config.get("players_1", False))
                self.two_player_button.setChecked(config.get("players_2", False))
                self.ai_player_button.setChecked(config.get("players_ai", False))
                self.classic_button.setChecked(config.get("theme_classic", False))
                self.coffee_button.setChecked(config.get("theme_coffee", False))
                self.aqua_button.setChecked(config.get("theme_aqua", False))
                self.save_history_checkbox.setChecked(config.get("save_xml", False))
                self.ip_address_textbox.setText(config.get("ip_address", ""))
                self.port_textbox.setText(config.get("port", ""))
                self.time_textbox.setText(config.get("time_per_turn", ""))

        except FileNotFoundError:
            # Don't load anything if the file doesn't exist
            pass

    def restore_settings(self):
        self.layout.removeWidget(self.left_menu_widget)
        self.layout.removeWidget(self.right_menu_widget)
        if os.path.exists("config.json"):
            os.remove("config.json")
        self.menu_dialog()

    def process_chess_notation(self):
        figure = None
        x_dest, y_dest = None, None

        # Creating a list of characters for notation
        notation = list(self.chess_notation_input.text())

        # Deleting all spacebars
        while ' ' in notation:
            notation.remove(' ')

        # Checking notations
        if len(notation) == 2 and notation[0].islower():  # Pawn move
            notation.insert(0, 'P')

        if len(notation) == 4 and notation[0] == 'N' and notation[2].islower():  # 4 signs knights notation
            figure = None
            if self.scene.turn == 1:  # White turn
                figure = notation[0].lower()
            elif self.scene.turn == -1:  # Black turn
                figure = notation[0].upper()

            rc = notation[1]  # row (y values) or a column (x values)
            isRow = False

            # Reading destination positions
            x_dest = ord(notation[2]) - ord('a')
            y_dest = 7 - (ord(notation[3]) - ord('1'))

            # print(x_dest, y_dest)

            # Checking if rc is for rows or for columns
            if ord(notation[1].lower()) - ord('a') in range(8):  # Column / x value
                rc = int(ord(notation[1].lower()) - ord('a'))
                isRow = False

            elif 7 - (ord(notation[1]) - ord('1')) in range(8):  # Row / y value
                rc = int(7 - (ord(notation[1]) - ord('1')))
                isRow = True

            # Checking for multiple appearance of the same piece in a row or a column
            counter = 0
            index = 0
            if isRow:
                for col in range(8):
                    if self.scene.current_figures[rc][col] == figure:
                        counter += 1
                        index = int(col)
            else:
                for row in range(8):
                    if self.scene.current_figures[row][rc] == figure:
                        counter += 1
                        index = int(row)

            # Ignoring move if there are multiple pieces
            if counter > 1:
                # print("Multiple pieces in a way")
                self.chess_notation_input.clear()
                return

            # Setting the piece on destination point
            if isRow:
                relativeX = x_dest - index
                relativeY = y_dest - rc
                self.scene.pieces_matrix[rc][index].setCoordinates(relativeX, relativeY)
            else:
                relativeX = x_dest - rc
                relativeY = y_dest - index
                self.scene.pieces_matrix[index][rc].setCoordinates(relativeX, relativeY)

            self.chess_notation_input.clear()

        if len(notation) == 3 and notation[0].isupper() and notation[1].islower():  # Typical notation move
            if self.scene.turn == 1:  # White turn
                figure = notation[0].lower()
            elif self.scene.turn == -1:  # Black turn
                figure = notation[0].upper()

            # Destination point on chessboard
            x_dest = ord(notation[1].upper()) - ord('A')
            y_dest = 7 - (ord(notation[2]) - ord('1'))

            # Checking if knights can have the same destination spot
            if figure == 'N' or figure == 'n':
                # Getting positions of the knights of the same color
                n_ind = [(col_idx, row_idx) for row_idx, row in enumerate(self.scene.current_figures) for col_idx, val
                         in
                         enumerate(row) if val == figure]

                n1_x = n_ind[0][0]
                n1_y = n_ind[0][1]

                n2_x = n_ind[1][0]
                n2_y = n_ind[1][1]

                # Checking if they can move to the destination point
                knight1_able, knight2_able = False, False
                # print(self.scene.pieces_matrix[n1_x][n1_y].figure)

                self.scene.pieces_matrix[n1_y][n1_x].highlightMoves(n1_x, n1_y)
                if self.scene.pieces_matrix[n1_y][n1_x].checkMove(x_dest, y_dest) \
                        and ([x_dest, y_dest] in self.scene.highlighted):
                    knight1_able = True
                self.scene.highlighted = [[]]
                self.scene.AIchoice = []

                self.scene.pieces_matrix[n2_y][n2_x].highlightMoves(n2_x, n2_y)
                if self.scene.pieces_matrix[n2_y][n2_x].checkMove(x_dest, y_dest) \
                        and ([x_dest, y_dest] in self.scene.highlighted):
                    knight2_able = True
                self.scene.highlighted = [[]]
                self.scene.AIchoice = []

                if knight1_able and knight2_able:
                    self.chess_notation_input.clear()
                    return

            # Indices of specific figures
            indices = [(col_idx, row_idx) for row_idx, row in enumerate(self.scene.current_figures) for col_idx, val in
                       enumerate(row) if val == figure]

            # Checking moves based on notation for each piece, until the right one is found
            for coords in indices:
                relativeX = x_dest - coords[0]
                relativeY = y_dest - coords[1]

                # If the right piece made a move, quit loop
                if self.scene.pieces_matrix[coords[1]][coords[0]].setCoordinates(relativeX, relativeY):
                    break

        # Pawn with promotion 4 signs (turning to 3 signs)
        if len(notation) == 4 and notation[0] == 'P' and notation[1].islower() and notation[3].isupper():
            notation.remove('P')
        # Pawn with promotion
        if len(notation) == 3 and notation[0].islower() and notation[2].isupper() \
                and notation[2] in ['Q', 'R', 'B', 'N']:
            if self.scene.turn == 1:  # White turn
                figure = 'p'
            elif self.scene.turn == -1:  # Black turn
                figure = 'P'

            # Destination point on chessboard
            x_dest = ord(notation[0].upper()) - ord('A')
            y_dest = 7 - (ord(notation[1]) - ord('1'))

            # Indices of pawns that are able to make a move with promotion
            if figure == 'p':
                indices = [(col_idx, 1) for col_idx, val in enumerate(self.scene.current_figures[1]) if val == 'p']
            elif figure == 'P':
                indices = [(col_idx, 6) for col_idx, val in enumerate(self.scene.current_figures[6]) if val == 'P']
            else:
                indices = []

            # Checking moves based on notation for each piece, until the right one is found
            for coords in indices:
                relativeX = x_dest - coords[0]
                relativeY = y_dest - coords[1]

                # If the right piece made a move, quit loop
                if self.scene.pieces_matrix[coords[1]][coords[0]].setCoordinates(relativeX, relativeY, True):
                    if self.scene.turn == 1:
                        self.scene.current_figures[y_dest][x_dest] = notation[2].lower()
                    elif self.scene.turn == -1:
                        self.scene.current_figures[y_dest][x_dest] = notation[2]

                    self.scene.draw_board()
                    break

        # Just for convenience of user input making every character uppercase for castling
        notation = list(map(str.upper, notation))

        # Both castling cases
        if notation == list("O-O-O") or notation == list("O-O"):
            row = None
            king = None
            if window.scene.turn == 1:
                row = 7
                king = 'k'
            elif window.scene.turn == -1:
                row = 0
                king = 'K'

            # If there is no king to move, there is no castling
            if window.scene.current_figures[row][4] != king:
                return

            # Small castling
            if notation == list("O-O") and self.scene.pieces_matrix[row][4].setCoordinates(2, 0):
                self.scene.current_figures[row][4] = ''

            elif notation == list("O-O-O") and self.scene.pieces_matrix[row][4].setCoordinates(-2, 0):
                self.scene.current_figures[row][4] = ''

        self.scene.draw_board()
        self.chess_notation_input.clear()


def indent_xml(element, level=0):
    indent_str = "\n" + level * "  "
    if len(element):
        if not element.text or not element.text.strip():
            element.text = indent_str + "  "
        if not element.tail or not element.tail.strip():
            element.tail = indent_str
        for elem in element:
            indent_xml(elem, level + 1)
        if not element.tail or not element.tail.strip():
            element.tail = indent_str
    elif level and (not element.tail or not element.tail.strip()):
        element.tail = indent_str


if __name__ == "__main__":
    server_thread = threading.Thread(target=server_main, daemon=True)
    server_thread.start()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
