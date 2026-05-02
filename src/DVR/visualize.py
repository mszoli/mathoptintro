import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button
from .settings import RESTAURANT

COURIER_COLORS = ["tab:blue", "tab:orange", "tab:purple", "tab:brown", "tab:pink"]
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

EMPTY = np.empty((0, 2))


def load(results_dir: str):
    with open(os.path.join(results_dir, "orders.json")) as f:
        orders = json.load(f)
    with open(os.path.join(results_dir, "routes.json")) as f:
        routes = json.load(f)
    return orders, routes


def route_waypoints(route: dict) -> list:
    pts = [(route["departure_time"], RESTAURANT)]
    for stop in route["stops"]:
        pts.append((stop["delivery_time"], stop["location"]))
    pts.append((route["return_time"], RESTAURANT))
    return pts


def courier_pos_at(waypoints: list, t: int):
    for i in range(len(waypoints) - 1):
        t0, loc0 = waypoints[i]
        t1, loc1 = waypoints[i + 1]
        if t0 <= t <= t1:
            alpha = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return (loc0[0] + alpha * (loc1[0] - loc0[0]),
                    loc0[1] + alpha * (loc1[1] - loc0[1]))
    return None


def path_so_far(waypoints: list, t: int) -> list:
    path = []
    for i in range(len(waypoints) - 1):
        t0, loc0 = waypoints[i]
        t1, loc1 = waypoints[i + 1]
        if not path:
            path.append(loc0)
        if t >= t1:
            path.append(loc1)
        elif t >= t0:
            alpha = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            path.append((loc0[0] + alpha * (loc1[0] - loc0[0]),
                         loc0[1] + alpha * (loc1[1] - loc0[1])))
            break
    return path


def show(name: str, step: int = 1):
    results_dir = os.path.join(RESULTS_DIR, name)
    orders, routes = load(results_dir)

    delivery_return = {}
    for r in routes:
        for stop in r["stops"]:
            delivery_return[stop["order_id"]] = r["return_time"]

    max_time = max(
        (r["return_time"] for r in routes),
        default=max(o["arrival_time"] for o in orders),
    )
    frames = [i * step for i in range(int(max_time / step) + 2)]

    courier_ids = sorted(set(r["courier_id"] for r in routes))
    n_couriers = len(courier_ids)

    fig, ax = plt.subplots(figsize=(7, 7))
    plt.subplots_adjust(bottom=0.18)

    ax.set_xlim(-1, 31)
    ax.set_ylim(-1, 31)
    ax.set_aspect("equal")
    ax.set_title(name)
    ax.plot(*RESTAURANT, "ks", markersize=10, zorder=5)

    order_scatter = ax.scatter([], [], s=60, zorder=3)
    courier_scatters = [
        ax.scatter([], [], s=120, marker="^", color=COURIER_COLORS[i % len(COURIER_COLORS)], zorder=4)
        for i in range(n_couriers)
    ]
    courier_lines = [
        ax.plot([], [], "-", color=COURIER_COLORS[i % len(COURIER_COLORS)], lw=1.5, alpha=0.6, zorder=2)[0]
        for i in range(n_couriers)
    ]
    time_text = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top")

    ax_slider = plt.axes([0.15, 0.08, 0.7, 0.03])
    slider = Slider(ax_slider, "t", 0, frames[-1], valinit=0, valstep=step)

    ax_button = plt.axes([0.45, 0.02, 0.1, 0.04])
    button = Button(ax_button, "Play")

    state = {"playing": False, "frame_idx": 0}

    def draw(t: int):
        visible = [
            o for o in orders
            if o["arrival_time"] <= t
            and not (
                o["delivery_time"] is not None
                and delivery_return.get(o["id"], t) <= t
            )
        ]
        if visible:
            xs = [o["location"][0] for o in visible]
            ys = [o["location"][1] for o in visible]
            colors = [
                "red" if o["cancelled"]
                else "green" if o["delivery_time"] is not None and o["delivery_time"] <= t
                else "gold"
                for o in visible
            ]
            order_scatter.set_offsets(np.column_stack([xs, ys]))
            order_scatter.set_color(colors)
        else:
            order_scatter.set_offsets(EMPTY)

        for i, cid in enumerate(courier_ids):
            active = [r for r in routes if r["courier_id"] == cid and r["departure_time"] <= t <= r["return_time"]]
            if active:
                wps = route_waypoints(active[-1])
                pos = courier_pos_at(wps, t)
                courier_scatters[i].set_offsets(np.array([pos]) if pos else EMPTY)
                path = path_so_far(wps, t)
                if len(path) >= 2:
                    xs_p, ys_p = zip(*path)
                    courier_lines[i].set_data(xs_p, ys_p)
                else:
                    courier_lines[i].set_data([], [])
            else:
                courier_scatters[i].set_offsets(EMPTY)
                courier_lines[i].set_data([], [])

        time_text.set_text(f"t = {t:.0f}")

        slider.eventson = False
        slider.set_val(t)
        slider.eventson = True

        fig.canvas.draw_idle()

    def update(_):
        if not state["playing"]:
            return
        state["frame_idx"] = (state["frame_idx"] + 1) % len(frames)
        draw(frames[state["frame_idx"]])

    def on_slider(val):
        state["frame_idx"] = min(range(len(frames)), key=lambda i: abs(frames[i] - val))
        draw(frames[state["frame_idx"]])

    def on_button(_):
        state["playing"] = not state["playing"]
        button.label.set_text("Pause" if state["playing"] else "Play")

    slider.on_changed(on_slider)
    button.on_clicked(on_button)

    ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)
    state["ani"] = ani
    draw(0)
    plt.show()


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "greedy_1by1"
    show(name)
