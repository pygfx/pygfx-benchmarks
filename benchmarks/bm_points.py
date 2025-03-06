import numpy as np
import pygfx as gfx

from _benchmark import benchmark, run_all

rng = np.random.default_rng()

# An option to add 5 clipping planes to ensure that the clipping code is not
# too slow
five_clipping_planes = rng.random((5, 4), dtype="float32").tolist()
# Twenty should exagerate the clipping code, though it is unclear if it is
# representative of real workloads
twenty_clipping_planes = rng.random((20, 4), dtype="float32").tolist()


def benchmark_points(canvas, n_objects, n_verts, *, clipping_planes=None):
    if clipping_planes is None:
        clipping_planes = []

    renderer = gfx.WgpuRenderer(canvas, blend_mode="ordered2")
    renderer.measure_gpu_times = True

    scene = gfx.Scene()

    x = np.linspace(-480, 480, n_verts, dtype=np.float32)
    y = np.sin(x / 30) * 240
    positions = np.column_stack([x, y, np.zeros_like(x)])

    for i in range(n_objects):
        points = gfx.Points(
            gfx.Geometry(positions=positions),
            gfx.PointsMaterial(
                size=20,
                clipping_planes=clipping_planes,
            ),
        )
        points.local.y = 500 * (i - 0.5 * n_objects) / n_objects
        scene.add(points)

    scene.add(gfx.Background.from_color("#000"))
    camera = gfx.OrthographicCamera(1000, 1000)
    canvas.request_draw(lambda: renderer.render(scene, camera))

    # First draw to load stuff in memory
    canvas._draw_frame_and_present()

    yield None

    while True:
        canvas._draw_frame_and_present()  # includes time to take screenshot
        yield  # renderer.stats["gpu_times"]


# A couple of measurements of 100k points, divided over multiple objects


@benchmark
def benchmark_points_1_100k(canvas):
    # 1 points object with 100000 points
    yield from benchmark_points(canvas, 1, 100_000)


@benchmark
def benchmark_points_1_100k_five_clipping_planes(canvas):
    # 1 points object with 100000 points
    yield from benchmark_points(
        canvas, 1, 100_000, clipping_planes=five_clipping_planes
    )


@benchmark
def benchmark_points_1_100k_twenty_clipping_planes(canvas):
    # 1 points object with 100000 points
    yield from benchmark_points(
        canvas, 1, 100_000, clipping_planes=twenty_clipping_planes
    )


@benchmark
def benchmark_points_100_1000(canvas):
    # 100 points objects with 1000 points each
    yield from benchmark_points(canvas, 100, 1000)


@benchmark
def benchmark_points_100_1000_five_clipping_planes(canvas):
    # 100 points objects with 1000 points each
    yield from benchmark_points(canvas, 100, 1000, clipping_planes=five_clipping_planes)


@benchmark
def benchmark_points_100_1000_twenty_clipping_planes(canvas):
    # 100 points objects with 1000 points each
    yield from benchmark_points(
        canvas, 100, 1000, clipping_planes=twenty_clipping_planes
    )


@benchmark
def benchmark_points_1000_100(canvas):
    # 1000 points objects with 100 points each
    yield from benchmark_points(canvas, 1000, 100)


@benchmark
def benchmark_points_1000_100_five_clipping_planes(canvas):
    # 1000 points objects with 100 points each
    yield from benchmark_points(canvas, 1000, 100, clipping_planes=five_clipping_planes)


@benchmark
def benchmark_points_1000_100_twenty_clipping_planes(canvas):
    # 1000 points objects with 100 points each
    yield from benchmark_points(
        canvas, 1000, 100, clipping_planes=twenty_clipping_planes
    )


# A simple case, and a case of drawing 1M


@benchmark
def benchmark_points_10_10(canvas):
    # 10 points objects with 10 points each
    yield from benchmark_points(canvas, 10, 10)


@benchmark
def benchmark_points_10_10_five_clipping_planes(canvas):
    # 10 points objects with 10 points each
    yield from benchmark_points(canvas, 10, 10, clipping_planes=five_clipping_planes)


@benchmark
def benchmark_points_10_10_twenty_clipping_planes(canvas):
    # 10 points objects with 10 points each
    yield from benchmark_points(canvas, 10, 10, clipping_planes=twenty_clipping_planes)


@benchmark
def benchmark_points_1_1m(canvas):
    # 1 points object with 1mpoints
    yield from benchmark_points(canvas, 1, 1_000_000)


@benchmark
def benchmark_points_1_1m_five_clipping_planes(canvas):
    # 1 points object with 1mpoints
    yield from benchmark_points(
        canvas, 1, 1_000_000, clipping_planes=five_clipping_planes
    )


@benchmark
def benchmark_points_1_1m_twenty_clipping_planes(canvas):
    # 1 points object with 1mpoints
    yield from benchmark_points(
        canvas, 1, 1_000_000, clipping_planes=twenty_clipping_planes
    )


if __name__ == "__main__":
    from wgpu.gui.auto import WgpuCanvas

    c = None  # WgpuCanvas()
    run_all(globals(), c)
