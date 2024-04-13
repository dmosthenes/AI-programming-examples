import numpy as np

class NeuralNetwork():

    def __init__(self, input, hidden, output):
        """
        Defines the number of input features, hidden layers,
        and outputs.
        """
        
        self.input = input
        self.hidden = hidden
        self.output = output

        # Initialise random weights between input and hidden layer
        self.weights_ih = np.random.uniform(-1, 1, size=(self.hidden, self.input))
        self.bias_ih = np.ones((self.hidden, 1))

        # Initialise random weights between hidden layer and output
        self.weights_ho = np.random.uniform(-1, 1, size=(self.output, self.hidden))
        self.bias_ho = np.ones((self.output, 1))

    def __eq__(self, other):
        if (self.weights_ih == other.weights_ih).all() and (self.bias_ih == other.bias_ih).all() and (self.weights_ho == other.weights_ho).all() and (self.bias_ho == other.bias_ho).all():
            return True
        return False
    
    def sigmoid(self, matrix):
        return 1 / (1 + np.exp(-matrix))
    
    def copy(self):
        """
        Return a copy of the neural network.
        """

        copy = NeuralNetwork(self.input, self.hidden, self.output)
        copy.weights_ih = np.copy(self.weights_ih)
        copy.bias_ih = np.copy(self.bias_ih)
        copy.weights_ho = np.copy(self.weights_ho)
        copy.bias_ho = np.copy(self.bias_ho)
        return copy
    
    def mutate(self, mutation_factor):
        """
        Randomly modify the weights in the network by
        the given factor.
        """

        # mutation_factor chance to add random amount
        # between -1 and 1 to each bias

        weights = [self.weights_ih, self.weights_ho, self.bias_ih, self.bias_ho]

        for i, _ in enumerate(weights):
            if np.random.uniform(0,1) < mutation_factor:

                weights[i] += np.random.uniform(-0.1,0.1, size=weights[i].shape)


    def feedforward(self, input_features):
        """
        Find the matrix product of the input features and the
        hidden layer, then return the ouput of the hidden
        layer ...
        """

        try:
            assert isinstance(input_features, list)
        except AssertionError:
            print("Input features must be a list.")
            quit()

        # Convert input features into np array
        input_matrix = np.reshape(input_features, (len(input_features), 1))

        # Take the matrix product of the inputs and the hidden weights
        hidden = self.weights_ih@input_matrix

        # Add the bias weights to the prediction
        hidden = hidden + self.bias_ih

        # Apply the activation function
        hidden = self.sigmoid(hidden)

        # Take the matrix product of the hidden outputs and output weights
        output = self.weights_ho @ hidden

        # Add the bias weights to the prediction
        output = output + self.bias_ho

        # Apply the activation function
        output = self.sigmoid(output)

        return output
    
    def train(self, input_features, label):
        """
        Training loop for one data point and one label.
        """

        # Get a prediction for the input features
        pred = self.feedforward(input_features)

        # Convert label to a matrix
        label = np.reshape(label, (len(label), 1))

        # Get the error between the prediction and label
        error = label - pred

        # Backpropagate error to hidden layer
        # Get transpose of the hidden weight matrix
        ho_transpose = np.matrix.transpose(self.weights_ho)

        # Get the error for the hidden layer
        ho_error = ho_transpose @ error

        # Deal with the hidden bias


        # Backpropagate error to input layer
        # Transpose the input weights
        ih_transpose = np.matrix.transpose(self.weights_ih)

        # Get the error for the input layer
        ih_error = ih_transpose @ error

        # Deal with the input bias


        # Update the model's weights
