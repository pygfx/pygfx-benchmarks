"""
Investigate the optimal chunk size for uploading data.

There are various parameters that affect performance:

* The machine and GPU type.
* The upload approach.
* The pattern of what elements must be uploaded.
* The full buffer size.
* The chunk size.

I hope to get an indication of the optimal chunk size, perhaps depending
on one of the other parameters, though ideally a value that works good
(enough) accross the spectrum.
"""


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


def update_resource(resource):
    _update_resource(resource)
    get_shared().device._poll()  # Wait for GPU to finish


# Global device
device = wgpu.gpu.request_adapter(power_preference="high-performance").request_device()
print(device.adapter.summary)

##

def up_wbuf_queue_write(buffer_size, chunk_size):

    data1 = np.ones((buffer_size,), np.uint8)

    storage_buffer = device.create_buffer(
        size=buffer_size, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )

    nchunks = buffer_size // chunk_size
    n = chunk_size
    if nchunks <= 1:
        nchunks = 1
        n = buffer_size

    yield

    while True:

        for i in range(0, nchunks, 1):
            device.queue.write_buffer(
                storage_buffer, i * n, data1[i * n : (i + 1) * n]
            )

        device.queue.submit([])  # bit of a hack to prevent weird wgpu-core error
        device._poll()  # Wait for GPU to finish queue

        yield


def up_wbuf_write_mapped(buffer_size, chunk_size):

    data1 = np.ones((buffer_size,), np.uint8)

    storage_buffer = device.create_buffer(
        size=buffer_size, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )

    nchunks = buffer_size // chunk_size
    n = chunk_size
    if nchunks <= 1:
        nchunks = 1
        n = buffer_size

    yield

    while True:

        # todo: oh, kak, die temp buffer moet voor elke chunk ...
        # todo: maar in de praktijk kun je met dat mappen nog wel iets aan de range doen ofzo.
        encoder = device.create_command_encoder()

        tmp_buffer = device.create_buffer(
            size=buffer_size, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
        )
        tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

        for i in range(0, nchunks, 1):
            tmp_buffer.write_mapped(data1[i * n : (i + 1) * n], i * n)

        tmp_buffer.unmap()
        encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, buffer_size)

        device.queue.submit([encoder.finish()])
        device._poll()  # Wait for GPU to finish queue

        yield

##

def create_benchmark(func, buffer_size2, chunk_size2):

    def wrapper():
        return func(2**buffer_size2, 2**chunk_size2)

    wrapper.__name__ = func.__name__ + f"_{buffer_size2}_{chunk_size2}"
    return benchmark(20)(wrapper)

def run_benchmarks(func, buffer_size2, chunk_size2_start, chunk_size2_end):
    for chunk_size2 in range(chunk_size2_start, chunk_size2_end):
        b = create_benchmark(func, buffer_size2, chunk_size2)
        b()


if __name__ == "__main__":
    # run_benchmarks(up_wbuf_queue_write, 15, 6, 16)
    # run_benchmarks(up_wbuf_write_mapped, 15, 6, 16)

    # run_benchmarks(up_wbuf_queue_write, 20, 10, 20)
    # run_benchmarks(up_wbuf_write_mapped, 20, 10, 18)

    # run_benchmarks(up_wbuf_queue_write, 25, 12, 22)
    # run_benchmarks(up_wbuf_write_mapped, 25, 12, 22)

    run_benchmarks(up_wbuf_queue_write, 28, 14, 24)
    run_benchmarks(up_wbuf_write_mapped, 28, 14, 24)

    # run_benchmarks(up_wbuf_queue_write, 30, 17, 30)
    # run_benchmarks(up_wbuf_write_mapped, 30, 17, 30)


