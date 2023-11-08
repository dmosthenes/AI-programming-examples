"""
Tic Tac Toe Player
"""

import math
import copy
import random

X = "X"
O = "O"
EMPTY = None


class InvalidAction(Exception):
    """
    Exception raised when an attempt is made to make an invalid move.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(message)

def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    
    Xs = 0
    Os = 0

    for row in board:
        for cell in row:
            if cell is X:
                Xs += 1
            if cell is O:
                Os += 1
    
    board_total = Xs + Os

    if board_total == 9:
        return None
    elif board_total == 0:
        return X
    elif Xs > Os:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    
    available_moves = []

    for i, row in enumerate(board):
        for j, cell in enumerate(row):
            if cell is EMPTY:
                available_moves.append((i,j))

    return available_moves

def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    
    # Raise invalid action exception if action cannot be performed for given board
    if board[action[0]][action[1]] is not EMPTY:
        raise InvalidAction("Attempted move is invalid.")
    
    # Construct new board with action
    new_board = copy.deepcopy(board)

    # Insert proposed action
    new_board[action[0]][action[1]] = player(board)
    return new_board

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    # Check for wins in each row
    for row in board:
        if allTheSame(row):
            return row[0]
    
    # Check for wins in each column
    for i in range(3):
        col = []
        col.append(board[0][i])
        col.append(board[1][i])
        col.append(board[2][i])
        if allTheSame(col):
            return col[0]
        
    # Check for wins along both diagonals
    left_diag = []
    left_diag.append(board[0][0])
    left_diag.append(board[1][1])
    left_diag.append(board[2][2])
    if allTheSame(left_diag):
        return left_diag[0]
    
    right_diag = []
    right_diag.append(board[0][2])
    right_diag.append(board[1][1])
    right_diag.append(board[2][0])
    if allTheSame(right_diag):
        return right_diag[0]
    
    # Otherwise, there is no winner
    return None

def allTheSame(trio):
    """
    Returns True if all inputs are the same value.
    """

    if trio[0] == trio[1] and trio[1] == trio[2]:
        return True
    return False

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    
    # Game is not over if there is no winner and there are empty cells
    if winner(board) is None:
        for row in board:
            for cell in row:
                if cell is EMPTY:
                    return False
    
    # Otherwise game is over
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    Assumes board is a terminal board.
    """
    
    if winner(board) is X:
        return 1
    elif winner(board) is O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    # If first move, pick randomly
    if board == initial_state():
        return (random.randint(0,2), random.randint(0,2))

    # Return None if board is terminal
    if terminal(board):
        return None

    # Get current player
    playa = player(board)

    # Get all possible moves
    frontier = actions(board)

    # Store best move
    best_move = None

    # Find maximising move if X
    if playa is X:

        # Set value to be lowest possible
        v = -2

        # Loop over each move
        for move in frontier:

            # Check if utility score is higher than v
            utility_score = maxhelper(result(board, move))
            if v < utility_score:
                best_move = move
                v = utility_score

        return best_move
    
    # Find minimising move if O
    else:

        # Set value to be highest possible
        v = 2

        # Loop over each move
        for move in frontier:

            # Check if utility score is higher than v
            utility_score = minhelper(result(board, move))
            if v > utility_score:
                best_move = move
                v = utility_score

        return best_move


def minhelper(board):
    """
    Return the utility of the given board.
    """

    # Base case: board is terminal, return its utility
    if terminal(board):
        return utility(board)
    
    # Recursive bit: search tree of available moves
    available_moves = actions(board)

    v = -2
    
    for move in available_moves:
        utility_score = maxhelper(result(board, move))
        if v < utility_score:
            v = utility_score

    return v


def maxhelper(board):
    """
    Find the max move for the given board.
    """

    # Base case: board is terminal, return its utility
    if terminal(board):
        return utility(board)
    
    # Recursive bit: search tree of available moves
    available_moves = actions(board)

    v = 2

    for move in available_moves:
        utility_score = minhelper(result(board, move))
        if v > utility_score:
            v = utility_score

    return v

