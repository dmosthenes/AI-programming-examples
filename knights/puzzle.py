from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")
AStatement1 = Symbol("I am both a Knight and a Knave")
AStatement2 = Symbol("We are both Knaves")
AStatement3 = Symbol("We are the same kind")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")
BStatement1 = Symbol("We are different kinds")
BStatement2 = Symbol("A said 'I am a knave'")
BStatement3 = Symbol("C is a knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")
CStatement1 = Symbol("A is a knight")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # TODO

    # If A's statement is true then it is a knight
    Implication(AStatement1, AKnight),

    # If A's statement is true then A is a Knight and a Knave
    Implication(AStatement1, And(AKnight, AKnave)),

    # If A's statement is false then it is a Knave
    Implication(Not(AStatement1), AKnave),

    # A is either a Knight or a Knave but not both
    And(Or(AKnave, AKnight), Not(And(AKnight, AKnave)))

)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # TODO

    # If A's statement is true then both A and B are knaves
    Implication(AStatement2, And(AKnave, BKnave)),

    # If A is a knave then its statements are false
    Implication(AKnave, Not(AStatement2)),

    # If A's statement is false, then A is a Knave
    Implication(Not(AStatement2), AKnave),

    # If A's statement is false, then A and B are different
    Implication(Not(AStatement2), And(Or(And(AKnave, BKnight), And(AKnight, BKnave)), Not(And(AKnight, BKnight)), Not(And(AKnave, BKnave)))),

    # A is either a Knight or a Knave but not both
    And(Or(AKnave, AKnight), Not(And(AKnight, AKnave))),

    # B is either a Knight or a Knave but not both
    And(Or(BKnave, BKnight), Not(And(BKnight, BKnave)))

    
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # TODO

    # If A's statement is true then both A and B are the same kind
    Implication(AStatement3, Or(And(AKnave, BKnave), And(AKnight, BKnight))),

    # If A's statement is true then A is a Knight
    Implication(AStatement3, AKnight),

    # If A's statement is false then A is a Knave
    Implication(Not(AStatement3), AKnave),

    # Either A or B's statement is true but not both
    And(Or(AStatement3, BStatement1), Not(And(AStatement3, BStatement1))),

    # If B's statement is true then A and B are different kinds
    Implication(BStatement1, Or(And(AKnave, BKnight), And(AKnight, BKnave))),

    # If B's statement is true then B is a Knight
    Implication(BStatement1, BKnight),

    # If B's statement is false then B is a knave
    Implication(Not(BStatement1), BKnave),

    # A is either a Knight or a Knave but not both
    And(Or(AKnave, AKnight), Not(And(AKnight, AKnave))),

    # B is either a Knight or a Knave but not both
    And(Or(BKnave, BKnight), Not(And(BKnight, BKnave)))


)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(
    # TODO

    # If B's first statement is true, then it is a Knight and A said that it is a Knave
    Implication(BStatement2, And(AKnave, BKnight)),

    # If B's first statement is false, then it is a Knave and A said that is a Knight
    Implication(Not(BStatement2), And(AKnight, BKnave)),

    # If B's first statement is false, then it is a Knave and C is a Knight
    Implication(BStatement2, And(BKnave, CKnight)),

    # If B's second statement is true, then C is a Knave and it is a Knight
    Implication(BStatement3, And(CKnave, BKnight)),

    # If B's second statement is false, then C is a Knight and it is a Knave
    Implication(Not(BStatement3), And(CKnight, BKnave)),

    # If B's second statement is false, then A said that it is a Knight
    Implication(Not(BStatement3), And(CKnight, AKnight)),

    # If C's statement is true, then A is a Knight and it is a Knight
    Implication(CStatement1, And(AKnight, CKnight)),

    # If C's statement is false, then A is a Knave and it is a Knave
    Implication(Not(CStatement1), And(AKnave, CKnave)),

    # A is either a Knight or a Knave but not both
    And(Or(AKnave, AKnight), Not(And(AKnight, AKnave))),

    # B is either a Knight or a Knave but not both
    And(Or(BKnave, BKnight), Not(And(BKnight, BKnave))),

    # C is either a Knight or a Knave but not both
    And(Or(CKnave, CKnight), Not(And(CKnight, CKnave)))

)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
