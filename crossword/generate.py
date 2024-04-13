import sys

from crossword import *
from copy import copy, deepcopy

INTERLEAVING = True

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """

        self.enforce_node_consistency()
        self.ac3()
        if not INTERLEAVING:
            return self.backtrack(dict())
        else:
            return self.backtrack_ac3(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Loop over all variables
        for var in self.crossword.variables:

            # Create new set for var domain containing only words of length
            # consistent with unary constraint
            self.domains[var] = {word for word in self.domains[var] if len(word) == var.length}

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        if x.__eq__(y):
            return False

        coords = self.crossword.overlaps[x,y]
        if not coords:
            return False
        
        # Keep track of revisions with boolean variable
        revisions = False

        # If there is an overlap remove any words from x's domain which
        # do not have possible corresponding value in y's domain
        x_coord = coords[0]
        y_coord = coords[1]

        # Loop over copy of x domain words, original domain will change size
        for x_word in copy(self.domains[x]):

            # Remove x_word if there is not at least 1 word with equal char at index
            for y_word in self.domains[y]:

                    # When a word in y domain has matching character
                    if x_word[x_coord] == y_word[y_coord]:
                        # break out of y loop and consider next x word
                        break
                
            # When no char match is found, remove word from x
            # Condition is met only if end of y domain is
            # reached without finding any matches (for-else)
            # Break statement is never executed
            else:
                self.domains[x].remove(x_word)        
                revisions = True

        # Return revisions value
        return revisions

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        arc_queue = set()

        # Assume arcs is a list of tuples (v1, v2)
        # If optional argument is given, return a list of inconsistent words
        # for each variable Y in (Y,X)
        if arcs is not None:

            for arc in arcs:
                arc_queue.add(arc)

        # Add all arcs in the crossword if paramater is None
        else:

            # Loop over each variable
            for var in self.crossword.variables:

                # Get neighbours for each variable
                for neigh in self.crossword.neighbors(var):

                    # Add tuple to arc queue
                    arc_queue.add((var,neigh))

        # Until all arcs are dequeued
        while arc_queue:
            
            (x, y) = arc_queue.pop()

            # Revise arc
            if self.revise(x, y):
                
                # Problem is insoluble if nothing remains in domain
                if len(self.domains[x]) < 1:
                    return False
                
                # If revision occurs, enqueue additional arcs 
                for z in self.crossword.neighbors(x):
                    if z is y:
                        continue
                    arc_queue.add((x,z))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(self.crossword.variables) != len(assignment):
            return False

        # Check that each variable has a word assigment
        for word in assignment.values():
            
            if word is None:
                return False
            
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # Check if assigned words comply with variable length constraint
        # Loop over variables in crossword
        for var, word in assignment.items():

            # Check if variable is unassigned
            if word is None:
                continue

            # Otherwise, check if word is the corrent length
            if len(word) != var.length:

                return False
            
            # Check if var's assigned neighbours comply
            # Get neighbours
            neighs = self.crossword.neighbors(var)

            # Iterate over neighbours
            for neigh in neighs:

                # Check if neigh is assigned
                if neigh in assignment and assignment[neigh] is not None:
                    neigh_word = assignment[neigh]

                    # Get overlap coordinates   
                    (var_index, neigh_index) = self.crossword.overlaps[var,neigh]

                    # Return False if character is not the same
                    if not word[var_index] == neigh_word[neigh_index]:
                        return False
                    
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Create list of tuples of possible words and their n value
        least_constrained = {word: 0 for word in self.domains[var]}

        # Get var neighbours
        var_neigh = self.crossword.neighbors(var)

        # Loop over the domain of var
        for var_word in self.domains[var]:

            # Loop over each of var's neighbours
            for neigh in var_neigh:

                # Get coordinates of overlap between var and neigh
                (var_index, neigh_index) = self.crossword.overlaps[var,neigh]
 
                # Check how many words are available given chosen word
                for neigh_word in self.domains[neigh]:

                    # Check if neigh_word has same char at var_word overlap
                    if var_word[var_index] == neigh_word[neigh_index]:
                        least_constrained[var_word] += 1
        
        # Sort list according to highest n value first
        return sorted([x for x in least_constrained.keys()], key = lambda x: least_constrained[x])


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Create a list to contain tuple of variable and domain size
        smallest_domain = []

        # Loop over all variables
        for var in self.crossword.variables:

            # Skip any variables already assigned
            if var not in assignment or assignment[var] is None:
                # Append unassigned as tuple with domain length
                smallest_domain.append((var, len(self.domains[var])))

        # Sort by smallest to largest domain
        smallest_domain.sort(key=lambda x: x[1], reverse=True)

        # Reduce list to only elements with domains of equal size to smallest
        
        small_n = smallest_domain[0][1]


        smallest_domain = [item for item in smallest_domain if not item[1] > small_n]

        # When list has more than one element, select element with most neighbours
        if len(smallest_domain) > 1:

            highest_degree = (smallest_domain[0][0], len(self.crossword.neighbors(smallest_domain[0][0])))

            for (var,_) in smallest_domain:

                if len(self.crossword.neighbors(var)) > highest_degree[1]:

                    highest_degree = (var, len(self.crossword.neighbors(var)))

            return highest_degree[0]

        # Otherwise, select the first element of the list
        else:
            return smallest_domain[0][0]


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Base case: assignment complete
        if self.assignment_complete(assignment):
            return assignment

        # Select unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Loop over values in var's domain
        for word in self.order_domain_values(var, assignment):

            # Assign word in assignment dictionary
            assignment[var] = word

            # Continue to next word if assignment is not consistent
            if self.consistent(assignment):
                
                # Store result of backtracking, return if not None
                result = self.backtrack(assignment)
                if result:
                    return result
            
            # Otherwise, undo the assignment and remove inferences
            assignment[var] = None

        return None

    def backtrack_ac3(self, assignment):
        """
        Backtrack with interleaving.
        """
        # Base case: assignment complete
        if self.assignment_complete(assignment):
            return assignment

        # Select unassigned variable
        var = self.select_unassigned_variable(assignment)

        # Make a copy of domains
        copied_domains = deepcopy(self.domains)

        # Loop over values in var's domain
        for word in self.order_domain_values(var, assignment):

            # Assign word in assignment dictionary
            assignment[var] = word

            # Continue to next word if assignment is not consistent
            if self.consistent(assignment):

                # Set domain of var to the current word
                self.domains[var] = {word}

                # Remove inconsistent words from neighbour variables
                self.ac3([(neigh, var) for neigh in self.crossword.neighbors(var)])

                # Store result of backtracking, return if not None
                result = self.backtrack(assignment)
                if result is not None:
                    return result    
            
            # Otherwise, undo the assignment and remove inferences
            del assignment[var]

            # Remove inferences from domains (add inconsistent words back)
            self.domains = copied_domains

        return None

# import cProfile, signal, time

# def timeout_handler(signum, frame):
#     raise Exception("End of profiling")

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

    # Set the signal handler and a 5-minute alarm
    # signal.signal(signal.SIGALRM, timeout_handler)
    # signal.alarm(100)  # 300 seconds = 5 minutes

    # try:
    #     cProfile.run('main()', 'restats')
    # except Exception as e:
    #     print(e)

    # # Use pstats to read and print the stats
    # import pstats
    # p = pstats.Stats('restats')
    # p.sort_stats('cumulative').print_stats(10)  # Print top 10 functions