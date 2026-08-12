import pygame
import random
import math
import numpy as np

from neural_network import NeuralNetwork


class Bot:

    def __init__(self, width, height, radius):

        self.width = width
        self.height = height
        self.radius = radius

        self.brain = NeuralNetwork()

        self.reset()

    def reset(self):

        # Start everyone on the left side.
        #
        # This makes the evolutionary challenge more interesting:
        # everyone has to figure out how to reach the goal on the right.

        self.x = random.randint(50, 150)
        self.y = random.randint(50, self.height - 50)

        self.angle = random.uniform(
            0,
            math.pi * 2
        )

        self.alive = True
        self.reached_goal = False

        self.start_distance = 0
        self.distance_to_goal = 0

        # Information used later by the brain visualizer
        self.inputs = np.zeros(5)
        self.outputs = np.zeros(2)

    def update(self, goal):

        if not self.alive:
            return

        # ----------------------------------------------------
        # Distance to goal
        # ----------------------------------------------------

        dx = goal.x - self.x
        dy = goal.y - self.y

        distance = math.sqrt(
            dx * dx +
            dy * dy
        )

        self.distance_to_goal = distance

        # Store starting distance
        if self.start_distance == 0:
            self.start_distance = distance

        # ----------------------------------------------------
        # Direction towards goal
        # ----------------------------------------------------

        target_angle = math.atan2(
            dy,
            dx
        )

        angle_difference = target_angle - self.angle

        # Keep between -PI and +PI
        angle_difference = math.atan2(
            math.sin(angle_difference),
            math.cos(angle_difference)
        )

        direction_normalized = (
            angle_difference / math.pi
        )

        # ----------------------------------------------------
        # Wall distances
        # ----------------------------------------------------

        left_distance = self.x / self.width

        right_distance = (
            self.width - self.x
        ) / self.width

        # ----------------------------------------------------
        # Current direction
        # ----------------------------------------------------

        current_direction = math.cos(
            self.angle
        )

        # ----------------------------------------------------
        # Neural network inputs
        # ----------------------------------------------------

        self.inputs = np.array([
            distance / math.sqrt(
                self.width ** 2 +
                self.height ** 2
            ),

            direction_normalized,

            left_distance,

            right_distance,

            current_direction
        ])

        # ----------------------------------------------------
        # Ask the brain
        # ----------------------------------------------------

        self.outputs = self.brain.forward(
            self.inputs
        )

        turn = self.outputs[0]

        speed = (
            self.outputs[1] + 1
        ) / 2

        # ----------------------------------------------------
        # Move
        # ----------------------------------------------------

        self.angle += turn * 0.15

        self.x += (
            math.cos(self.angle)
            * 2.5
            * speed
        )

        self.y += (
            math.sin(self.angle)
            * 2.5
            * speed
        )

        # ----------------------------------------------------
        # Screen boundaries
        # ----------------------------------------------------

        if self.x < self.radius:

            self.x = self.radius
            self.angle = math.pi - self.angle

        if self.x > self.width - self.radius:

            self.x = self.width - self.radius
            self.angle = math.pi - self.angle

        if self.y < self.radius:

            self.y = self.radius
            self.angle = -self.angle

        if self.y > self.height - self.radius:

            self.y = self.height - self.radius
            self.angle = -self.angle

        # ----------------------------------------------------
        # Check goal
        # ----------------------------------------------------

        goal_distance = math.sqrt(
            (self.x - goal.x) ** 2 +
            (self.y - goal.y) ** 2
        )

        if goal_distance < goal.radius + self.radius:

            self.reached_goal = True
            self.alive = False

    def calculate_fitness(self):

        if self.start_distance <= 0:
            return 0

        # How much closer did we get?
        progress = (
            self.start_distance -
            self.distance_to_goal
        )

        progress_score = (
            progress /
            self.start_distance
        )

        # Additional reward for being close
        closeness_score = (
            1 /
            (1 + self.distance_to_goal / 100)
        )

        fitness = (
            progress_score +
            closeness_score
        )

        # Huge reward for actually reaching the goal
        if self.reached_goal:
            fitness += 10

        return fitness

    def draw(self, screen, color):

        pygame.draw.circle(
            screen,
            color,
            (
                int(self.x),
                int(self.y)
            ),
            self.radius
        )

        # Direction indicator
        direction_x = (
            self.x +
            math.cos(self.angle) * 12
        )

        direction_y = (
            self.y +
            math.sin(self.angle) * 12
        )

        pygame.draw.line(
            screen,
            (220, 230, 255),
            (
                self.x,
                self.y
            ),
            (
                direction_x,
                direction_y
            ),
            2
        )