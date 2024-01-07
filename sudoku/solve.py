import sys
from PIL import Image, ImageDraw, ImageFont
from sudoku import SudokuBoard, SudokuNode
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
        self.domains = {node: node.get_domain()
                        for node in self.sudoku.get_board()}
    
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
        for i, cell in enumerate(assignment.get_board()):

            # calculate column and row
            # returns a tuple of (floor division, modulus division)
            row, col = divmod(i, 9)

            # Draw new rectangle
            rect = [
                (col * cell_size + cell_border, row * cell_size + cell_border),
                ((col + 1) * cell_size - cell_border, (row + 1) * cell_size - cell_border)
            ]

            draw.rectangle(rect, fill="white")
            _,_, w, h = draw.textbbox((0,0), cell.value, font=font)
            draw.text(
                (rect[0][0] + ((interior_size - w) / 2),
                 rect[0][1] + ((interior_size - h) / 2) - 10),
                 cell.value, fill="black", font=font
            )
        
        img.save(filename)

    def print(self, assignment):
        """
        Print the current assignment to terminal.
        """
        print(" _" * 9)
        counter = 0
        for node in assignment.get_board():
            counter += 1
            print("|", end="")
            print(node.value)
            if counter % 9 == 0:
                print("|")
                print(" _" * 9)
    
    def solve(self):
        """
        Enforce arc consistency, and solve the CSP.
        """
        self.ac3()

        # Create initial assignment dictionary with assigned cells
        assignment = {cell: cell.domain.pop()
                      for cell in self.sudoku if len(self.domain) == 1}

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

            # If only one element remains, value should be int not set
            if isinstance(self.domains[neigh], int):
                revision = True
                self.domains[x].remove(self.domains[neigh])

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

            for cell in self.sudoku.get_board():
                if cell.value != 0:
                    cell_queue.add(cell)

        # Until all cells are dequeued
        while cell_queue:

            cell = cell_queue.pop()

            if self.revise(cell):

                # Problem is insoluble if nothing remains in the domain
                if len(self.domains[cell]) < 1:
                    return False
        
                # Skip enqueing other neighbours when revision occurs
                # Neighbours are already

        return True


    def assignment_complete(self, assignment):
        """
        Returns True if assignment (SudokuBoard) assigns a value to
        every node. Otherwise, False.
        """
        
        # Get all cells from board
        for cell in self.sudoku.get_board():

            # Check that all cells are in dictionary keys
            try:
                assert assignment[cell]
            except AssertionError:
                return False
            
            # Check that all cells have int values
            try:
                assert isinstance(assignment[cell], int)
            except AssertionError:
                return False
            
        return True
    
    def consistent(self, assignment):
        """
        Returns True if assignment (SudokuBoard) has no conflicting
        characters - though may be incomplete. Otherwise, False.
        """

        # Check that each row, column, box sums to 45 or less
        # Check that no recurring values in each row, column, box
        



    def order_domain_values(self, node, assignment):
        """
        Return a list of values in the domain of node sorted by the number
        of values they rule out for neighbouring nodes. The first value
        rules out the fewest values in neighbours.
        """

    def select_unassigned_variable(self, assignment):
        """
        
        """

    def backtrack(self, assignment):
        """
        
        """

    def backtrack_ac3(self, assignment):
        """
        
        """

def main():
    """
    Takes a string of numbers representing a Sudoku board and
    initialises a grid. Then loops until the board is complete.
    Prints the result of checking if the board is correct.
    """
    
    if len(sys.argv) > 2:
        sys.exit("Usage: python sudoku.py [sudoku]")

    # Ingest suduko board
    if sys.argv[1] is None:
        board_string = EXAMPLE

    board_string.strip(" ,[]#")

    # Generate sudoku board
    board = SudokuBoard(board_string)

    # Solve board
    assignment = board.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        assignment.print_board()
        assignment.save()

if __name__ == "__main__":
    main()