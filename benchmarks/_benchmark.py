"""
Utilities for doing benchmarks.
"""

import gc
import time

import numpy as np
from wgpu.gui.offscreen import WgpuCanvas as OffscreenWgpuCanvas, run
import pygfx as gfx

gfx.renderers.wgpu.enable_wgpu_features("timestamp-query")


def benchmark(func):
    """Decorator for benchmark functions."""

    if isinstance(func, int):
        n_timings = func
    else:
        n_timings = 10

    def outer(func):

        def inner(*args):

            # Do somewhat of a reset
            for _ in range(3):
                gc.collect()
                time.sleep(0.02)

            # Boot the generator.
            generator = func(*args)

            # Seed: the generator does its preparations.
            generator.__next__()

            # Do a few warmup iters. In practice the first iter or two tends to take more time than the rest.
            generator.__next__()
            generator.__next__()

            # Do measurements
            times = {}
            for iter in range(n_timings):
                # time.sleep(0) # so weird, if I sleep for 0.1, some tests take longer??
                t0 = time.perf_counter_ns()
                extra_times = generator.__next__()
                t1 = time.perf_counter_ns()
                times.setdefault("cpu", []).append((t1 - t0))
                if extra_times:
                    for k, t in extra_times.items():
                        times.setdefault(k, []).append(t)

            # Process results
            stats_str = ""
            for k in times.keys():
                tt = [t / 1000_000 for t in times[k]]
                mean_str = f"{np.mean(tt):0.2f}".rjust(6)
                stats_str += f"  {k.strip()}:{mean_str}"
                # if len(times) == 1:
                #     stats_str += f" ± {np.std(tt):0.2f}".ljust(6)
                #     stats_str += str(tt)
            stats_str = stats_str.lstrip(" ")

            # Show results
            name = func.__name__
            if name.startswith("benchmark_"):
                name = name[10:]
            # print([t / 1000_000  for t in times["cpu"]])
            print(f"{name.rjust(30)} ({n_timings}x) - {stats_str}")

        inner.__name__ == func.__name__
        inner.is_benchmark = True
        return inner

    if callable(func):
        return outer(func)
    elif isinstance(func, int):
        return outer
    else:
        raise TypeError("Unexpected use of @benchmark")


def run_all(dict, canvas=None):
    """To put at the bottom of each benchmark file."""
    benchmark_funcs = []
    for ob in dict.values():
        if callable(ob) and getattr(ob, "is_benchmark", False):
            benchmark_funcs.append(ob)

    if canvas is None:
        canvas = OffscreenWgpuCanvas()

    for func in benchmark_funcs:
        func(canvas)
