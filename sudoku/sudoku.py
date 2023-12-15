# Sudoku solver with inference and backtracking

# Example board
# [8, 5, 0, 0, 0, 2, 4, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 9, 0, 0, 
# 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 0, 0, 2, 3, 0, 5, 0, 
# 0, 0, 9, 0, 0 ,0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 
# 0, 7, 0, 0, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 4, 0]


# Create sudoku node object
# Has field of nine boolean values, representing known illegal values and possible values
# Solved boolean field, indicating whether node is solved
# Update method - updates possible values of node given relevant adjacent nodes
    # Method takes node and adjacent node values (constraints) as input
class SudokuNode:
    """

    """
    def __init__(self, value, coordinates):
        # self.constraints = [True for i in range(9)]
        self.value = value
        self.coordinates = coordinates
        self.constraints = set()

        # If node has an existing value assign it and modify constraints
        if value == 0:
            # self.constraints = [False for i in range(9)]
            # self.constraints[value] = True
            # self.constraints = None
        # else:
            for i in range (1, 10):
                self.constraints.add(i)
            
    
    def update_node(self, adjacent_nodes):
        """
        
        """
        # Update list of constraints for the node to eliminate solved adjacent nodes
        for adj in adjacent_nodes:
            if adj.value != 0:
                self.constraints.remove(adj.value)
        
        # If only one possibility remains, update node's value to index + 1
        if len(self.constraints) == 1:
            self.value = self.constraints.pop()


# Create sudoku board object
# Has field of list of 81 nodes for each space of board
# Get relevant adjacent nodes method returns all relevant nodes for a given node
# from each row, column, and box
class SudokuBoard:
    """

    """
    def __init__(self, board):
        self.board = []

        # defines coordinates for top left corner (0,0) to bottom right (8,8)
        # board is list of 27 lists of 3 nodes
        counter = 0
        for y in range(9):
            for x in range(9):
                counter += 1
                if counter % 3 == 0:
                    self.board.append(list())
                self.board[-1].append(SudokuNode(board[0], (x,y)))
                board = board[1:]
        
        # Generate nine adjacency boxes
        # Possible boxes: 
            # [0,0] - [2,2], [3,0] - [5,2], [6,0] - [8,2]
            # [0,3] - [2,5], [3,3] - [5,5], [6,3] - [8,5]
            # [0,6] - [2,8], [3,6] - [5,8], [6,6] - [8,8]
                

    def get_adjacent_nodes(self, target_node):
        adjacent_nodes = set()
        target_row = target_node.coordinates[1]       # Determines the row of the target node
        target_col = target_node.coordinates[0]       # Determines the column of the target node

        # Get adjacent nodes for the row
        # Loop over lists to find other nodes in the row

        # 0,1,2
        # 3,4,5
        # 6,7,8
        # 9,10,11
        # 12,13,14
        # 15,16,17
        # 18,19,20
        # 21,22,23
        # 24,25,26

        # If in second row, y coordinate is 1, lists 3,4,5 are required
        # If in fifth row, y coordinate is 4, lists 12,13,14 are required
        # If in ninth row, y coordinate is 8, lists 24,25,26 are required

        # Iterate over 3 sub-lists
        for i in range(3):
            # Select sub-list containing the relevant nodes given the target node's row
            for node in self.board[target_row * 3 + i]:
                adjacent_nodes.add(node)
        assert len(adjacent_nodes) == 9

        # for node in self.board:
        #     if node.coordinates[1] == target_node.coordinates[1]:
        #         adjacent_nodes.add(node)

        # Get adjacent nodes for the column

        # If in second column, x coordinate is 1, second node of lists 0,3,6,9,12,15,18,21,24 are required (0,1,2)
        # If in fifth column, x coordinate is 4, second node of lists 1,4,7,10,13,16,19,22,25 are required (3,4,5)
        # If in ninth column, x coordinate is 8, third node of lists 2,5,8,11,14,17,20,23,26 are required (6,7,8)
        
        # Define the start column given the target node's column
        start = -3 if target_col < 3 else 0 if target_col < 6 else 3
        # Iterate over 9 relevant sub-lists
        for _ in range(9):
            # Select the relevant sub-list and the relevant position within each sub-list
            start += 3
            adjacent_nodes.add(self.board[start][target_col % 3])
        assert len(adjacent_nodes) == 17

        # Get adjacent nodes for the box

        # Determine row to start search around target node
        row_start = 0 if target_row < 3 else 9 if target_row < 6 else 18

        # Determine col to start search around target node
        col_start = 0 if target_col < 3 else 1 if target_col < 6 else 2

        # Index of first sub-list is row_start + col_start

        # Iterate over each group of 3 sub-lists
        for i in range(3):
            # Iterate over each node in the relevant sub-list
            for node in self.board[row_start + col_start + (3 * i)]:
                adjacent_nodes.add(node)
        assert len(adjacent_nodes) == 21

        adjacent_nodes.remove(target_node.coordinates)
        return adjacent_nodes

def main():

    # Ingest suduko board
    # Create new sudoku board object full of sudoku nodes
    return None

if __name__ == "__main__":
    main()

    #    self.adj_boxes = []

    #     self.top_left = set()
    #     for i in range(3):
    #         for j in range(3):
    #             self.top_left.add(i,j)
    #     assert len(self.top_left) == 9
    #     self.adj_boxes.append(self.top_left)

    #     self.top_mid = set()
    #     for i in range(3,6):
    #         for j in range(3):
    #             self.top_mid.add(i,j)
    #     assert len(self.top_mid) == 9
    #     self.adj_boxes.append(self.top_mid)
        
    #     self.top_right = set()
    #     for i in range(6,9):
    #         for j in range(3):
    #             self.top_right.add(i,j)
    #     assert len(self.top_right) == 9
    #     self.adj_boxes.append(self.top_right)

    #     self.mid_left = set()
    #     for i in range(3):
    #         for j in range(3,6):
    #             self.mid_left.add(i,j)
    #     assert len(self.mid_left) == 9
    #     self.adj_boxes.append(self.mid_left)
        
    #     self.mid_mid = set()
    #     for i in range(3,6):
    #         for j in range(3,6):
    #             self.mid_mid.add(i,j)
    #     assert len(self.mid_mid) == 9
    #     self.adj_boxes.append(self.mid_mid)
        
    #     self.mid_right = set()
    #     for i in range(6,9):
    #         for j in range(3,6):
    #             self.mid_right.add(i,j)
    #     assert len(self.mid_right) == 9
    #     self.adj_boxes.append(self.mid_right)

    #     self.bot_left = set()
    #     for i in range(3):
    #         for j in range(6,9):
    #             self.bot_left.add(i,j)
    #     assert len(self.bot_left) == 9
    #     self.adj_boxes.append(self.bot_left)
        
    #     self.bot_mid = set()
    #     for i in range(3,6):
    #         for j in range(6,9):
    #             self.bot_mid.add(i,j)
    #     assert len(self.bot_mid) == 9
    #     self.adj_boxes.append(self.bot_mid)
        
    #     self.bot_right = set()
    #     for i in range(6,9):
    #         for j in range(6,9):
    #             self.bot_right.add(i,j)
    #     assert len(self.bot_right) == 9
    #     self.adj_boxes.append(self.bot_right)    
