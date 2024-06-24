"""
Investigate texture uploads.

I already investigated buffer uploads in detail. I expect a lot of the
results translate to textures. However, textures are different because
they are multi-dimensional. This benchmark gets more insights into that
aspect.
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

def up_wtex_write_mapped(dim, tex_size, chunk_size):

    assert isinstance(dim, int) and dim in (1, 2, 3)
    assert isinstance(tex_size, tuple) and len(tex_size) == 3

    assert tex_size == chunk_size, "only full uploads with this method for now"

    data1 = np.ones(tuple(reversed(tex_size)), np.uint8)

    texture = device.create_texture(
        dimension=dim, size=tex_size, usage=wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING, format=wgpu.TextureFormat.r8unorm
    )

    yield

    while True:

        chunk = data1

        encoder = device.create_command_encoder()

        bytes_per_pixel = 1
        tmp_buffer = device.create_buffer(
            size=chunk.nbytes, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
        )
        tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

        tmp_buffer.write_mapped(chunk)

        tmp_buffer.unmap()
        encoder.copy_buffer_to_texture(
            {"buffer": tmp_buffer, "bytes_per_row": chunk.shape[2] * bytes_per_pixel, "rows_per_image": chunk.shape[1]},
            {"texture": texture},
            copy_size=chunk_size,
        )

        device.queue.submit([encoder.finish()])
        device._poll()  # Wait for GPU to finish queue

        yield


def up_wtex_queue_write(dim, tex_size, chunk_size):

    assert isinstance(dim, int) and dim in (1, 2, 3)
    assert isinstance(tex_size, tuple) and len(tex_size) == 3


    # bpp, nchannels, dtype, format = 1, 1, np.uint8, wgpu.TextureFormat.r8unorm
    bpp, nchannels, dtype, format = 16, 4, np.float32, wgpu.TextureFormat.rgba32float

    np_shape = tuple(reversed(tex_size)) + (nchannels, )
    data1 = np.ones(np_shape, dtype)

    texture = device.create_texture(
        dimension=dim, size=tex_size, usage=wgpu.TextureUsage.COPY_DST | wgpu.TextureUsage.TEXTURE_BINDING, format=format
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
                    origin = ix * chunk_size[0], iy * chunk_size[1], iz * chunk_size[2],
                    chunk = data1[origin[2]:origin[2]+chunk_size[2], origin[1]:origin[1]+chunk_size[1], origin[0]:origin[0]+chunk_size[0]]
                    chunk = np.ascontiguousarray(chunk)
                    device.queue.write_texture(
                        {"texture": texture, "origin": origin},
                        chunk,
                        {"bytes_per_row": chunk.shape[2] * bpp, "rows_per_image": chunk.shape[1]},
                        chunk_size,
                    )

        device.queue.submit([])  # bit of a hack to prevent weird wgpu-core error
        device._poll()  # Wait for GPU to finish queue

        yield


def create_benchmark(func, dim, tex_size, chunk_size, suffix):

    def wrapper():
        return func(dim, tex_size, chunk_size)

    wrapper.__name__ = func.__name__ + suffix
    return benchmark(20)(wrapper)

def run_benchmark_set(func, dim, tex_size):
    b = create_benchmark(func, dim, tex_size, tex_size, f"_{tex_size}")
    b()


def run_benchmark_chunks(dim, tex_size, chunk_size):
    func = up_wtex_queue_write
    b = create_benchmark(func, dim, tex_size, chunk_size, f"_{tex_size}_{chunk_size}")
    b()


if __name__ == "__main__":
    pass

    # print("-- queue_write vs write_mapped")
    #
    # run_benchmark_set(up_wtex_queue_write, 2, (256, 256, 1))
    # run_benchmark_set(up_wtex_queue_write, 2, (512, 512, 1))
    # run_benchmark_set(up_wtex_queue_write, 2, (1024, 1024, 1))
    # run_benchmark_set(up_wtex_queue_write, 2, (2048, 2048, 1))
    #
    #
    # run_benchmark_set(up_wtex_write_mapped, 2, (256, 256, 1))
    # run_benchmark_set(up_wtex_write_mapped, 2, (512, 512, 1))
    # run_benchmark_set(up_wtex_write_mapped, 2, (1024, 1024, 1))
    # run_benchmark_set(up_wtex_write_mapped, 2, (2048, 2048, 1))

    print("-- 1D")

    run_benchmark_chunks(1, (2048, 1, 1), (64, 1, 1))
    run_benchmark_chunks(1, (2048, 1, 1), (128, 1, 1))
    run_benchmark_chunks(1, (2048, 1, 1), (256, 1, 1))
    run_benchmark_chunks(1, (2048, 1, 1), (512, 1, 1))
    run_benchmark_chunks(1, (2048, 1, 1), (1024, 1, 1))
    run_benchmark_chunks(1, (2048, 1, 1), (2048, 1, 1))

    print("-- 2D")

    run_benchmark_chunks(2, (2048, 2048, 1), (64, 64, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (128, 128, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (256, 256, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (512, 512, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (1024, 1024, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 2048, 1))

    print("--")

    run_benchmark_chunks(2, (2048, 2048, 1), (64, 2048, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (128, 2048, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (256, 2048, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (512, 2048, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (1024, 2048, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 2048, 1))

    print("--")

    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 64, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 128, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 256, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 512, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 1024, 1))
    run_benchmark_chunks(2, (2048, 2048, 1), (2048, 2048, 1))


    print("-- 3D")
    size3d = 512, 512, 1024

    run_benchmark_chunks(2, size3d, (64, 64, 64))
    run_benchmark_chunks(2, size3d, (128, 128, 128))
    run_benchmark_chunks(2, size3d, (256, 256, 256))
    run_benchmark_chunks(2, size3d, (512, 512, 512))
    run_benchmark_chunks(2, size3d, (512, 512, 1024))

    print("--")

    run_benchmark_chunks(2, size3d, (32, 512, 1024))
    run_benchmark_chunks(2, size3d, (64, 512, 1024))
    run_benchmark_chunks(2, size3d, (128, 512, 1024))
    run_benchmark_chunks(2, size3d, (256, 512, 1024))
    run_benchmark_chunks(2, size3d, (512, 512, 1024))

    print("--")

    run_benchmark_chunks(2, size3d, (512, 32, 1024))
    run_benchmark_chunks(2, size3d, (512, 64, 1024))
    run_benchmark_chunks(2, size3d, (512, 128, 1024))
    run_benchmark_chunks(2, size3d, (512, 256, 1024))
    run_benchmark_chunks(2, size3d, (512, 512, 1024))

    print("--")

    run_benchmark_chunks(2, size3d, (512, 512, 32))
    run_benchmark_chunks(2, size3d, (512, 512, 64))
    run_benchmark_chunks(2, size3d, (512, 512, 128))
    run_benchmark_chunks(2, size3d, (512, 512, 256))
    run_benchmark_chunks(2, size3d, (512, 512, 512))
    run_benchmark_chunks(2, size3d, (512, 512, 1024))

