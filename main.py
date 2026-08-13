import pygame

from bot import Bot
from evolution import Evolution
from obstacle import get_course
from viz_server import start_server, viz_state


# ============================================================
# Settings
# ============================================================

WIDTH = 1200
HEIGHT = 700

FPS = 60

BOT_COUNT = 50
BOT_RADIUS = 7

GENERATION_TIME = 10

# How many generations a population spends on one obstacle layout
# before rotating to the next. Brains are never reset when this
# happens, only the environment changes, so bots are pushed to
# generalize instead of memorizing one specific gap pattern.
COURSE_ROTATION_INTERVAL = 10

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

id_font = pygame.font.SysFont(
    "Arial",
    12
)


# ============================================================
# Create bots
# ============================================================

bots = [
    Bot(
        WIDTH,
        HEIGHT,
        BOT_RADIUS,
        bot_id=i
    )
    for i in range(BOT_COUNT)
]

evolution = Evolution(
    bots
)

goal = Goal()

course_index = 0

obstacles, course_name = get_course(
    course_index,
    WIDTH,
    HEIGHT
)


# ============================================================
# Brain viewer server
# ============================================================
#
# Runs in a background thread. The PHP page (run separately with
# e.g. `php -S localhost:8000` inside viz_php/) polls this over
# HTTP to show what a selected bot is "thinking".

start_server(port=8765)

viz_state.set_bots(bots)
viz_state.set_evolution(evolution)
viz_state.set_world(WIDTH, HEIGHT, goal, obstacles, BOT_RADIUS)


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

        # Rotate the obstacle course every N generations. Bots keep
        # their brains (mutation/reset already happened inside
        # evolve()), only the environment around them changes.
        if evolution.generation % COURSE_ROTATION_INTERVAL == 0:

            course_index += 1

            obstacles, course_name = get_course(
                course_index,
                WIDTH,
                HEIGHT
            )

            viz_state.set_world(WIDTH, HEIGHT, goal, obstacles, BOT_RADIUS)

    # New generation may be a new list (even if same Bot objects),
    # so keep the viz server pointed at the current one every frame.
    viz_state.set_bots(bots)

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
                show_rays=show_rays,
                id_font=id_font
            )

        else:

            bot.draw(
                screen,
                BOT_COLOR,
                id_font=id_font
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

    generations_until_rotation = (
        COURSE_ROTATION_INTERVAL -
        (evolution.generation % COURSE_ROTATION_INTERVAL)
    )

    course_text = font.render(
        f"Course: {course_name} (next in {generations_until_rotation} gen)",
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

    screen.blit(
        course_text,
        (20, 145)
    )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(
        FPS
    )


pygame.quit()