import pygame
import random
import math
import numpy as np

from neural_network import NeuralNetwork


# ============================================================
# Sensor settings
# ============================================================

RAY_COUNT = 5
RAY_SPREAD = math.pi * 0.8   # total angle covered by the ray fan
RAY_MAX_DISTANCE = 250


class Bot:

    def __init__(self, width, height, radius, bot_id=0):

        self.width = width
        self.height = height
        self.radius = radius

        # Stable identity, used by the brain viewer to look this bot
        # up over HTTP. Stays the same across generations since
        # Evolution reuses the same Bot instances (just resets them).
        self.id = bot_id

        self.brain = NeuralNetwork()

        self.hit_obstacle = False

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
        self.hit_obstacle = False

        self.start_distance = 0
        self.distance_to_goal = 0

        # Used by the refined fitness function: how long this bot
        # has been alive, and how much clearance it kept from
        # obstacles on average (0 = constantly grazing walls,
        # 1 = always far away).
        self.time_alive = 0
        self._clearance_sum = 0

        # 5 original inputs + RAY_COUNT obstacle sensors
        self.inputs = np.zeros(5 + RAY_COUNT)
        self.outputs = np.zeros(2)

        # Default rays: all pointing straight from the bot's own
        # position (zero length), so draw() always has valid
        # (x, y) tuples to unpack, even before the first update().
        self.ray_hits = [(self.x, self.y)] * RAY_COUNT

    def sense_obstacles(self, obstacles):
        """
        Casts a fan of rays from the bot and returns, for each ray,
        the normalized distance (0 = touching something, 1 = nothing
        within range) to the closest obstacle or wall.
        """

        readings = []
        hit_points = []

        start_angle = self.angle - RAY_SPREAD / 2

        for i in range(RAY_COUNT):

            ray_angle = (
                start_angle +
                (RAY_SPREAD / (RAY_COUNT - 1)) * i
            )

            closest_distance = RAY_MAX_DISTANCE

            # ------------------------------------------------
            # Check obstacles
            # ------------------------------------------------

            for obstacle in obstacles:

                hit_distance = obstacle.ray_intersection_distance(
                    self.x,
                    self.y,
                    ray_angle,
                    RAY_MAX_DISTANCE
                )

                if hit_distance is not None and hit_distance < closest_distance:

                    closest_distance = hit_distance

            # ------------------------------------------------
            # Check screen boundaries (treat as walls too)
            # ------------------------------------------------

            dir_x = math.cos(ray_angle)
            dir_y = math.sin(ray_angle)

            for step in range(0, int(RAY_MAX_DISTANCE), 4):

                check_x = self.x + dir_x * step
                check_y = self.y + dir_y * step

                if (
                    check_x < 0 or check_x > self.width or
                    check_y < 0 or check_y > self.height
                ):

                    if step < closest_distance:
                        closest_distance = step

                    break

            hit_points.append(
                (
                    self.x + dir_x * closest_distance,
                    self.y + dir_y * closest_distance
                )
            )

            readings.append(closest_distance / RAY_MAX_DISTANCE)

        self.ray_hits = hit_points

        return readings

    def update(self, goal, obstacles=None):

        if not self.alive:
            return

        if obstacles is None:
            obstacles = []

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
        # Obstacle sensors
        # ----------------------------------------------------

        ray_readings = self.sense_obstacles(obstacles)

        # Track how much breathing room this bot kept from obstacles
        # over its lifetime, used by the fitness function below.
        self.time_alive += 1
        self._clearance_sum += min(ray_readings)

        # ----------------------------------------------------
        # Neural network inputs
        # ----------------------------------------------------

        base_inputs = [
            distance / math.sqrt(
                self.width ** 2 +
                self.height ** 2
            ),

            direction_normalized,

            left_distance,

            right_distance,

            current_direction
        ]

        self.inputs = np.array(
            base_inputs + ray_readings
        )

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
        # Check obstacle collision
        # ----------------------------------------------------

        for obstacle in obstacles:

            if obstacle.collides_with_point(self.x, self.y, self.radius):

                self.alive = False
                self.hit_obstacle = True

                break

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

        # Average obstacle clearance over the bot's lifetime, scaled
        # down so it nudges behavior without overpowering progress.
        # A bot that constantly hugs walls scores lower than one that
        # keeps some breathing room, even if both reach the goal.
        average_clearance = (
            self._clearance_sum / self.time_alive
            if self.time_alive > 0 else 0
        )

        clearance_score = average_clearance * 0.5

        fitness = (
            progress_score +
            closeness_score +
            clearance_score
        )

        # Huge reward for actually reaching the goal, plus a speed
        # bonus: reaching it in under ~5 seconds (300 frames @ 60fps)
        # earns extra credit, tapering to 0 for slow runs. This
        # separates "found a fast route" from "wandered into it".
        if self.reached_goal:

            fitness += 10

            speed_bonus = max(0, 300 - self.time_alive) / 100
            fitness += speed_bonus

        # Bigger penalty for hitting an obstacle. This used to be -1,
        # which the +10 goal bonus made almost irrelevant. At -3 it's
        # a real deterrent without completely wiping out a bot that
        # otherwise made good progress.
        if self.hit_obstacle:
            fitness -= 3

        return fitness

    def draw(self, screen, color, show_rays=False, id_font=None):

        if id_font is not None:

            id_surface = id_font.render(
                str(self.id),
                True,
                (200, 200, 210)
            )

            screen.blit(
                id_surface,
                (
                    self.x - id_surface.get_width() / 2,
                    self.y - self.radius - 16
                )
            )

        if show_rays:

            for hit_x, hit_y in self.ray_hits:

                pygame.draw.line(
                    screen,
                    (90, 90, 110),
                    (
                        self.x,
                        self.y
                    ),
                    (
                        hit_x,
                        hit_y
                    ),
                    1
                )

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