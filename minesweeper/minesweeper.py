import itertools
import random
import termcolor

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
        self.cells.discard(cell)
        self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
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

        # 1) and 2) Mark cell as a move that has been made and safe
        self.moves_made.add(cell)
        self.safes.add(cell)

        # TODO:Consider marking new cell as safe in all existing sentences
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        # Remove sentence from the knowledge base if all elements are safe
        for sentence in self.knowledge[:]:
            if sentence.count == 0:
                self.knowledge.remove(sentence)

        # 3) Create a new sentence entailing that the adjacent cells 
        # (where they are not known to be safe or mined) have the
        # given count
        adjacent = set()
        
        # Iterate over adjacent cells, skipping cells which are
        # out of bounds
        for i in range(cell[0]-1, cell[0]+2):
            if i < 0 or i > self.height-1: 
                continue
            for j in range(cell[1]-1, cell[1]+2):
                if j < 0 or j > self.width-1:
                    continue

                # Skip cells that are known safe or mines
                if (i,j) in self.safes or (i,j) in self.mines: 
                    continue

                # Update the adjacent list
                adjacent.add((i,j))
        
        # Construct the new sentence and add to knowledge
        new_sentence = Sentence(adjacent, count)

        # 5) Check if the new sentence is a subset of any sentences
        # or if any existing sentence is a subset of the new sentence
        new_sentences = []
        for sentence in self.knowledge:
            if new_sentence.cells.issubset(sentence.cells):
                new_set = sentence.cells - new_sentence.cells
                sub_sentence = Sentence(new_set, sentence.count - new_sentence.count)
                new_sentences.append(sub_sentence)

            elif sentence.cells.issubset(new_sentence.cells):
                new_set = new_sentence.cells - sentence.cells
                sub_sentence = Sentence(new_set, new_sentence.count - sentence.count)
                new_sentences.append(sub_sentence)
        
        # Append new sentence and subsentences to knowledge base
        self.knowledge.append(new_sentence)
        # print("New sentences")
        # for sentence in new_sentences: print(sentence.__str__())
        # new_sentences = set(new_sentences)
        for sentence in new_sentences: self.knowledge.append(sentence)
        # self.knowledge.extend(new_sentences)

        # Remove any duplicates from the knowledge base
        unique_knowledge = []
        [unique_knowledge.append(x) for x in self.knowledge if x not in unique_knowledge]
        self.knowledge = unique_knowledge

        print("Sentences: ", end="")
        for sentence in self.knowledge:
            print(sentence)

        # 4) Loop over the knowledge and check if any mines or safes have become certain

        RED = "\033[31m"
        GREEN = "\033[32m"

        for sentence in self.knowledge:
            new_safes = sentence.known_safes()
            new_mines = sentence.known_mines()
            
            if new_safes != set():
                termcolor.cprint(f"Adding to safes: {new_safes}", "green")
                self.knowledge.remove(sentence)
            if new_mines != set():
                termcolor.cprint(f"Adding to mines: {new_mines}", "red")
                self.knowledge.remove(sentence)

            self.safes.update(new_safes)
            self.mines.update(new_mines)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """

        # Debugging
        # print("Sentences")
        # for sentence in self.knowledge: print(sentence)
        print("Safes")
        print(self.safes)
        
        # Subtract moves made from safe cells
        available_safe = self.safes
        available_safe = available_safe - self.moves_made

        # Return random move from available cells
        try:
            move = available_safe.pop()
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
        # print(all_cells)

        # Return a random cell
        try:
            move = all_cells.pop()
            return move
        except(KeyError):
            return None