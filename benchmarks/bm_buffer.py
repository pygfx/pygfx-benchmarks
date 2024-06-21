import time

import numpy as np
import wgpu
import pygfx as gfx
from pygfx.renderers.wgpu.engine.update import (
    ensure_wgpu_object,
    update_resource as _update_resource,
)
from pygfx.renderers.wgpu import get_shared

from _benchmark import benchmark, run_all


N = 100_000_000


def update_resource(resource):
    _update_resource(resource)
    get_shared().device._poll()  # Wait for GPU to finish


@benchmark(20)
def upload_buffer_full_naive(canvas):
    # Emulate updating a pretty big buffer

    data1 = np.zeros((N,), np.uint8)
    data2 = np.ones((N,), np.uint8)

    buffer = gfx.Buffer(data1)
    ensure_wgpu_object(buffer)
    update_resource(buffer)

    yield

    while True:
        buffer.data[:] = data2
        buffer.update_range()
        update_resource(buffer)
        yield


@benchmark(20)
def upload_buffer_full_optimized(canvas):
    # Emulate updating a pretty big buffer, replacing full data if possible

    data1 = np.zeros((N,), np.uint8)
    data2 = np.ones((N,), np.uint8)

    buffer = gfx.Buffer(data1)
    ensure_wgpu_object(buffer)
    update_resource(buffer)

    yield

    while True:
        if hasattr(buffer, "set_data"):
            # buffer.set_data(data2)
            # buffer._chunk_map.fill(True)
            # buffer._chunks_any_dirty = True
            buffer.update_full()
        else:
            buffer.data[:] = data2
            buffer.update_range()
        update_resource(buffer)
        yield


@benchmark(20)
def upload_buffer_full_noncont(canvas):
    # Emulate updating a pretty big buffer

    data1 = np.zeros((N*2,), np.uint8)[::2]
    data2 = np.ones((N*2,), np.uint8)[::2]

    buffer = gfx.Buffer(data1)
    ensure_wgpu_object(buffer)
    update_resource(buffer)

    yield

    while True:
        if hasattr(buffer, "set_data"):
            buffer.set_data(data1)
        else:
            buffer.data[:] = data2
            buffer.update_range()
        update_resource(buffer)
        yield


@benchmark(20)
def upload_buffer_half(canvas):
    # Emulate updating a pretty big buffer

    data1 = np.zeros((N), np.uint8)
    data2 = np.ones((N), np.uint8)

    buffer = gfx.Buffer(data1)
    ensure_wgpu_object(buffer)
    update_resource(buffer)

    yield

    while True:

        buffer.data[: N // 2] = data1[: N // 2]
        buffer.update_range(0, N // 2)

        data1, data2 = data2, data1

        update_resource(buffer)
        yield


@benchmark(20)
def upload_buffer_two_quarters(canvas):
    # Emulate updating a pretty big buffer

    data1 = np.zeros((N,), np.uint8)
    data2 = np.ones((N,), np.uint8)

    buffer = gfx.Buffer(data1)
    ensure_wgpu_object(buffer)
    update_resource(buffer)

    yield

    while True:
        buffer.data[: N // 4] = data1[: N // 4]
        buffer.update_range(0, N // 4)
        buffer.data[-N // 4 :] = data1[-N // 4 :]
        buffer.update_range(3 * N // 4, N)

        data1, data2 = data2, data1

        update_resource(buffer)
        yield


@benchmark(20)
def upload_100_buffers(canvas):
    # This emulates updating a bunch of uniform buffers

    buffers = []
    nbuffers = 100
    for i in range(nbuffers):
        data = np.zeros((N // nbuffers,), np.uint8)
        buffer = gfx.Buffer(data)
        buffers.append(buffer)

    for buffer in buffers:
        ensure_wgpu_object(buffer)
        update_resource(buffer)

    yield

    while True:

        for buffer in buffers:
            buffer.update_range()
            update_resource(buffer)
        yield


if __name__ == "__main__":
    run_all(globals())
