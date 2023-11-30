import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """

    # Initialise p to 1
    p = 1

    # Loop over each person
    for person in people:

        gene_prob = 0
        trait_prob = 0

        # When person has no parents
        if person["mother"] is None and person["father"] is None:

            # Take probability that person in one_gene has one copy
            if person in one_gene:
                gene_prob = PROBS["gene"][1]

                # Take probability that person with 1 gene has/hasn't trait
                trait_prob = PROBS["trait"][1][True] if person in have_trait else PROBS["trait"][1][False]

            # Take probability that person in two_genes has two copies
            elif person in two_genes:
                gene_prob = PROBS["gene"][2] 

                # Take probability that person with 2 genes has/hasn't trait
                trait_prob = PROBS["trait"][2][True] if person in have_trait else PROBS["trait"][2][False]

            # Take probability that person in neither has no copy
            else:
                gene_prob = PROBS["gene"][0] 

                # Take probability that person with 0 genes has/hasn't trait
                trait_prob = PROBS["trait"][0][True] if person in have_trait else PROBS["trait"][0][False]
        
        # When person has parents
        else:

            # Get list of parents
            mother = people[person["mother"]]
            father = people[person["father"]]

            # Take probability of inheriting gene from mother
            mother_prob = 0.5 if mother in one_gene else 0.99 if mother in two_genes else PROBS["mutation"]

            # Take probability of inheriting gene from father
            father_prob = 0.5 if father in one_gene else 0.99 if father in two_genes else PROBS["mutation"]

            # Take probability that person has 1 gene, given parents' genes
            if person in one_gene:

                # Take probability of gene from mother but not father
                prob_1 = mother * (1 - father_prob)

                # Take probability of gene from father but not mother
                prob_2 = father * (1 - mother_prob)

                # Add together to get gene probability
                gene_prob = prob_1 + prob_2

                # Take the probability that person with 1 gene has / hasn't the trait
                trait_prob = PROBS["trait"][1][True] if person in have_trait else PROBS["trait"][1][False]
                  
            # Take probability that person has 2 genes, given parents' genes
            elif person in two_genes:

                # Take probability of gene from parent 1 and parent 2
                trait_prob = mother_prob * father_prob

                # Take the probability that person with 2 genes has / hasn't the trait
                trait_prob = PROBS["trait"][2][True] if person in have_trait else PROBS["trait"][2][False]

            # Take probability that person has 0 genes, given parents' genes
            else:

                # Take probability of gene from neither parent 1 nor parent 2
                gene_prob = (1 - mother_prob) * (1 - father_prob)

                # Take the probability that person with 0 genes has / hasn't the trait
                trait_prob = PROBS["trait"][0][True] if person in have_trait else PROBS["trait"][0][False]

        # Multiply probability of given number of genes and presence or not of trait
        p *= gene_prob * trait_prob
        
    # Multiply the probabilities for each person to find p
    return p


def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    
    # Loop over each person in dictionary
    for person in probabilities:

        # Add p to relevant number of genes
        if person in one_gene:
            person["gene"][1] += p

        elif person in two_genes:
            person["gene"][2] += p

        else:
            person["gene"][0] += p

        # Add p to trait or not trait
        if person in have_trait:
            person["trait"][True] += p

        else:
            person["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """

    # Loop over each person in dictionary
    for person in probabilities:

        # Get sum of trait distribution
        t_sum = person["trait"][True] + person["trait"][False]

        # Normalise trait distribution
        person["trait"][True] = person["trait"][True] / t_sum
        person["trait"][False] = person["trait"][False] / t_sum

        # Get sum of gene distribution
        g_sum = person["gene"][0] + person["gene"][1] + person["gene"][2]

        # Normalise gene distribution
        person["gene"][0] = person["gene"][0] / g_sum
        person["gene"][1] = person["gene"][1] / g_sum
        person["gene"][2] = person["gene"][2] / g_sum


if __name__ == "__main__":
    main()
