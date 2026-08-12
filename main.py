import pygame

from bot import Bot
from evolution import Evolution
from obstacle import build_default_course


# ============================================================
# Settings
# ============================================================

WIDTH = 1200
HEIGHT = 700

FPS = 60

BOT_COUNT = 50
BOT_RADIUS = 7

GENERATION_TIME = 10

BACKGROUND = (15, 17, 24)

BOT_COLOR = (80, 180, 255)
BEST_BOT_COLOR = (255, 210, 80)

GOAL_COLOR = (80, 255, 140)


# ============================================================
# Goal
# ============================================================

class Goal:

    def __init__(self):

        self.x = WIDTH - 80
        self.y = HEIGHT // 2

        self.radius = 18

    def draw(self, screen):

        pygame.draw.circle(
            screen,
            GOAL_COLOR,
            (
                self.x,
                self.y
            ),
            self.radius
        )

        pygame.draw.circle(
            screen,
            BACKGROUND,
            (
                self.x,
                self.y
            ),
            self.radius - 5
        )


# ============================================================
# Pygame
# ============================================================

pygame.init()

screen = pygame.display.set_mode(
    (
        WIDTH,
        HEIGHT
    )
)

pygame.display.set_caption(
    "Neural Bots"
)

clock = pygame.time.Clock()


# ============================================================
# Font
# ============================================================

font = pygame.font.SysFont(
    "Arial",
    20
)


# ============================================================
# Create bots
# ============================================================

bots = [
    Bot(
        WIDTH,
        HEIGHT,
        BOT_RADIUS
    )
    for _ in range(BOT_COUNT)
]

evolution = Evolution(
    bots
)

goal = Goal()

obstacles = build_default_course(
    WIDTH,
    HEIGHT
)


# ============================================================
# Generation timer
# ============================================================

generation_timer = 0

show_rays = False


# ============================================================
# Main loop
# ============================================================

running = True

while running:

    # --------------------------------------------------------
    # Events
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_t:

                show_rays = not show_rays

    # --------------------------------------------------------
    # Update bots
    # --------------------------------------------------------

    for bot in bots:

        bot.update(
            goal,
            obstacles
        )

    # --------------------------------------------------------
    # Generation timer
    # --------------------------------------------------------

    generation_timer += 1 / FPS

    if generation_timer >= GENERATION_TIME:

        evolution.bots = bots

        evolution.evolve()

        bots = evolution.bots

        generation_timer = 0

    # --------------------------------------------------------
    # Draw
    # --------------------------------------------------------

    screen.fill(
        BACKGROUND
    )

    for obstacle in obstacles:

        obstacle.draw(
            screen
        )

    goal.draw(
        screen
    )

    # Find best bot
    best_bot = max(
        bots,
        key=lambda bot: bot.calculate_fitness()
    )

    # Draw bots
    for bot in bots:

        if bot == best_bot:

            bot.draw(
                screen,
                BEST_BOT_COLOR,
                show_rays=show_rays
            )

        else:

            bot.draw(
                screen,
                BOT_COLOR
            )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    generation_text = font.render(
        f"Generation: {evolution.generation}",
        True,
        (230, 230, 230)
    )

    best_text = font.render(
        f"Best fitness: {evolution.best_fitness:.3f}",
        True,
        (230, 230, 230)
    )

    average_text = font.render(
        f"Average fitness: {evolution.average_fitness:.3f}",
        True,
        (230, 230, 230)
    )

    time_text = font.render(
        f"Next generation: {GENERATION_TIME - generation_timer:.1f}s",
        True,
        (230, 230, 230)
    )

    rays_text = font.render(
        "Rays (best bot): ON [T]" if show_rays else "Rays (best bot): OFF [T]",
        True,
        (150, 150, 160)
    )

    screen.blit(
        generation_text,
        (20, 20)
    )

    screen.blit(
        best_text,
        (20, 45)
    )

    screen.blit(
        average_text,
        (20, 70)
    )

    screen.blit(
        time_text,
        (20, 95)
    )

    screen.blit(
        rays_text,
        (20, 120)
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(
        FPS
    )


pygame.quit()