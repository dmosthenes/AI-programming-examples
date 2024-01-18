import sys
from PIL import Image, ImageDraw, ImageFont
from sudoku import SudokuBoard
import copy
import termcolor

EXAMPLE = "8, 5, 0, 0, 0, 2, 4, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 9, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 0, 0, 2, 3, 0, 5, 0, 0, 0, 9, 0, 0 ,0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 7, 0, 0, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 4, 0"
EXAMPLE2 = "010020300004005060070000008006900070000100002030048000500006040000800106008000000"
EXAMPLE3 = "070050800005008020010000009008100050000200001090034000900002030000600107006000000"
EXAMPLE4 = "000943000060010050000000000800000003750060014100000009000000000020050080000374000"
EXAMPLE5 = "000123000040050060000000000700000003460080052500000001000000000070060040000394000"
EXAMPLE6 = "000028500000700000902005700403000070700010008050000603006200904000006000004150000"
EXAMPLE7 = "000000000001203400020040050060000040007030100050000080080050060003908200000000000"
EXAMPLE8 = "070040800009005060060000003004100070000200006020034000100008090000600401007000000"
EXAMPLE9 = "070060900006002030020000006003100040000200008050034000900003020000700105008000000"
EXAMPLE10 = "000000000070102030000345000031000740002080300059000210000794000010206090000000000"
EXAMPLE11 = "010000020002000300000405000006040200070000010005060800000901000004000600090000070"
EXAMPLE12 = "0500700830040000600000500008306000000009001000000000005070004000003020001000000000"

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
    
    def print_domain_board(self, x):
        """
        Prints the board as defined by current domains.
        """

        print("   _ " * 9)
        counter = 0

        for cell in self.sudoku.get_board():
            counter += 1
            print("|", end="")

            # Print cell in green if it is the target cell
            if x.__eq__(copy.copy(self.domains[cell]).pop()):
                print(" ", end="")
                termcolor.cprint(copy.copy(self.domains[cell]).pop(),"green", end=" ")

            # When cell is a neighbour of target cell
            elif cell in x.neighbours:
                
                # When cell is a neighbour with an assigned value
                if len(self.domains[cell]) == 1:
                    print(" ", end="")
                    termcolor.cprint(copy.copy(self.domains[cell]).pop(),"red", end=" ")

                # When cell is a neighbour with an unassigned value
                else:
                    print(" ", end="")
                    termcolor.cprint("0","red", end=" ")
            
            # When cell is not target or neighbour but is assigned
            elif len(self.domains[cell]) == 1:
                print(" ", copy.copy(self.domains[cell]).pop(), end=" ")
            
            # When cell is not target, neighbour, and is not assigned
            else:
                print(" ", "0", end=" ")

            if counter % 9 == 0:
                print("|")
                print("   _ " * 9)

    def print_domains(self, x=None):
        """
        Prints the self.domains dictionary, highlighting selected cell
        and neighbours.
        """

        if x:
        # Print target term, if there is one
            termcolor.cprint(f"Current cell: {x}: {self.domains[x]}", "green")

        # Loop over domains dictionary
        for cell, values in self.domains.items():

            # Print cells
            if cell.__eq__(x):
                termcolor.cprint(f"{cell}: {values}", "green", end=", ")
            elif cell in x.neighbours and len(values) == 1:
                termcolor.cprint(f"{cell}: {values}", "red", end=", ")
            else:
                print(f"{cell}: {values}", end=", ")
        
        print("\n\n")


    def solve(self):
        """
        Enforce arc consistency, and solve the CSP.
        """
        
        global INTERLEAVING
        
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

    def ac3(self, cell_prime=None):
        """
        Update self.domains such that each cell is arc consistent.
        If cells is None, begin with all cells. Otherwise, use cells
        as the initial list of cells to make consistent.

        Returns True if arc consistency is enforced and no domains
        are empty. Return False if any domains end up empty.
        """

        cell_queue = set()

        if cell_prime is not None:

            for neigh in cell_prime.neighbours:
                cell_queue.add(neigh)

        else:

            # Loop over each cell on the board
            for cell in self.sudoku.get_board():

                # Add cells which are not already asigned
                if len(self.domains[cell]) > 1:
                    cell_queue.add(cell)

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
    
    def ac3_again(self, cell_prime):

        # Create a queue of cells to check against their neighbours' domains
        cell_queue = set()

        # Add cell_prime and its neighbors to the queue
        cell_queue.add(cell_prime)
        cell_queue.update(cell_prime.neighbours)

        # Process the queue until it's empty
        while cell_queue:
            cell = cell_queue.pop()

            # Check if the domains of the cell can be updated
            if self.revise(cell):

                # Check that the domain is not empty
                if self.domains[cell] == set():
                    # Terminate early if domain is empty, undoing changes
                    return False

                # Enqueue cell's neighbors if there was a revision
                # Skip any cells which are already length 1
                cell_queue.update({neigh for neigh in cell.neighbours if len(self.domains[neigh]) > 1})

        return True

    def backtrack(self, assignment):
        """
        Perform backtracking search to return a complete assignment dictionary.
        """

        # Base case: all values assigned correctly
        if self.assignment_complete(assignment) and self.consistent(assignment):
            return assignment
        
        # Recursive bit
        print(f"Assigned: {len(assignment)}")

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
        copied_domains = copy.deepcopy(self.domains)

        # Loop over each available value for the given cell
        for value in self.order_domain_values(cell):

            # Assign the current value
            assignment[cell] = value

            # Continue if not consistent
            if self.consistent(assignment):

                # Update the current cell's domain
                self.domains[cell] = {value}

                # Check for any new inferences and revisions in cell's neighbours
                # if self.ac3_again(cell):
                self.ac3_again(cell)

                # Store result of backtracking
                result = self.backtrack_ac3(assignment)
                if result is not None:
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
    
    global INTERLEAVING

    if len(sys.argv) > 3:
        sys.exit("Usage: python solve.py [interleaving] [sudoku]")

    # Ingest suduko board
    if len(sys.argv) < 3:
        board_string = EXAMPLE12
    
    # Set interleaving
    if len(sys.argv) == 2:

        if sys.argv[1] == "True":
            INTERLEAVING = True
        elif sys.argv[1] == "False":
            INTERLEAVING = False

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