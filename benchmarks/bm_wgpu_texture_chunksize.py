"""
Investigate chunking for texture uploads.

I already investigated buffer uploads. Textures are different because
they are multi-dimensional. How best to chose the chunks in this case?
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

def up_wtex_queue_write(dim, tex_size, chunk_size):

    assert isinstance(dim, int) and dim in (1, 2, 3)
    assert isinstance(tex_size, tuple) and len(tex_size) == 3

    data1 = np.ones(tuple(reversed(tex_size)), np.uint8)

    texture = device.create_texture(
        dimension=dim, size=tex_size, usage=wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING, format=wgpu.TextureFormat.r8unorm
    )

    # Get number of chunks in each dimension
    nchunks = [1, 1, 1]
    chunk_size = list(chunk_size)
    for i in range(3):
        nchunks[i] = tex_size[i] // chunk_size[i]
        if  nchunks[i] <= 1:
            nchunks[i] = 1
            chunk_size[i] = tex_size[i]

    while True:

        for iz in range(nchunks[2]):
            for iy in range(nchunks[1]):
                for ix in range(nchunks[0]):
                    bytes_per_pixel = 1
                    origin = ix * chunk_size[0], iy * chunk_size[1], iz * chunk_size[2],
                    chunk = data1[origin[2]:origin[2]+chunk_size[2], origin[1]:origin[1]+chunk_size[1], origin[0]:origin[0]+chunk_size[0]]
                    chunk = np.ascontiguousarray(chunk)
                    device.queue.write_texture(
                        {"texture": texture, "origin": origin},
                        chunk,
                        {"bytes_per_row": chunk.shape[2] * bytes_per_pixel, "rows_per_image": chunk.shape[1]},
                        chunk_size,
                    )

        device.queue.submit([])  # bit of a hack to prevent weird wgpu-core error
        device._poll()  # Wait for GPU to finish queue

        yield


def create_benchmark(func, dim, tex_size, chunk_size):

    def wrapper():
        return func(dim, tex_size, chunk_size)

    wrapper.__name__ = func.__name__ + f"_{tex_size}_{chunk_size}"
    return benchmark(20)(wrapper)

def run_benchmarks(dim, tex_size, chunk_size):
    func = up_wtex_queue_write
    b = create_benchmark(func, dim, tex_size, chunk_size)
    b()
    # for chunk_size2 in range(chunk_size, chunk_size2_end):
    #     b = create_benchmark(func, tex_size, chunk_size2)
    #     b()


if __name__ == "__main__":
    pass

    run_benchmarks(1, (2048, 1, 1), (64, 1, 1))
    run_benchmarks(1, (2048, 1, 1), (128, 1, 1))
    run_benchmarks(1, (2048, 1, 1), (256, 1, 1))
    run_benchmarks(1, (2048, 1, 1), (512, 1, 1))
    run_benchmarks(1, (2048, 1, 1), (1024, 1, 1))
    run_benchmarks(1, (2048, 1, 1), (2048, 1, 1))

    print("--")

    run_benchmarks(2, (2048, 2048, 1), (64, 64, 1))
    run_benchmarks(2, (2048, 2048, 1), (128, 128, 1))
    run_benchmarks(2, (2048, 2048, 1), (256, 256, 1))
    run_benchmarks(2, (2048, 2048, 1), (512, 512, 1))
    run_benchmarks(2, (2048, 2048, 1), (1024, 1024, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 2048, 1))

    print("--")

    run_benchmarks(2, (2048, 2048, 1), (64, 2048, 1))
    run_benchmarks(2, (2048, 2048, 1), (128, 2048, 1))
    run_benchmarks(2, (2048, 2048, 1), (256, 2048, 1))
    run_benchmarks(2, (2048, 2048, 1), (512, 2048, 1))
    run_benchmarks(2, (2048, 2048, 1), (1024, 2048, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 2048, 1))

    print("--")

    run_benchmarks(2, (2048, 2048, 1), (2048, 64, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 128, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 256, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 512, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 1024, 1))
    run_benchmarks(2, (2048, 2048, 1), (2048, 2048, 1))



