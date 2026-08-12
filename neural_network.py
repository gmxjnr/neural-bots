import numpy as np


class NeuralNetwork:

    def __init__(self):
        # 5 inputs -> 6 hidden neurons
        self.weights_input_hidden = np.random.randn(5, 6) * 0.5
        self.bias_hidden = np.zeros(6)

        # 6 hidden neurons -> 2 outputs
        self.weights_hidden_output = np.random.randn(6, 2) * 0.5
        self.bias_output = np.zeros(2)

    def activate(self, x):
        return np.tanh(x)

    def forward(self, inputs):

        # Input -> hidden
        hidden = np.dot(inputs, self.weights_input_hidden)
        hidden += self.bias_hidden
        hidden = self.activate(hidden)

        # Hidden -> output
        output = np.dot(hidden, self.weights_hidden_output)
        output += self.bias_output
        output = self.activate(output)

        return output

    def copy(self):
        """
        Creates an exact copy of this neural network.
        """

        new_brain = NeuralNetwork()

        new_brain.weights_input_hidden = self.weights_input_hidden.copy()
        new_brain.bias_hidden = self.bias_hidden.copy()

        new_brain.weights_hidden_output = self.weights_hidden_output.copy()
        new_brain.bias_output = self.bias_output.copy()

        return new_brain

    def mutate(self, mutation_rate=0.1, mutation_strength=0.5):
        """
        Randomly changes some weights and biases.

        This is what creates variation between generations.
        """

        # Input -> hidden weights
        mask = np.random.random(self.weights_input_hidden.shape) < mutation_rate

        mutations = (
            np.random.randn(*self.weights_input_hidden.shape)
            * mutation_strength
        )

        self.weights_input_hidden += mask * mutations

        # Hidden biases
        mask = np.random.random(self.bias_hidden.shape) < mutation_rate

        mutations = (
            np.random.randn(*self.bias_hidden.shape)
            * mutation_strength
        )

        self.bias_hidden += mask * mutations

        # Hidden -> output weights
        mask = np.random.random(self.weights_hidden_output.shape) < mutation_rate

        mutations = (
            np.random.randn(*self.weights_hidden_output.shape)
            * mutation_strength
        )

        self.weights_hidden_output += mask * mutations

        # Output biases
        mask = np.random.random(self.bias_output.shape) < mutation_rate

        mutations = (
            np.random.randn(*self.bias_output.shape)
            * mutation_strength
        )

        self.bias_output += mask * mutations