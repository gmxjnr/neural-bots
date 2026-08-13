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


# ============================================================
# Course library
# ============================================================
#
# Each function builds one obstacle layout. Bots keep their brains
# (weights persist across generations) but get moved between these
# layouts periodically, so they're pushed to learn general obstacle-
# avoidance rather than memorizing one specific gap pattern.

def build_course_open(width, height):
    """
    Almost no obstacles. Used as the "warm-up" course so a fresh
    population can first learn to reach the goal at all.
    """

    return [

        Obstacle(
            width * 0.5 - 20, height * 0.75,
            40, height * 0.25
        ),

    ]


def build_course_zigzag(width, height):
    """
    The original course: alternating walls from top and bottom,
    forcing an S-shaped path.
    """

    return [

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


def build_course_gauntlet(width, height):
    """
    Narrower gaps and more walls than the zigzag. Meant to be
    attempted after bots already handle zigzag reasonably well.
    """

    return [

        Obstacle(
            250, 0,
            35, height * 0.55
        ),

        Obstacle(
            250, height * 0.75,
            35, height * 0.25
        ),

        Obstacle(
            550, height * 0.2,
            35, height * 0.6
        ),

        Obstacle(
            850, 0,
            35, height * 0.45
        ),

        Obstacle(
            850, height * 0.65,
            35, height * 0.35
        ),

    ]


def build_course_funnel(width, height):
    """
    A pinch-point in the middle of the map: obstacles from both top
    and bottom leave only a narrow central gap, then open back up.
    """

    return [

        Obstacle(
            width * 0.45, 0,
            40, height * 0.42
        ),

        Obstacle(
            width * 0.45, height * 0.58,
            40, height * 0.42
        ),

        Obstacle(
            width * 0.75, height * 0.15,
            35, height * 0.3
        ),

        Obstacle(
            width * 0.75, height * 0.65,
            35, height * 0.3
        ),

    ]


COURSES = [
    build_course_open,
    build_course_zigzag,
    build_course_gauntlet,
    build_course_funnel,
]

COURSE_NAMES = [
    "Open",
    "Zigzag",
    "Gauntlet",
    "Funnel",
]


def get_course(index, width, height):
    """
    Returns (obstacles, name) for the course at this index, wrapping
    around the course list so it can be called with an ever-
    increasing counter.
    """

    course_index = index % len(COURSES)

    obstacles = COURSES[course_index](width, height)
    name = COURSE_NAMES[course_index]

    return obstacles, name


def build_default_course(width, height):
    """
    Kept for backwards compatibility with anything still importing
    this directly; equivalent to the original zigzag layout.
    """

    return build_course_zigzag(width, height)