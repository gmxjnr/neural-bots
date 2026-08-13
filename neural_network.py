import numpy as np


INPUT_COUNT = 10   # 5 original inputs + 5 obstacle ray sensors
HIDDEN_COUNT = 12  # bumped up since the network now has more to reason about
OUTPUT_COUNT = 2


class NeuralNetwork:

    def __init__(self):

        self.weights_input_hidden = np.random.randn(INPUT_COUNT, HIDDEN_COUNT) * 0.5
        self.bias_hidden = np.zeros(HIDDEN_COUNT)

        self.weights_hidden_output = np.random.randn(HIDDEN_COUNT, OUTPUT_COUNT) * 0.5
        self.bias_output = np.zeros(OUTPUT_COUNT)

        # Snapshot of the most recent forward pass, kept around purely
        # so external tools (like the brain viewer) can inspect what
        # this network is "thinking" without re-running it.
        self.last_inputs = None
        self.last_hidden = None
        self.last_outputs = None

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

        self.last_inputs = inputs
        self.last_hidden = hidden
        self.last_outputs = output

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