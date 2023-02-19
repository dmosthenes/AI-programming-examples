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
        if all(x == board[i][0] for x in board):
            return board[i][0]
    
    # Check verticals
    for i in range(3):
        vert = []
        for j in range(3):
            vert.append(board[j][i])
        if all(x == vert[0] for x in vert):
            return vert[0]

    # Check diagonals
    right = [board[0][0], board[1][1], board[2][2]]
    left = [board[0][2], board[1][1], board[2][0]]

    if all(x == right[0] for x in right):
        return right[0]
    elif all(x == left[0] for x in left):
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

    # Base case: terminal board
    if terminal(board):
        return utility(board)

    # Recursive bit: rank lists of actions, choosing min or max
    results = []
    # Get player
    if player(board) == X:
        # Get actions for max player
        max_actions = actions(board)
        # Choose the max value action
        for action in max_actions:
            # Evaluate each action
            max_board = result(board, action)
            results.append((minimax(max_board), action))
        return sorted(results)[0][1]
    else:
        # Get actions for min player
        min_actions = actions(board)
        # Choose the min value action
        for action in min_actions:
            # Evaluate each action
            min_board = result(board, action)
            results.append((minimax(min_board), action))
        print(results)
        return sorted(results)[-1][1]



#     # Return None if game over
#     if terminal(board):
#         return None

#     # Rank each move -1 to 1
#     moves = []
#     for action in actions(board):
#         moves.append((minimax_helper(board, action, 0), action))
    
#     # Pick optimal move
#     # Check if min or max turn
#     if player(board) == X:
#         moves = sorted(moves)
#         return moves[0][1]
#     else:
#         moves = sorted(moves, reverse=True)
#         return moves[-1][1]

# def minimax_helper(board, action, total):
#     """
#     Returns a tuple (x, y) where x is the minimax value and y is the coordinate (i, j)
#     """
#     # Base case: terminal board
#     if terminal(board):
#         return utility(board)

#     # Recursive bit: Loop over all moves next player can make
#     next_board = result(board, action)
#     next_actions = actions(next_board)
#     for next_action in next_actions:
#         return total += minimax_helper(next_board, next_action, total)

