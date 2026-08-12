import random


class Evolution:

    def __init__(self, bots):

        self.bots = bots

        self.generation = 1

        self.best_fitness = 0
        self.average_fitness = 0

    def evolve(self):

        # ----------------------------------------------------
        # Calculate fitness
        # ----------------------------------------------------

        fitness_scores = []

        for bot in self.bots:

            fitness = bot.calculate_fitness()

            fitness_scores.append(
                (fitness, bot)
            )

        # Sort from best -> worst
        fitness_scores.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # ----------------------------------------------------
        # Statistics
        # ----------------------------------------------------

        self.best_fitness = (
            fitness_scores[0][0]
        )

        self.average_fitness = (
            sum(
                score
                for score, bot in fitness_scores
            )
            / len(fitness_scores)
        )

        # ----------------------------------------------------
        # Select the best bots
        # ----------------------------------------------------

        survivor_count = max(
            2,
            len(self.bots) // 5
        )

        survivors = [
            bot
            for score, bot
            in fitness_scores[:survivor_count]
        ]

        # ----------------------------------------------------
        # Create next generation
        # ----------------------------------------------------

        new_bots = []

        for i in range(len(self.bots)):

            # Keep the absolute best bot unchanged
            if i == 0:

                parent = survivors[0]

                child = self.bots[i]

                child.brain = parent.brain.copy()

            else:

                # Pick a random survivor
                parent = random.choice(
                    survivors
                )

                child = self.bots[i]

                # Copy brain
                child.brain = parent.brain.copy()

                # Mutate it
                child.brain.mutate(
                    mutation_rate=0.10,
                    mutation_strength=0.4
                )

            # Reset bot for new generation
            child.reset()

            new_bots.append(child)

        self.bots = new_bots

        self.generation += 1