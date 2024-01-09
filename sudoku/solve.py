import sys
from PIL import Image, ImageDraw, ImageFont
from sudoku import SudokuBoard
import copy

EXAMPLE = "8, 5, 0, 0, 0, 2, 4, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 9, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 0, 0, 2, 3, 0, 5, 0, 0, 0, 9, 0, 0 ,0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 7, 0, 0, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 4, 0"
INTERLEAVING = False

class SudokuSolve():
    """
    Methods to take a given SudokuBoard comprised of SudokuNodes
    and solve it.
    """

    def __init__(self, sudoku):
        """
        Create new CSP sudoku solve.
        """
        self.sudoku = sudoku
        self.domains = {cell: cell.get_domain()
                        for cell in self.sudoku.get_board()}
    
    def save(self, assignment, filename="output.png"):
        """
        Save sudoku to image file.
        """

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        
        # Create a new image with sudoku dimensions
        img = Image.new(
            "RGBA",
            (9 * cell_size,
             9 * cell_size),
             "black"
        )

        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        # Loop over each cell in the board
        for i, cell in enumerate(self.sudoku.get_board()):

            # calculate column and row
            # returns a tuple of (floor division, modulus division)
            row, col = divmod(i, 9)

            # Draw new rectangle
            rect = [
                (col * cell_size + cell_border, row * cell_size + cell_border),
                ((col + 1) * cell_size - cell_border, (row + 1) * cell_size - cell_border)
            ]

            draw.rectangle(rect, fill="white")
            _,_, w, h = draw.textbbox((0,0), str(assignment[cell]), font=font)
            draw.text(
                (rect[0][0] + ((interior_size - w) / 2),
                 rect[0][1] + ((interior_size - h) / 2) - 10),
                 str(assignment[cell]), fill="black", font=font
            )
        
        img.save(filename)

    def print(self, assignment):
        """
        Print the current assignment to terminal.
        """
        print("   _ " * 9)
        counter = 0
        for cell in self.sudoku.get_board():
            counter += 1
            print("|", end="")
            print(" ", assignment[cell], end=" ")
            if counter % 9 == 0:
                print("|")
                print("   _ " * 9)
    
    def solve(self):
        """
        Enforce arc consistency, and solve the CSP.
        """
        self.ac3()

        # Create initial assignment dictionary with assigned cells
        assignment = {cell: copy.copy(self.domains[cell]).pop()
                      for cell in self.sudoku.get_board() if len(self.domains[cell]) == 1}

        if not INTERLEAVING:
            return self.backtrack(assignment)
        else:
            return self.backtrack_ac3(assignment)
    
    def revise(self, x):
        """
        Make node 'x' arc consistent with its neighbours.
        Returns True revision occurs, otherwise False.

        Does not assign values even if only one in domain.
        """
        
        revision = False
        for neigh in x.neighbours:

            # If only one element remains, assign
            value = copy.copy(self.domains[neigh]).pop() if len(self.domains[neigh]) == 1 else None

            # Check if value present in x domain (it may have been revised already)
            if value in self.domains[x]:

                revision = True
                self.domains[x].remove(value)

        return revision


    def ac3(self, cells=None):
        """
        Update self.domains such that each cell is arc consistent.
        If cells is None, begin with all cells. Otherwise, use cells
        as the initial list of cells to make consistent.

        Returns True if arc consistency is enforced and no domains
        are empty. Return False if any domains end up empty.
        """

        cell_queue = set()

        if cells is not None:

            for cell in cells:
                cell_queue.add(cell)

        else:

            # Loop over each cell on the board
            for cell in self.sudoku.get_board():

                # Add cells which are not already asigned
                # try:
                if len(self.domains[cell]) > 1:
                    cell_queue.add(cell)
                # except KeyError:

                    # print(len(self.domains))

                    # cell.print()
                    # for c in self.domains.keys():
                    #     c.print()

                    # print(cell in self.domains)

                    # quit()

        # Until all cells are dequeued
        while cell_queue:

            cell = cell_queue.pop()

            if self.revise(cell):

                # Problem is insoluble if nothing remains in the domain
                if self.domains[cell] == set():
                    return False
        
                # Enqueue neighbours if revision was made
                for neigh in cell.neighbours:

                    # Add if neighbour is not already asssigned
                    if len(self.domains[neigh]) > 1:
                        cell_queue.add(neigh)

        return True


    def assignment_complete(self, assignment):
        """
        Returns True if assignment (SudokuBoard) assigns a value to
        every node. Otherwise, False.
        """
        
        # Get all cells from board
        for cell in self.sudoku.get_board():

            # Check that all cells are in dictionary keys
            if cell not in assignment:
                return False
            # try:
            #     assert assignment[cell]
            # except KeyError:
            #     return False
            
            # Check that all cells have int values
            # try:
            # assert isinstance(assignment[cell], int)
            # except TypeError:
            #     return False
            
        return True
    
    def consistent(self, assignment):
        """
        Returns True if assignment (SudokuBoard) has no conflicting
        characters - though may be incomplete. Otherwise, False.
        """

        # Check that each row, column, box sums to 45 or less
        # Check that no recurring values in each row, column, box

        # rows
        for row in range(9):
            row_items = []
            for cell in assignment.keys():
                # Check if cell belongs to current row
                if cell.row == row:
                    # Add value to list if assigned
                    if cell in assignment:
                        row_items.append(assignment[cell])
            # Check that sum is less than or equal to 45
            if not sum(row_items) <= 45:
                return False
            # Check that all items are unique
            if any(row_items.count(item) > 1 for item in row_items):
                return False
        
        # cols
        for col in range(9):
            col_items = []
            for cell in assignment.keys():
                # Check if cell belongs to current col
                if cell.col == col:
                    # Add value to list if domain is resolved
                    if cell in assignment:
                        col_items.append(assignment[cell])
            # Check that sum is less than or equal to 45
            if not sum(col_items) <= 45:
                return False
            # Check that all items are unique
            if any(col_items.count(item) > 1 for item in col_items):
                return False

        # boxes
        for box in range(9):
            box_items = []
            for cell in assignment.keys():
                # Check if cell belongs to current box
                if cell.box == box:
                    # Add value to list if domain is resolved
                    if cell in assignment:
                        box_items.append(assignment[cell])
            # Check that sum is less than or equal to 45
            if not sum(box_items) <= 45:
                return False
            # Check that all items are unique
            if any(box_items.count(item) > 1 for item in box_items):
                return False
            
        return True


    def order_domain_values(self, cell):
        """
        Return a list of values in the domain of node sorted by the number
        of values they rule out for neighbouring nodes. The first value
        rules out the fewest values in neighbours.
        """

        least_constraining = {value: 0
                              for value in self.domains[cell]}

        # Loop over the values in cell's domain
        for value in least_constraining.keys():

            # Loop over each neighbouring cell
            for neigh in cell.neighbours:

                # Update least_constraining dictionary if value is present
                if value in self.domains[neigh]:

                    least_constraining[value] += 1

        # Return sorted list
        return sorted([item for item in least_constraining.keys()], key=lambda x: least_constraining[x])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned cell not already assigned in assignment.
        Choose the cell with the minimum number of remaining values
        in its domain. In the case of a tie, choose randomly.
        """

        unassigned = {cell: len(self.domains[cell])
                      for cell in self.sudoku.get_board()
                      if cell not in assignment or 
                      not isinstance(assignment[cell], int)}
        
        # return sorted unassigned values
        return sorted([item for item in unassigned.keys()], key=lambda x: unassigned[x])[0]


    def backtrack(self, assignment):
        """
        Perform backtracking search to return a complete assignment dictionary.
        """

        # Base case: all values assigned correctly
        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        
        # Recursive bit

        # Choose the next cell to assign
        cell = self.select_unassigned_variable(assignment)

        # Loop over ordered domain values
        for value in self.order_domain_values(cell):

            # Assign value and continue
            assignment[cell] = value

            if self.consistent(assignment):

                result = self.backtrack(assignment)
                if result:
                    return result
                
            del assignment[cell]

        return None
        

    def backtrack_ac3(self, assignment):
        """
        Perform backtracking serach with inferences to return a complete assignment
        dictionary.
        """

        # Base case: assignment is complete and consistent
        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        
        # Recursive bit
        print(f"Assigned: {len(assignment)}")

        # Pick a new cell to assign
        cell = self.select_unassigned_variable(assignment)

        # Take a copy of the domains
        copied_domains = copy.copy(self.domains)

        # Loop over each available value for the given cell
        for value in self.order_domain_values(cell):

            # Assign the current value
            assignment[cell] = value

            # Continue if not consistent
            if self.consistent(assignment):

                # Update the current cell's domain
                self.domains[cell] = {value}

                # Check for any new inferences and revisions
                self.ac3()

                # Store result of backtracking
                result = self.backtrack_ac3(assignment)
                if result:
                    return result
            
            # Undo assignment
            del assignment[cell]

            # Remove inferences
            self.domains = copied_domains
        
        return None

def main():
    """
    Takes a string of numbers representing a Sudoku board and
    initialises a grid. Then loops until the board is complete.
    Prints the result of checking if the board is correct.
    """
    
    if len(sys.argv) > 2:
        sys.exit("Usage: python solve.py [sudoku]")

    # Ingest suduko board
    if len(sys.argv) < 2:
        board_string = EXAMPLE

    board_string = board_string.replace(",","").replace(" ","")
    print(board_string)

    # Generate sudoku board
    board = SudokuBoard(board_string)

    # Create new SudokuSolve object
    solver = SudokuSolve(board)

    assignment = solver.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        solver.print(assignment)
        solver.save(assignment)

if __name__ == "__main__":
    main()