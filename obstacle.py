import pygame
import math


OBSTACLE_COLOR = (200, 70, 90)


class Obstacle:

    def __init__(self, x, y, width, height):

        self.rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

    def draw(self, screen):

        pygame.draw.rect(
            screen,
            OBSTACLE_COLOR,
            self.rect,
            border_radius=4
        )

    def collides_with_point(self, x, y, radius):
        """
        Circle vs rectangle collision check.
        Used to see if a bot has hit this obstacle.
        """

        closest_x = max(
            self.rect.left,
            min(x, self.rect.right)
        )

        closest_y = max(
            self.rect.top,
            min(y, self.rect.bottom)
        )

        dx = x - closest_x
        dy = y - closest_y

        distance_squared = dx * dx + dy * dy

        return distance_squared < radius * radius

    def ray_intersection_distance(self, origin_x, origin_y, angle, max_distance):
        """
        Casts a ray from (origin_x, origin_y) at the given angle.
        Returns the distance to this obstacle's edge, or None if it
        doesn't hit within max_distance.

        Uses simple step-based marching (fast enough for small maps
        and small ray counts, and much easier to reason about than
        a full slab/AABB intersection test).
        """

        step_size = 4

        steps = int(max_distance / step_size)

        dir_x = math.cos(angle)
        dir_y = math.sin(angle)

        for step in range(steps):

            distance = step * step_size

            check_x = origin_x + dir_x * distance
            check_y = origin_y + dir_y * distance

            if self.rect.collidepoint(check_x, check_y):

                return distance

        return None


def build_default_course(width, height):
    """
    A simple obstacle course: a few wall segments the bots
    need to navigate around to reach the goal on the right.
    """

    obstacles = [

        Obstacle(
            300, 0,
            40, height * 0.65
        ),

        Obstacle(
            600, height * 0.35,
            40, height * 0.65
        ),

        Obstacle(
            900, 0,
            40, height * 0.55
        ),

    ]

    return obstacles