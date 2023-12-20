# Sudoku solver with inference and backtracking

# Example board
# [8, 5, 0, 0, 0, 2, 4, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 9, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 0, 0, 2, 3, 0, 5, 0, 0, 0, 9, 0, 0 ,0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 7, 0, 0, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 4, 0]

from copy import copy

class SudokuNode:
    """
    Defines a sudoku node with a value from 1 to 9 or 0 if undetermined.
    Lists node's coordinates within grid as a tuple from (0,0) to (8,8).
    Lists possible values in constraints set. Empty set if value == 0.
    Includes empty set to store adjacent nodes.
    """
    def __init__(self, value, coordinates, box):
        self.value = value
        self.coordinates = coordinates
        self.constraints = set()
        self.adjacent = set()
        self.row = coordinates[1]
        self.col = coordinates[0]
        self.box = box

        # If node has an existing value assign it and modify constraints
        if value == 0:
            for i in range (1, 10):
                self.constraints.add(i)
            
    
    def update_constraints(self):
        """
        Updates the node's constraints set according to values of node's adjacent nodes.
        If an adjacent node is non-zero, removes its value from the constraints set.
        If only one value remains in constraints set for a node with value == 0, 
        sets the value of the node to the remaining value in the constraints set.
        """
        # Update list of constraints for the node to eliminate solved adjacent nodes
        for adj in self.adjacent:
            if adj.value != 0:
                self.constraints.remove(adj.value)
        
        # If only one possibility remains, update node's value to index + 1
        if len(self.constraints) == 1:
            self.value = self.constraints.pop()
    
    def add_adjacent(self, adjacents):
        """
        Sets the adjacent nodes field to the given parameter.
        """
        self.adjacent = adjacents

# Take out the sub-lists
class SudokuBoard:
    """
    Defines a sudoku board comprised of 81 nodes for each cell in the board.
    Given a string of 81 numbers without separators, adds 81 SudokuNodes to
    a list, setting each node's value and coordinates from (0,0) to (8,8)
    within the board. Then updates each node in the list to set its adjacent nodes.
    """
    def __init__(self, board):
        self.board = []

        # defines coordinates for top left corner (0,0) to bottom right (8,8)
        node_counter = 0            # tracks the index of the next node
        box_counter = 0             # tracks the current node's box
        for y in range(9):
            # Need to check if box counter should decrement by 3 or add 1
            if y == 3 or y == 6:
                box_counter += 1
            else:
                box_counter -= 3
            for x in range(9):
                node_counter += 1
                if node_counter % 3 == 0:
                    box_counter += 1
                self.board.append(SudokuNode(int(board[0]), (x,y), box_counter))
                board = board[1:]
        
        self.adjacent_loop()
                

    def add_adjacent_nodes(self, target_node):
        """
        Alternative implementation using row, column, box fields in each node.
        """

        adjacent_nodes = set()
        target_row = target_node.row       # Determines the row of the target node
        target_col = target_node.col       # Determines the column of the target node
        target_box = target_node.box

        # Get all nodes for the target row
        # Assume no sub-lists
        for node in self.board:
            if node.row == target_row:
                adjacent_nodes.add(node)
        
        # Get all nodes for the target column
        for node in self.board:
            if node.col == target_col:
                adjacent_nodes.add(node)

        # Get all nodes for the target box
        for node in self.board:
            if node.box == target_box:
                adjacent_nodes.add(node)

        target_node.add_adjacent(adjacent_nodes)

   
    def adjacent_loop(self):
        """
        Calls add_adjacent_node function for each node in the board.
        """
        for sub_list in self.board:
            for node in sub_list:
                self.add_adjacent_nodes(node)
    
    def constraints_loop(self):
        """
        Updates the contrainsts set for each node in the board.
        Return True if constraints of any node are updated, otherwise False.
        """
        updated = False
        for sub_list in self.board:
            for node in sub_list:
                const_before = copy(node.constraints)
                node.update_constraints()
                if const_before != node.constraints:
                    updated = True
        
        return updated
    
    def backtrack(self):
        """
        Recursively selects the most constrained node and sets it to a possible value.
        Then calls the constraints loop function to update adjacent information.
        Continues until the board is complete and correct.
        """

        # Update constraints at start of each layer of recursion
        self.constraints_loop()

        # Base case: board is complete and correct?
        if self.is_complete() and self.is_correct():
            return self.board

        # Recursive bit

        # Search for most constrained node (node with smallest contraints set)
        most_constrained = None
        shortest = 9
        for node in self.board:
            if len(node.constraints) < shortest:
                shortest = len(node.constraints)
                most_constrained = node

        # Loop over available options in the most_constrained node
        for possibility in most_constrained.constraints:

            # Assign the next possibility as the node's value and move down a layer
            most_constrained.value = possibility

            new_board = self.backtrack()

            # Return board if resulting board is still correct
            if new_board.is_complete() and new_board.is_correct():
                return new_board

            # If the new board returned by the lower layer is None,
            # the chosen value is wrong and the loop must continue
            # This occurs automatically


        # At this point in execution, all possible values for the node have been exhausted
        # Return None to backtrack to the previous layer and make a different choice
        return None
    

    def is_complete(self):
        """
        Returns True if all values are non-zero otherwise False.
        """
        for sub_list in self.board:
            for node in sub_list:
                if node.value == 0:
                    return False
        return True
    
    def is_correct(self):
        """
        Alternative implementation. Assume no sub-lists.
        """

        # Check rows
        row_total = set()
        for i in range(9):
            for node in self.board:
                if node.row == i:
                    row_total.add(node.value)
            try:
                assert sum(row_total) == 45
            except AssertionError:
                return False
            row_total = set()

        # Check columns
        col_total = set()
        for i in range(9):
            for node in self.board:
                if node.col == i:
                    col_total.add(node.value)
            try:
                assert sum(col_total) == 45
            except AssertionError:
                return False
            col_total = set()
        
        # Check boxes
        box_total = set()
        for i in range(9):
            for node in self.board:
                if node.box == i:
                    box_total.add(node.value)
            try:
                assert sum(box_total) == 45
            except AssertionError:
                return False
            box_total = set()
        
        return True

    def print_board(self):
        """
        Prints the current values of each node to terminal as a grid.
        """
        print(" _" * 9)
        counter = 0
        for sub_list in self.board:
            for node in sub_list:
                counter += 1
                print("|", end="" )
                print(node.value)
            if counter % 9 == 0:
                print("|")
                print(" _" * 9)


def main():
    """
    Takes a string of numbers representing a Sudoku board and
    initialises a grid. Then loops until the board is complete.
    Prints the result of checking if the board is correct.
    """
    
    # Ingest suduko board
    board_string = input("Enter board:\n")
    board_string.strip(" ,[]#")
    board = SudokuBoard(board_string)

    # Update constraints of each node until all values are resolved
    while not board.is_complete():
        board.print_board()

        # Break loop if no contraints set of any node has changed
        if not board.constraints_loop():
            break
        input("Continue y/n?")
    
    if not board.is_complete():
        # Once all constraints have been updated as much as possible, commence backtracking
        board = board.backtrack()

    print(f"Certified correct: {board.is_correct()} ")

    board.print_board()
    

if __name__ == "__main__":
    main()

# first attempt Sudoku Board method
 # def add_adjacent_nodes(self, target_node):
    #     """
    #     Given a target node, updates the node's adjacent node field with a
    #     set of its 21 adjacent nodes from the row, column, and surrounding
    #     box.
    #     """
    #     adjacent_nodes = set()
    #     target_row = target_node.coordinates[1]       # Determines the row of the target node
    #     target_col = target_node.coordinates[0]       # Determines the column of the target node

    #     # Get adjacent nodes for the row
    #     # Loop over lists to find other nodes in the row

    #     # 0,1,2
    #     # 3,4,5
    #     # 6,7,8
    #     # 9,10,11
    #     # 12,13,14
    #     # 15,16,17
    #     # 18,19,20
    #     # 21,22,23
    #     # 24,25,26

    #     # If in second row, y coordinate is 1, lists 3,4,5 are required
    #     # If in fifth row, y coordinate is 4, lists 12,13,14 are required
    #     # If in ninth row, y coordinate is 8, lists 24,25,26 are required

    #     # Iterate over 3 sub-lists
    #     for i in range(3):
    #         # Select sub-list containing the relevant nodes given the target node's row
    #         for node in self.board[target_row * 3 + i]:
    #             adjacent_nodes.add(node)
    #     assert len(adjacent_nodes) == 9

    #     # Get adjacent nodes for the column

    #     # If in second column, x coordinate is 1, second node of lists 0,3,6,9,12,15,18,21,24 are required (0,1,2)
    #     # If in fifth column, x coordinate is 4, second node of lists 1,4,7,10,13,16,19,22,25 are required (3,4,5)
    #     # If in ninth column, x coordinate is 8, third node of lists 2,5,8,11,14,17,20,23,26 are required (6,7,8)
        
    #     # Define the start column given the target node's column
    #     start = -3 if target_col < 3 else 0 if target_col < 6 else 3
    #     # Iterate over 9 relevant sub-lists
    #     for _ in range(9):
    #         # Select the relevant sub-list and the relevant position within each sub-list
    #         start += 3
    #         adjacent_nodes.add(self.board[start][target_col % 3])
    #     assert len(adjacent_nodes) == 17

    #     # Get adjacent nodes for the box

    #     # Determine row to start search around target node
    #     row_start = 0 if target_row < 3 else 9 if target_row < 6 else 18

    #     # Determine col to start search around target node
    #     col_start = 0 if target_col < 3 else 1 if target_col < 6 else 2

    #     # Index of first sub-list is row_start + col_start

    #     # Iterate over each group of 3 sub-lists
    #     for i in range(3):
    #         # Iterate over each node in the relevant sub-list
    #         for node in self.board[row_start + col_start + (3 * i)]:
    #             adjacent_nodes.add(node)
    #     assert len(adjacent_nodes) == 21

    #     adjacent_nodes.remove(target_node.coordinates)
    #     target_node.add_adjacent(adjacent_nodes)

        # Generate nine adjacency boxes
    # Possible boxes: 
        # [0,0] - [2,2], [3,0] - [5,2], [6,0] - [8,2]
        # [0,3] - [2,5], [3,3] - [5,5], [6,3] - [8,5]
        # [0,6] - [2,8], [3,6] - [5,8], [6,6] - [8,8]

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
