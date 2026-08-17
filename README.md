# Neural Bots

An experimental AI simulation where autonomous bots learn and evolve through **neural networks and evolutionary algorithms**.

The goal of this project is to explore how relatively simple neural networks can be combined with evolution to create increasingly capable autonomous agents — without directly programming their behavior.

## Overview

Neural Bots simulates a population of bots inside a 2D environment. Each bot has its own neural network that receives information about its surroundings and produces movement decisions.

Instead of manually teaching the bots what to do, their neural networks are gradually improved through an evolutionary process:

1. Bots are spawned with randomly initialized neural networks.
2. Each bot interacts with the environment.
3. Bots receive a fitness score based on their performance.
4. The best-performing bots are selected.
5. Their neural networks are copied and mutated.
6. A new generation is created.
7. The process repeats.

Over many generations, the population should gradually develop better behavior.

## Features

* Neural-network driven autonomous bots
* Population-based simulation
* Evolutionary selection
* Neural-network mutation
* Fitness-based generation progression
* Real-time 2D visualization
* Configurable neural-network architecture
* Modular Python project structure

## How It Works

Each bot has a neural network that acts as its "brain".

The network takes environmental information as input and processes it through one or more hidden layers before producing movement outputs.

A simplified architecture currently looks like:

```text
Input Layer
    ↓
Hidden Layer
    ↓
Output Layer
```

The exact inputs and outputs can be changed as the project evolves.

### Neural Networks

The neural networks are implemented using NumPy rather than relying on a machine-learning framework.

This keeps the implementation relatively lightweight and makes it easier to understand what is happening inside the network.

The network is responsible for turning environmental information into actions.

### Evolution

Evolution is handled separately from the neural-network implementation.

Each generation follows a basic evolutionary cycle:

```text
Population
    ↓
Simulation
    ↓
Fitness Evaluation
    ↓
Selection
    ↓
Mutation
    ↓
New Population
    ↓
Repeat
```

The best-performing bots are used as the foundation for the next generation, while mutations introduce variation into their neural networks.

## Project Structure

```text
neural-bots/
│
├── main.py
├── bot.py
├── neural_network.py
├── evolution.py
├── requirements.txt
└── README.md
```

### `main.py`

Handles the simulation itself, including the Pygame window, environment and main update loop.

### `bot.py`

Contains the bot implementation, including movement, state and interaction with the environment.

### `neural_network.py`

Contains the neural-network implementation used as the bot's brain.

### `evolution.py`

Handles the evolutionary process, including fitness evaluation, selection, reproduction and mutation.

## Technologies

* **Python**
* **NumPy**
* **Pygame**
* Object-oriented programming
* Neural networks
* Evolutionary algorithms
* Genetic mutation and selection

## Installation

Clone the repository:

```bash
git clone https://github.com/gmxjnr/neural-bots.git
cd neural-bots
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Run the simulation:

```bash
python main.py
```

## Project Status

This project is currently **under active development**.

The current implementation is primarily an experimental learning project. More advanced evolutionary mechanics, environmental challenges and neural-network features will be added over time.

Planned improvements include:

* [x] More complex environments
* [ ] Improved fitness functions
* [ ] Better visualization of generations
* [ ] Configurable neural-network architectures
* [ ] More advanced mutation strategies
* [ ] Saving and loading evolved populations
* [ ] Generation statistics
* [ ] Visualization of neural-network activity
* [ ] More sophisticated bot behavior

## Why I Built This

I built Neural Bots as a way to learn more about **artificial intelligence, neural networks and evolutionary algorithms by implementing the concepts myself**.

Rather than relying entirely on existing AI libraries, the project focuses on understanding the underlying concepts and building the individual components from scratch.

It also serves as an ongoing experiment into a simple question:

> **What kind of behavior can emerge when you give simple agents a brain, a goal and the ability to evolve?**

## License

This project is currently available for educational and experimental purposes.

A formal license will be added in the future.
