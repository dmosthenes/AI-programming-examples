import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# Holmes sat. : N V
# Holmes lit a pipe. : N V Det N
# We arrived the day before Thursday. : N V Det N P N
# Holmes sat in the red armchair and he chuckled. : N V P Det Adj N Conj N V
# (NP: Holmes, V: sat, (NP: P: in, (NP: Det: the, (NP: Adj: red, (NP: (NP: N: armchair,) Conj: and, (NP: N: he, V: chuckled))))
# My companion smiled an enigmatical smile. : NP V Det NP
# Holmes chuckled to himself. : N V P N
# She never said a word until we were at the door here. : N Adv V Det N Conj N V P Det N Adv
# Holmes sat down and lit his pipe. : N V Adv Conj V Det N
# I had a country walk on Thursday and came home in a dreadful mess. : N V Det Adj N P N Conj V N P Det Adj N
# I had a little moist red paint in the palm of my hand. : N V Det Adj Adj Adj N P Det N P Det N


# Should accept “Holmes sat in the armchair.” “Holmes sat in the red armchair.” 
# “Holmes sat in the little red armchair.”), but not “Holmes sat in the the armchair.”
# Remove NP -> Det NP

# NONTERMINALS = """
# S -> NP V | NP V NP | NP Adv NP | NP V Det NP | Det N V Det NP | NP Adv Conj NP
# NP -> N | NP P NP | P Det NP | P NP | Adj NP | NP Conj NP | NP V | V NP | V Det NP | NP V NP | NP Adv | Conj NP
# """

NONTERMINALS = """
S -> NP V | NP V NP | NP Conj NP | NP P NP
NP -> N | N NP | Det N | Det N NP | P NP | Det Adj NP | Adj NP | N V | N Adv V | V Det N | N V NP | N Adv V NP | Det N Adv | N V Adv | V N NP | V NP
"""


grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:

        # while True:
        s = input("Sentence: ")

        # Convert input into list of words
        s = preprocess(s)

        # Attempt to parse sentence
        try:
            trees = list(parser.parse(s))
        except ValueError as e:
            print(e)
            return
        if not trees:
            print("Could not parse sentence.")
            return

        # Print each tree with noun phrase chunks
        for tree in trees:
            tree.pretty_print()

            print("Noun Phrase Chunks")
            for np in np_chunk(tree):
                print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    # raise NotImplementedError

    tokens = nltk.tokenize.word_tokenize(sentence)

    return [tok.lower() for tok in tokens if all(char.isalpha() for char in tok)]

    # return [tok.lower() for tok in tokens if not any(not char.isalpha() for char in tok)]

    # out = []

    # for tok in tokens:

    #     if any(not char.isalpha() for char in tok):
    #         continue

    #     out.append(tok.lower())

    # return out


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    frontier = []
    out = []

    # Add initial NP to frontier
    # for subtree in tree.subtrees():
    #     if subtree.label() == "NP":
    #         frontier.append(subtree)

    frontier.append(tree)

    while frontier:

        sub_NP = False

        # loop over all subtrees for the popped element of the frontier
        tree = frontier.pop()

        for subtree in tree.subtrees():

            # This loop adds the tree itself as a subtree, creating an infinite loop
            # This is avoided by skipping on equality between the tree and subtree
            if subtree == tree:
                continue

            # If a NP is a subtree, add to frontier
            if subtree.label() == "NP":
                frontier.append(subtree)
                sub_NP = True

        # When the tree has no NPs and is not already in the out list, it can be added
        if not sub_NP and tree not in out:
            out.append(tree)

    return out


if __name__ == "__main__":
    main()
