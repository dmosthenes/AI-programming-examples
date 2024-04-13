import tensorflow as tf
import keras
from keras import layers
import numpy as np

class NeuralNetwork():

    def __init__(self, a, b, c):
        self.inputs = a
        self.hidden = b
        self.outputs = c
        self.model = self.create_model()

    def create_model(self):
        model = keras.Sequential(
            [
                layers.Dense(self.inputs, activation='relu', name='input'),
                layers.Dense(self.hidden, activation='relu', name='hidden'),
                layers.Dense(self.outputs, activation='softmax', name='ouput')
            ]
        )

        return model

    def predict(self, input_features):

        # Put features into a tensor
        xs = tf.constant(input_features)
        ys = self.model.predict(xs)
        return np.argmax(ys)

    def copy(self):
        pass


    def mutate(self):
        pass

