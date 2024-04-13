import pygame
from tile_and_board import Square, TileCreator, Board, opposite
import os
import copy
import time
import random
import copy
import cProfile

class WaveFunctionCollapse():

    def __init__(self, tiles, width, height, board):

        self.tiles = tiles
        self.window_width = width
        self.window_height = height
        self.numbered_tiles = board.numbered_tiles
        self.board = board
        self.latest_assignment = None
        self.side_length = (self.window_width / self.board.rows)

        self.domains = {square.coordinates : self.tiles
                for square in board.squares}
        
        self.viewer = pygame.init()
        self.window = pygame.display.set_mode((self.window_width, self.window_height))

        pygame.display.set_caption("Wave Function Collapse Visualisation")

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

    def run(self):

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.window.fill(self.BLACK)

            pygame.display.flip()

            assignment = self.solve()

            if self.complete(assignment) is True:
                input("Close?")
                running = False
        
        pygame.quit()


    def update_window(self, latest_assignment, assignment, delete=False):

        if delete:

            (i,j) = latest_assignment
            pygame.draw.rect(self.window, self.BLACK, (i * self.side_length, j * self.side_length,
                                                        self.numbered_tiles[0].width, self.numbered_tiles[0].width))

        else:
            (i,j) = latest_assignment
            tile = assignment[(i,j)]

            scaled_surface = pygame.transform.scale(tile.surface, (self.side_length, self.side_length))

            self.window.blit(scaled_surface, (i * self.side_length, j * self.side_length))

            pygame.display.flip()


    def solve(self):
        """
        Enforce arc consistency, and solve the CSP.
        """

        assignment = {}

        # Make an initial random assignment in or around the middle
        # middle_square = Square(round(self.board.rows / 2), round(self.board.cols / 2), self.board.cols, self.board.rows)
        # middle_square = (round(self.board.rows / 2), round(self.board.cols / 2))
        middle_square = random.randint(0,self.board.rows -1), random.randint(0,self.board.cols -1)

        assignment[middle_square] = self.domains[middle_square].pop()
        self.domains[middle_square] = set()
        self.domains[middle_square].add(assignment[middle_square])

        # self.update_window(assignment)

        self.ac3([s for s in assignment.keys()])

        # if not INTERLEAVING:
        #     self.backtrack(assignment)
        # else:
        self.backtrack_with_interleaving(assignment, middle_square)

        return assignment


    def ac3(self, squares):
        """
        Only checks arc consistency for Squares which are assigned.

        Update self.domains such that each square is arc consistent.

        Returns True if arc consistency is enforced and no domains
        are empty. Return False if any domains end up empty.
        """
        
        # Create queue of squares
        squares_queue = squares

        while squares_queue:

            # Take the top square
            square = squares_queue[0]
            squares_queue = squares_queue[1:]

            # Check for inferences
            if self.revise(square):

                # Check that domain is not empty
                if not self.domains[square] or len(self.domains[square]) == 0:
                    return False
                
                # Enqueue further neighbours
                squares_queue.extend([neigh for neigh in self.board.squares[square[0] * self.board.rows + square[1]].neighbours.values()])

        return True
    

    def ac3_deprecated(self, squares):

        # Create arc queue of tuples between each square and each of its neighbours
        arc_queue = {(square, neighbour) for square in squares 
                     for neighbour in self.board[square[0] * self.board.rows + square[1]].neighbours.values()}
        
        while arc_queue:

            # Take the top element and check for arc consistency
            square, neigh = arc_queue.pop()
            if self.revise(square, neigh):

                # If changes were made, check if domain is empty
                if not self.domains[square]:

                    return False
                
                # Enqueue further neighbours
                arc_queue.add((new_neigh, square) for new_neigh 
                              in self.board[square[0] * self.board.rows + square[1]].neighbours.values() if new_neigh != neigh)
                
                
        return True


    def revise(self, x):
        """
        Modify the domains of x's neighbours to be consistent with the value of x
        if x is assigned (length is 1).
        """
        
        if len(self.domains[x]) != 1:
            return False

        revision = False
        
        # Get x Square object
        x_square = self.board.squares[x[0] * self.board.rows + x[1]]
        
        # Get x's neighbours
        for side, neigh_square in x_square.neighbours.items():

            # Create the neighbouring square
            # neigh_square = Square(i,j,self.board.cols,self.board.rows)

            # Get compatible tiles for x on given side
            compat_tiles_num = copy.copy(self.domains[x]).pop().compatible_tiles[side]

            compat_tiles = {self.numbered_tiles[t] for t in compat_tiles_num}
            
            # Get the overlap between the compatible tiles and the neighbour
            overlap = compat_tiles.intersection(self.domains[neigh_square])

            # Update the neighbouring domain if it is different
            if overlap != self.domains[neigh_square]:
                self.domains[neigh_square] = overlap
                revision = True

        return revision


    def complete(self, assignment):
        """Returns True if assignment assigns a value to
        every Square on the Board. Otherwise, False."""

        # Check that each square in the domains dictionary maps to a tile.
        for square in self.domains.keys():
            # if square not in assignment or assignment[square] == set():
            if square not in assignment.keys():
                return False

        return True
    

    def consistent(self, assignment):
        """
        Returns True if assignment has no conflicting
        tiles - though may be incomplete. Otherwise, False.
        """

        # sides = ["top", "right", "bottom", "left"]

        # Iterate over the assignment dictionary
        for (i,j), tile in assignment.items():

            # Check that each neighbour that is assigned is a compatible tile
            neighbours = self.board.squares[i * self.board.rows + j].neighbours

            for side in neighbours.keys():

                neigh_square = neighbours[side]

                # Convert combatible tiles from numbers
                compat_tiles = {self.numbered_tiles[c] for c in tile.compatible_tiles[side]}

                # neigh_square = Square(i, j, self.board.cols, self.board.rows)
                if neigh_square in assignment:
                    if assignment[neigh_square] not in compat_tiles:
                        return False

        return True
    

    def backtrack(self, assignment):
        """
        Perform backtracking search to return a complete assignment dictionary.
        """

        # Base case
        if self.complete(assignment) and self.consistent(assignment):
            return assignment
        
        # Update visualisation
        time.sleep(0.1)
        self.update_window(self.latest_assignment, assignment)
        
        # Recursive bit

        # Select an unassigned square
        square = self.select_unassigned_variable(assignment)
        tiles = self.order_domain_values(square)

        # Iterate over possible values
        for tile in tiles:

            assignment[square] = tile

            self.latest_assignment = square

            if self.consistent(assignment):

                self.domains[square] = set()
                self.domains[square].add(tile)

                # Check that each assigned variable has len 1 in domain
                # for s in assignment.keys():

                #     assert len(self.domains[s]) == 1

                result = self.backtrack(assignment)
                if result:
                    return result
            
            del assignment[square]

        return None
    

    def backtrack_with_interleaving(self, assignment, latest_assignment):
        """
        Perform backtracking serach with inferences to return a complete assignment
        dictionary.
        """

        # Update visualisation
        self.update_window(latest_assignment, assignment)

        # Base case
        if self.complete(assignment) and self.consistent(assignment):
            return assignment
        
        # Select an unassigned square
        square = self.select_unassigned_variable(assignment)
        tiles = self.order_domain_values(square)

        # domains_copy = copy.deepcopy(self.domains)
        domains_copy = self.domains.copy()

        # Iterate over possible values
        for tile in tiles:

            assignment[square] = tile

            if self.consistent(assignment):

                self.domains[square] = set()
                self.domains[square].add(tile)

                # Make inferences
                if not self.ac3([s for s in assignment.keys()]):
                    continue

                result = self.backtrack_with_interleaving(assignment, square)
                if result:
                    assignment = result
                    return result
                
            del assignment[square]
            self.domains = domains_copy
            self.update_window(square, assignment, True)

        return None

    def select_unassigned_variable_random(self, assignment):
        """
        Pick random Square and return a neighbour not in assignment.
        """

        for i,j in assignment.keys():
            
            neighbours = list(self.board.squares[i * self.board.rows + j].neighbours.values())

            # neighbours = list(square.neighbours.values())
            random.shuffle(neighbours)

            for neigh_square in neighbours:

                # neigh_square = Square(i,j,self.board.cols,self.board.rows)

                if neigh_square not in assignment:

                    return neigh_square


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned Square not already assigned in assignment.
        Choose the cell with the minimum number of remaining values
        in its domain. In the case of a tie, choose randomly.
        """

        # Get dictionary of Squares which are neighbours to assignment
        unassigned_list = []

        # Each square has an assigned tile
        for (i,j) in assignment.keys():

            neighbours = set()

            # Get neighbouring squares
            for neigh_square in self.board.squares[i * self.board.rows + j].neighbours.values():

                # Create neighbour square
                # neigh_square = (Square(i, j, self.board.cols, self.board.rows))

                neighbours.add((neigh_square, len(self.domains[neigh_square])))

            unassigned_list.extend([n for n in neighbours if n[0] not in assignment.keys()])

        return sorted(unassigned_list, key=lambda x: x[1])[0][0]
    

    def order_domain_values(self, square):
        """
        Return a list of values in the domain of Square sorted by the number
        of values they rule out for neighbouring Squares. The first value
        rules out the fewest values in neighbours.
        """

        available_tiles = self.domains[square]
        neighbours = self.board.squares[square[0] * self.board.rows + square[1]].neighbours

        # out = [tile for tile in available_tiles]
        # random.shuffle(out)
        # return out

        values = []

        # code for returning values sorted by ruling out the fewest first
        for tile in available_tiles:

            total = 0

            # For each neighbour, consider how many tiles fit if the
            # current tile was selected
            for side in neighbours.keys():

                current_square = neighbours[side]

                # current_square = Square(i, j, self.board.cols, self.board.rows)

                # This is a set of Tile
                possible_tiles = self.domains[current_square]

                # This is a set of Int
                compat_tiles_ints = tile.compatible_tiles[side]

                # Convert to a set of Tile
                compat_tiles = {self.numbered_tiles[tile] for tile in compat_tiles_ints}

                overlap = possible_tiles.intersection(compat_tiles)

                total += len(overlap)

            values.append((tile, total))

        # Return the sorted list
        out = [x[0] for x in sorted(values, key=lambda x:x[1], reverse=True)]
        random.shuffle(out)
        return out


def main():

    # time.sleep(5)

    width = 800
    height = 800

    rows = 20
    cols = 20

    # self.scaling_factor = (self.window_width / self.board.rows) / self.numbered_tiles[0].width

    tile_set = random.choice([dir for dir in os.listdir("images")])
    

    side_length = round(width / rows)

    # Create a TileCreator
    tile_maker = TileCreator(os.path.join("images", tile_set), side_length, True)
    tiles = tile_maker.generate_tiles()

    # Get tile numbers
    numbered_tiles = tile_maker.numbered_tiles

    # Initialise the board
    # Set the number of rows and columns
    board = Board(rows, cols, tiles, numbered_tiles)

    quit

    # Set the window resolution
    wfc = WaveFunctionCollapse(tiles, width, height, board)

    wfc.run()


if __name__ == "__main__":
    # cProfile.run('main()')
    main()
