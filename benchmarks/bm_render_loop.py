"""
Per-frame render-loop cost: ``FlatScene(scene, view_matrix) + sort()`` for a
large scene, with a *moving* camera (the realistic case — the view matrix
changes every frame) and without a camera (``sort_objects=False``).

This isolates the CPU work the renderer does every frame *before* issuing GPU
draws: categorizing objects, resolving group_order, assigning renderer-ids,
refreshing transforms, computing depth, and sorting. It is what the pygfx
"incremental scene index" + render-loop optimizations target
(pygfx issue #1298, https://github.com/hmaarrfk/pygfx/pull/13).

Run on a checkout of pygfx to measure that revision:

    python bm_render_loop.py            # default 3000 groups x 10 = ~33k objects

The depth sort key only depends on the camera through each object's distance,
so the structural work is camera-independent; see results/scene_index/.
"""

import gc
import statistics
import time

import pygfx as gfx
from pygfx.renderers.wgpu.engine.renderer import FlatScene

from bm_scene_index import build_grouped


def _bench(fn, n=30, warm=5):
    for _ in range(warm):
        fn()
    gc_was_on = gc.isenabled()
    gc.disable()
    try:
        samples = []
        for _ in range(n):
            t0 = time.perf_counter_ns()
            fn()
            samples.append(time.perf_counter_ns() - t0)
    finally:
        if gc_was_on:
            gc.enable()
    return statistics.median(samples) / 1000  # microseconds


def main(n_groups=3000, n_per_group=10):
    scene = build_grouped(n_groups, n_per_group)
    n = n_groups * n_per_group
    print(f"scene: ~{n} renderables ({n_groups} groups x {n_per_group})")

    cam = gfx.PerspectiveCamera(70, 1)
    cam.local.position = (0, 0, 500)
    cam.show_pos((0, 0, 0))
    frame = [0]

    def moving_camera():
        frame[0] += 1
        cam.local.x = frame[0] * 0.5  # camera moves every frame
        flat = FlatScene(scene, cam.view_matrix)
        flat.sort()

    def no_camera():
        flat = FlatScene(scene, None)
        flat.sort()

    print(f"moving-camera : {_bench(moving_camera):10.1f} us")
    print(f"no-camera     : {_bench(no_camera):10.1f} us")


if __name__ == "__main__":
    main()
