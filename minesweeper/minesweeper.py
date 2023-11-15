import itertools
import random
from termcolor import cprint

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        # If the number of cells is less than or equal to the count
        # then all cells are mines and can be returned. Otherwise
        # it is unclear which remaining cells are mines.
        if len(self.cells) <= self.count:
            return self.cells
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        
        # If the count reaches 0, then all remaining cells are safe
        # otherwise it is unclear which cells are mines.
        if self.count == 0:
            return self.cells
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # If a cell is known to be a mine, remove it from the cells
        # and reduce the count by one.
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1) and 2) mark cell as a move that has been made and safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # 3) add a new sentence to the knowledge base
        adjacent = set()
        reduce_count = 0
        for i in range(cell[0]-1, cell[0]+2):
            if i < 0 or i > self.height-1: 
                # Continue if row is out of bounds
                # >0 or <7
                continue
            for j in range(cell[1]-1, cell[1]+2):
                if j < 0 or j > self.width-1:
                    # Continue if column is out of bounds
                    # >0 or <7
                    continue
                if (i,j) != cell and (i,j) not in self.safes:
                    # Add tuple to set unless it is the middle cell or a known safe
                    adjacent.add((i,j))
                if (i,j) in self.mines:
                    reduce_count += 1
        
        # Construct new sentence, if adjacents exist
        new_sent = None
        if adjacent != set():
            new_sent = Sentence(adjacent, count - reduce_count)

        if new_sent is not None:
            self.knowledge.append(new_sent)

        # 4) mark any additional cells as safe or as mines
        # if it can be concluded based on the AI's knowledge base

        # Store a list of sentences to remove from knowledge because they are all mines or all safes
        rm_sent = []

        # Loop over the sentences in the knowledge base
        for sent in self.knowledge:

            # Get a set of safe cells from a sentence or an empty set
            new_safes = sent.known_safes()
            if new_safes != set():
                new_safes_list = [s for s in new_safes]

                # Loop over set of new safe cells and update safe knowledge
                for safe in new_safes_list:
                    if safe not in self.mines:
                        self.mark_safe(safe)

                # Mark sentences for removal from knowledge if they are all mines or all safes
                if new_safes_list != []:
                    rm_sent.append(sent)

        # Loop over th
        for sent in self.knowledge:

             # Get a set of mines from a sentence or an empty set
            new_mines = sent.known_mines()
            if new_mines != set():
                new_mines_list = [m for m in new_mines]

                # Loop over set of new mine cells and update mine knowledge
                for mine in new_mines_list:
                    self.mark_mine(mine)

                # Mark sentences for removal from knowledge if they are all mines or all safes
                if new_mines_list != []:
                    rm_sent.append(sent)

        self.knowledge = [sent for sent in self.knowledge if sent not in rm_sent]


        # 5) Infer new sentences by checking subsets
        sub_sents = []
        for i, sent1 in enumerate(self.knowledge):

            if not sent1.cells:
                continue

            for sent2 in self.knowledge[i+1:]:
                if sent1 == sent2 or not sent2:
                    continue
                if sent1.cells.issubset(sent2.cells):
                    new_cells = sent2.cells.difference(sent1.cells)
                    new_count = sent2.count - sent1.count

                    if new_cells and new_count >= 0:
                        sub_sent = Sentence(new_cells, new_count)
                    # sub_sent = Sentence(sent2.cells.difference(sent1.cells),
                    #                     sent2.count - sent1.count)
                        
                        if sub_sent not in sub_sents:

                    
                    # if sub_sent.cells != set() and sub_sent.count >= 0:
                            sub_sents.append(sub_sent)

        
        # Add new sub-sentences to knowledge
        self.knowledge.extend(sub_sents)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        # Subtract moves made from safe cells
        available_safe = self.safes
        available_safe = available_safe - self.moves_made

        # Return random move from available cells
        try:
            move = available_safe.pop()
            print(f"Safe move {move}")
            return move
        except(KeyError):
            return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        
        # Get cells not to select (previously chosen or known mines)
        bad_cells = self.mines
        bad_cells = bad_cells.union(self.moves_made)

        # Generate a set of tuples representing each cell
        all_cells = set()

        for i in range(self.height):
            for j in range(self.width):
                all_cells.add((i,j))

        # Remove the bad cells from the all cells
        all_cells = all_cells.difference(bad_cells)

        # Return a random cell
        try:
            move = all_cells.pop()
            return move
        except(KeyError):
            return None