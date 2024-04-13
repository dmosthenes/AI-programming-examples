import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # raise NotImplementedError

    # Initialize lists
    evidence = []
    labels = []

    with open(filename) as file:
        data = csv.reader(file)

        # Skip header
        next(data)

        for row in data:

            evidence.append([int(row[0]), float(row[1]), int(row[2]), float(row[3]), 
                             int(row[4]), float(row[5]), float(row[6]), float(row[7]), 
                             float(row[8]), float(row[9]), int(month_to_num(row[10])), 
                             int(row[11]), int(row[12]), int(row[13]), int(row[14]),
                             1 if row[15] == "Returning_Visitor" else 0, 1 if row[16] == "TRUE" else 0])
            
            labels.append(1 if row[17] == "TRUE" else 0)

    # Return data as a tuple
    return (evidence, labels)

def month_to_num(month):

    match month:
        case "Jan":
            return 0
        case "Feb":
            return 1
        case "Mar":
            return 2
        case "Apr":
            return 3
        case "May":
            return 4
        case "June":
            return 5
        case "Jul":
            return 6
        case "Aug":
            return 7
        case "Sep":
            return 8
        case "Oct":
            return 9
        case "Nov":
            return 10
        case "Dec":
            return 11


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # raise NotImplementedError

    neigh = KNeighborsClassifier(1)

    return neigh.fit(evidence, labels)


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    # raise NotImplementedError

    # true_positive = 0
    # true_negative = 0
    # total_positive = 0
    # total_negative = 0

    # for i in range(len(labels)):

    #     if labels[i] == predictions[i]:
    #         if labels[i] == 1:
    #             true_positive += 1
    #             total_positive += 1
    #         else:
    #             true_negative += 1
    #             total_negative += 1
        
    #     else:
    #         if labels[i] == 1:
    #             total_positive += 1
    #         else:
    #             total_negative += 1

    # return (true_positive / total_positive, true_negative / total_negative)

    true_positive = 0
    true_negative = 0
    total_positive = labels.count(1)
    total_negative = labels.count(0)

    for label, prediction in zip(labels, predictions):

        if label == prediction == 1:
            true_positive += 1

        if label == prediction == 0:
            true_negative += 1

    sensitivity = true_positive / total_positive if true_positive > 0 else 0
    specifitiy = true_negative / total_negative if true_negative > 0 else 0

    return (sensitivity, specifitiy)


if __name__ == "__main__":
    main()
