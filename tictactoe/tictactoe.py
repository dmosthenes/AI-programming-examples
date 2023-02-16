"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


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

    x_count = 0
    o_count = 0
    for i in range(3):
        for j in range (3):
            if board[i][j] == "X":
                x_count += 1
            elif board[i][j] == "O":
                o_count += 1
            else:
                continue
    
    if o_count < x_count:
        return O
    else:
        return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """

    possible = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] is None:
                possible.add((i,j))
    return possible


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """

    b = board
    b[action[0]][action[1]] = player(board)
    return b


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # Check horizontals
    for i in range(3):
        if all(board[i]):
            return board[i][0]
    
    # Check verticals
    for i in range(3):
        vert = []
        for j in range(3):
            vert[j] = board[i][j]
        if all(vert):
            return vert[0]

    # Check diagonals
    right = [board[0][0], board[1][1], board[2][2]]
    left = [board[0][2], board[1][1], board[2][0]]

    if all(right):
        return right[0]
    elif all(left):
        return left[0]
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    else:
        for i in range(3):
            for j in range(3):
                if board[i][j] is EMPTY:
                    return False
        return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    w = winner(board)
    if w == X:
        return 1
    elif w == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
