"""
Benchmarks for the per-render scene-graph traversal cost in pygfx.

Background
----------
Historically ``FlatScene`` (pygfx/renderers/wgpu/engine/renderer.py) walked the
entire scene tree on *every* render to:

* bucket objects into lights / shadow casters / renderable objects, and
* propagate ``group_order`` down from each ``Group`` ancestor.

The "incremental scene index" work (pygfx issue #1298) moves that categorization
out of the per-frame hot path: each object keeps a small index of its descendants
that is maintained when the scene graph is *mutated* (add / remove / clear and the
visible / geometry / material / cast_shadow setters), so a steady-state render
loop on an unchanging scene no longer pays the walk.

This file has two parts:

1. ``main()`` -- the headline micro-benchmark. It times ``FlatScene(scene)``
   construction directly (pure CPU, no GPU). This is a *fair* isolation of the
   optimized path: the only work that moved out of the timed region is exactly
   the categorization/propagation the change targets, and on the new code that
   work genuinely happens at mutation time. The numbers therefore reflect the
   recurring per-frame cost of a steady-state loop. (Construction is measured
   after warm-up, so per-object transform/uniform updates -- common to both
   code paths -- have settled and do not bias the ratio.)

2. ``@benchmark`` functions -- a full offscreen-render *control*. At realistic
   sizes the full frame is dominated by GPU submission and per-object uniform
   updates, so the traversal saving is below the render noise floor. These exist
   to demonstrate *no regression* end-to-end and to act as a visual/correctness
   smoke test, NOT to show a speedup.

Run ``python bm_scene_index.py`` to get both.
"""

import gc
import statistics
import time

import numpy as np
import pygfx as gfx

from _benchmark import benchmark, run_all
from pygfx.renderers.wgpu.engine.renderer import FlatScene


# -- shared scene builders ---------------------------------------------------

_POS = np.array([[0, 0, 0]], dtype=np.float32)


def _point():
    return gfx.Points(gfx.Geometry(positions=_POS), gfx.PointsMaterial(size=1))


def build_flat(n_objects):
    """Flat scene: all renderable objects are direct children of the root."""
    scene = gfx.Scene()
    scene.add(gfx.AmbientLight(), gfx.DirectionalLight())
    for _ in range(n_objects):
        scene.add(_point())
    return scene


def build_grouped(n_groups, n_per_group):
    """Grouped scene: objects under sibling Groups (drives group_order)."""
    scene = gfx.Scene()
    scene.add(gfx.AmbientLight(), gfx.DirectionalLight())
    for g_i in range(n_groups):
        g = gfx.Group()
        g.render_order = g_i
        scene.add(g)
        for _ in range(n_per_group):
            g.add(_point())
    return scene


def build_deep(depth, leaves_per_level=1):
    """Deeply nested scene; amplifies per-level traversal / group_order cost."""
    scene = gfx.Scene()
    scene.add(gfx.AmbientLight())
    parent = scene
    for _ in range(depth):
        g = gfx.Group()
        parent.add(g)
        for _ in range(leaves_per_level):
            g.add(_point())
        parent = g
    return scene


# -- part 1: FlatScene construction micro-benchmark (the headline) -----------

def _measure(name, scene, n_iter=200):
    # Warm up: settle per-object transform/uniform updates and renderer-id
    # assignment, which are common to both code paths.
    for _ in range(5):
        FlatScene(scene)

    gc_was_enabled = gc.isenabled()
    gc.disable()  # keep GC pauses out of the per-sample timings
    try:
        samples = []
        for _ in range(n_iter):
            t0 = time.perf_counter_ns()
            FlatScene(scene)
            samples.append(time.perf_counter_ns() - t0)
    finally:
        if gc_was_enabled:
            gc.enable()

    median_us = statistics.median(samples) / 1000
    print(f"{name:<24} median={median_us:>10.2f} us")


def main():
    print("FlatScene() construction -- pure CPU, no GPU\n")
    for n in (500, 2000, 5000, 10000):
        _measure(f"flat_{n}", build_flat(n))
    for n in (50, 200, 500):
        _measure(f"grouped_{n}x10", build_grouped(n, 10))
    for d in (50, 200, 500):
        _measure(f"deep_{d}", build_deep(d))


# -- part 2: full-render control (no-regression / smoke test) ----------------

def _run_render(canvas, scene):
    renderer = gfx.WgpuRenderer(canvas)
    camera = gfx.OrthographicCamera(1000, 1000)
    canvas.request_draw(lambda: renderer.render(scene, camera))
    canvas.force_draw()  # warm
    yield None
    while True:
        canvas.force_draw()
        yield


@benchmark
def benchmark_render_flat_5000(canvas):
    yield from _run_render(canvas, build_flat(5000))


@benchmark
def benchmark_render_grouped_500x10(canvas):
    yield from _run_render(canvas, build_grouped(500, 10))


@benchmark
def benchmark_render_deep_200(canvas):
    yield from _run_render(canvas, build_deep(200))


if __name__ == "__main__":
    main()
    print("\nFull-render control (no-regression; traversal saving is below "
          "the render noise floor)\n")
    run_all(globals(), None)
