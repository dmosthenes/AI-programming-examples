from tictactoe import minimax

def main():
#     test_minimax()
#     return

# def test_minimax():
    EMPTY = None
    empty_board = list()
    for i in range(3):
        empty_board.append([])
        for _ in range(3):
            empty_board[i].append( EMPTY )
    
    assert minimax(empty_board) == 1

if __name__ == "__main__":
    main()

