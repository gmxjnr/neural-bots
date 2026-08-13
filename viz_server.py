import json
import threading

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class VizState:
    """
    Simple shared container holding a reference to the current bots
    list. This is a debug/visualization tool, not safety-critical
    code, so we keep this deliberately simple: swapping a reference
    is atomic enough under the GIL for our purposes here.
    """

    def __init__(self):
        self.bots = []
        self.evolution = None

        # Static-ish world info (changes only on course rotation),
        # used by the public live simulation view.
        self.width = 0
        self.height = 0
        self.goal = None
        self.obstacles = []
        self.bot_radius = 7

    def set_bots(self, bots):
        self.bots = bots

    def set_evolution(self, evolution):
        self.evolution = evolution

    def set_world(self, width, height, goal, obstacles, bot_radius):
        self.width = width
        self.height = height
        self.goal = goal
        self.obstacles = obstacles
        self.bot_radius = bot_radius


viz_state = VizState()


class VizRequestHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):

        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")

        # Allow the PHP page (different port) to fetch this directly
        # from the browser without a proxy.
        self.send_header("Access-Control-Allow-Origin", "*")

        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/bots":

            self._handle_bots_list()

        elif self.path == "/stats":

            self._handle_stats()

        elif self.path == "/world":

            self._handle_world()

        elif self.path.startswith("/bot/"):

            self._handle_bot_detail()

        else:

            self._send_json(
                {"error": "not found"},
                status=404
            )

    def _handle_world(self):

        goal = viz_state.goal

        self._send_json(
            {
                "width": viz_state.width,
                "height": viz_state.height,
                "bot_radius": viz_state.bot_radius,
                "goal": (
                    {"x": goal.x, "y": goal.y, "radius": goal.radius}
                    if goal is not None else None
                ),
                "obstacles": [
                    {
                        "x": obstacle.rect.x,
                        "y": obstacle.rect.y,
                        "width": obstacle.rect.width,
                        "height": obstacle.rect.height
                    }
                    for obstacle in viz_state.obstacles
                ]
            }
        )

    def _handle_stats(self):

        evolution = viz_state.evolution

        if evolution is None:
            self._send_json({"generation": 0, "history": []})
            return

        self._send_json(
            {
                "generation": evolution.generation,
                "best_fitness": round(evolution.best_fitness, 3),
                "average_fitness": round(evolution.average_fitness, 3),
                "history": evolution.history
            }
        )

    def _handle_bots_list(self):

        bots = viz_state.bots

        best_id = None

        if bots:

            best_bot = max(
                bots,
                key=lambda bot: bot.calculate_fitness()
            )

            best_id = best_bot.id

        payload = [
            {
                "id": bot.id,
                "x": round(bot.x, 1),
                "y": round(bot.y, 1),
                "angle": round(bot.angle, 3),
                "alive": bot.alive,
                "reached_goal": bot.reached_goal,
                "hit_obstacle": bot.hit_obstacle,
                "fitness": round(bot.calculate_fitness(), 3),
                "is_best": bot.id == best_id
            }
            for bot in bots
        ]

        self._send_json(payload)

    def _handle_bot_detail(self):

        bots = viz_state.bots

        try:
            bot_id = int(self.path.split("/bot/")[1])
        except (IndexError, ValueError):
            self._send_json({"error": "invalid id"}, status=400)
            return

        bot = next(
            (b for b in bots if b.id == bot_id),
            None
        )

        if bot is None:
            self._send_json({"error": "not found"}, status=404)
            return

        brain = bot.brain

        payload = {
            "id": bot.id,
            "alive": bot.alive,
            "reached_goal": bot.reached_goal,
            "hit_obstacle": bot.hit_obstacle,
            "fitness": round(bot.calculate_fitness(), 3),

            "inputs": (
                brain.last_inputs.tolist()
                if brain.last_inputs is not None else []
            ),
            "hidden": (
                brain.last_hidden.tolist()
                if brain.last_hidden is not None else []
            ),
            "outputs": (
                brain.last_outputs.tolist()
                if brain.last_outputs is not None else []
            ),

            "weights_input_hidden": brain.weights_input_hidden.tolist(),
            "weights_hidden_output": brain.weights_hidden_output.tolist(),
        }

        self._send_json(payload)

    def log_message(self, format, *args):
        # Silence default request logging, it would otherwise spam
        # the terminal alongside the pygame output every poll.
        pass


def start_server(port=8765):

    server = ThreadingHTTPServer(
        ("localhost", port),
        VizRequestHandler
    )

    thread = threading.Thread(
        target=server.serve_forever,
        daemon=True
    )

    thread.start()

    print(f"[viz] Brain viewer server running on http://localhost:{port}")

    return server