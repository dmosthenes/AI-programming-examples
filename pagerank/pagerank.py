import os
import random
import re
import sys
from math import isclose

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        print(sys.argv[1])
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.

    corpus: {"page 1": set("page 2", "page 3", ...), ...}
    """
    
    # Create output dictionary
    distribution = {}

    # Number of pages in corpus
    N = len(corpus)

    # Fetch pages linked to by current page
    linked_pages = corpus[page]

    # Assume that each value pair for key does not contain key page

    # When current page links to other pages
    if len(linked_pages) > 0:

        # Iterate over each page in corpus
        for p in corpus:

            # When a page is in the corpus but not linked to
            # by the current page
            if p not in linked_pages:

                # Page can only be reached by random "teleporting"
                distribution[p] = (1 - damping_factor) / N

            # When a page is linked to by the current page
            else:

                # Sum "teleporting probability" with
                rdom = (1 - damping_factor) / N

                # Probability of travelling by a link
                lnkd = damping_factor / len(linked_pages)

                distribution[p] = rdom + lnkd

    # When current page is isolated
    else:

        for p in corpus:
            
            # Distribute probability evenly across corpus
            distribution[p] = 1 / N

    return distribution


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    
    # Create output dictionary with all keys
    out = {}

    for page in corpus:

        # Set all starting values to 0
        out[page] = 0

    # Choose first page randomly
    start_page = random.choice(list(corpus.keys()))

    # Obtain initial transition probabilities
    transit = transition_model(corpus, start_page, damping_factor)

    # Collect n samples
    for _ in range(n):

        # Randomly select next page based on transition probabilities
        pages = list(transit.keys())
        weights = list(transit.values())

        # Choose next page based on previous weights
        next_page = random.choices(pages, weights, k=1)[0]

        # Update the total page visits
        out[next_page] += 1

        # Update transition probabilities
        transit = transition_model(corpus, next_page, damping_factor)

    # Normalise the probability samples
    for page in out:

        out[page] = out[page] / n
    
    return out


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Define initial transition matrix with each node 1/N
    prev_ranks = {}
    new_ranks = {}
    N = len(corpus)

    # Count iterations
    iter = 0

    for page in corpus:
        new_ranks[page] = 1 / N

    for page in corpus:
        prev_ranks[page] = 0
    
    # Continue iterating until converged
    while not converged(prev_ranks, new_ranks):

        # Increment counter
        iter += 1

        # Reassign the "new_ranks" to the "prev_ranks"
        prev_ranks = new_ranks.copy()

        # Calculate new rankings
        for page in corpus:

            # Apply page rank formula
            # linked_pages = corpus[page]

            # Calculate probability of navigating to page by randomly "teleporting"
            rdom = (1 - damping_factor) / N

            # Calculate the probability of navigating to page by link travel
            pr_sum = 0

            # Sum the scores for the linked pages

            # Get all the pages which link to page rather than pages page links to

            # Gather the incoming pages
            incoming_pages = []
            for in_page in corpus.keys():
                if in_page is page:
                    continue
                if page in corpus[in_page]:
                    incoming_pages.append(in_page)

            # Add together the page ranks of the incoming links
            for incoming_page in incoming_pages:
                pr_sum += prev_ranks[incoming_page] / len(corpus[incoming_page])

            # for linked_page in linked_pages:
            #     pr_sum += prev_ranks[linked_page] / len(corpus[linked_page])

            pr_sum_damped = pr_sum * damping_factor

            # Calculate new PR for page
            new_ranks[page] = rdom + pr_sum_damped

    # print(f"Converged after {iter} iterations.")

    return new_ranks


def converged(old, new):
    """
    Takes two dictionaries and checks if convergence has occurred.

    Convergence occurs when no PR changes by more than 0.001.
    """

    # Check that sum to 1
    total = sum(list(new.values()))
    if not isclose(total, 1.0):
        raise ValueError(f"Total probability is {total}")

    # Convergence occurs when no PR changes by more than 0.001

    # Iterate over each page
    for page in old:

        # When any page rank changes by more than 0.001, no convergence
        if abs(old[page] - new[page]) > 0.001:
            return False

    return True


if __name__ == "__main__":
    main()
