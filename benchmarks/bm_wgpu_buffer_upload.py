"""
Benchmarks for uploading data with wgpu buffers.
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

N = 100_000_000
nchunks = 1000
unaligned_split_size = N // nchunks
page_size = 4096
aligned_split_size = (unaligned_split_size // page_size) * page_size

##


@benchmark
def make_some_assertions(canvas):

    # This is to show that you cannot simply map a uniform/storage buffer.
    # An auxillary buffer is needed to move the data.

    error_msg = None
    try:
        device.create_buffer(
            size=1000, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.STORAGE
        )
    except wgpu.GPUValidationError as err:
        error_msg = err.message
    assert "usage can only be combined" in error_msg

    error_msg = None
    try:
        device.create_buffer(
            size=1000, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.UNIFORM
        )
    except wgpu.GPUValidationError as err:
        error_msg = err.message
    assert "usage can only be combined" in error_msg

    error_msg = None
    try:
        device.create_buffer(
            size=1000, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.VERTEX
        )
    except wgpu.GPUValidationError as err:
        error_msg = err.message
    assert "usage can only be combined" in error_msg

    yield

    while True:
        yield


##

# A couple of different ways to move data into a storage buffer.

# Simply setting the whole data


@benchmark(20)
def up_wbuf_queue_write_set(canvas):
    return upload_wgpu_buffer_queue_write("set")


@benchmark(20)
def up_wbuf_with_data_set(canvas):
    return upload_wgpu_buffer_with_data("set")


@benchmark(20)
def up_wbuf_write_mapped_set(canvas):
    return upload_wgpu_buffer_write_mapped("set")


# Setting in chunks


@benchmark(20)
def up_wbuf_queue_write_chunked(canvas):
    return upload_wgpu_buffer_queue_write("chunked")


@benchmark(20)
def up_wbuf_with_data_chuncked(canvas):
    return upload_wgpu_buffer_with_data("chunked")


@benchmark(20)
def up_wbuf_write_mapped_chunked(canvas):
    return upload_wgpu_buffer_write_mapped("chunked")


# Setting in chunks, but aligned


@benchmark(20)
def up_wbuf_queue_write_aligned(canvas):
    return upload_wgpu_buffer_queue_write("aligned")


@benchmark(20)
def up_wbuf_with_data_aligned(canvas):
    return upload_wgpu_buffer_with_data("aligned")


@benchmark(20)
def up_wbuf_write_mapped_aligned(canvas):
    return upload_wgpu_buffer_write_mapped("aligned")


# Setting the first quarter only


@benchmark(20)
def up_wbuf_queue_write_quarter1(canvas):
    return upload_wgpu_buffer_queue_write("quarter1")


@benchmark(20)
def up_wbuf_with_data_quarter1(canvas):
    return upload_wgpu_buffer_with_data("quarter1")


@benchmark(20)
def up_wbuf_write_mapped_quarter1(canvas):
    return upload_wgpu_buffer_write_mapped("quarter1")


# Setting the 3d quarter


@benchmark(20)
def up_wbuf_queue_write_quarter3(canvas):
    return upload_wgpu_buffer_queue_write("quarter3")


@benchmark(20)
def up_wbuf_with_data_quarter3(canvas):
    return upload_wgpu_buffer_with_data("quarter3")


@benchmark(20)
def up_wbuf_write_mapped_quarter3(canvas):
    return upload_wgpu_buffer_write_mapped("quarter3")


# Data is the result of a computation


@benchmark(20)
def up_wbuf_queue_write_add(canvas):
    return upload_wgpu_buffer_queue_write("add")


@benchmark(20)
def up_wbuf_write_mapped_add(canvas):
    return upload_wgpu_buffer_write_mapped("add")


@benchmark(20)
def up_wbuf_mapped_range_add(canvas):
    return upload_wgpu_buffer_get_mapped_range("add")


# With a mapped buffer, can precisely update data


@benchmark(20)
def up_wbuf_mapped_range_inter2(canvas):
    return upload_wgpu_buffer_get_mapped_range("inter2")


@benchmark(20)
def up_wbuf_mapped_range_masked2(canvas):
    return upload_wgpu_buffer_get_mapped_range("masked2")


##


def upload_wgpu_buffer_queue_write(math):

    # Upload via the convenience queue.write_buffer()
    # Simplest approach, but also the least flexible.
    # The abstraction allows optimizations under water though, so in certain use-cases it may be the fastest option.

    data1 = np.ones((N,), np.uint8)
    data2 = data1 + 1

    storage_buffer = device.create_buffer(
        size=N, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )

    yield

    while True:
        if math == "set":
            device.queue.write_buffer(storage_buffer, 0, data1, 0, N)
        elif math == "add":
            device.queue.write_buffer(storage_buffer, 0, data1 + data2, 0, N)
        elif math == "chunked":
            n = unaligned_split_size
            for i in range(nchunks):
                device.queue.write_buffer(
                    storage_buffer, i * n, data1[i * n : (i + 1) * n]
                )
        elif math == "aligned":
            n = aligned_split_size
            for i in range(nchunks):
                device.queue.write_buffer(
                    storage_buffer, i * n, data1[i * n : (i + 1) * n]
                )
        elif math == "quarter1":
            n = N // 4
            device.queue.write_buffer(storage_buffer, 0, data1[:n])
        elif math == "quarter3":
            n = N // 4
            device.queue.write_buffer(storage_buffer, 2 * n, data1[:n])
        else:
            assert False

        device.queue.submit([])  # bit of a hack to prevent weird wgpu-core error

        device._poll()  # Wait for GPU to finish queue

        yield


def upload_wgpu_buffer_with_data(math):

    # Upload by mapping and using device.create_buffer_with_data().
    # This avoids waiting for the buffer to be mapped, making it fast in theory.

    data1 = np.ones((N,), np.uint8)
    data2 = data1 + 1

    storage_buffer = device.create_buffer(
        size=N, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )
    tmp_usage = wgpu.BufferUsage.COPY_SRC

    yield

    while True:

        encoder = device.create_command_encoder()

        if math == "set":
            tmp_buffer = device.create_buffer_with_data(data=data1, usage=tmp_usage)
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)
        elif math == "add":
            tmp_buffer = device.create_buffer_with_data(
                data=data1 + data2, usage=tmp_usage
            )
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)
        elif math == "chunked":
            n = unaligned_split_size
            for i in range(nchunks):
                tmp_buffer = device.create_buffer_with_data(
                    data=data1[i * n : (i + 1) * n], usage=tmp_usage
                )
                encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, i * n, n)
        elif math == "aligned":
            n = aligned_split_size
            for i in range(nchunks):
                tmp_buffer = device.create_buffer_with_data(
                    data=data1[i * n : (i + 1) * n], usage=tmp_usage
                )
                encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, i * n, n)
        elif math == "quarter1":
            n = N // 4
            tmp_buffer = device.create_buffer_with_data(data=data1[:n], usage=tmp_usage)
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, n)
        elif math == "quarter3":
            n = N // 4
            tmp_buffer = device.create_buffer_with_data(
                data=data1[2 * n : 3 * n], usage=tmp_usage
            )
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 2 * n, n)
        else:
            assert False

        device.queue.submit([encoder.finish()])
        device._poll()  # Wait for GPU to finish queue

        yield


def upload_wgpu_buffer_write_mapped(math):

    # Upload by mapping and using the safe write_mapped().
    # The call to buffer.map() waits for the queue. When we've gone async, this
    # approach might be faster (in terms of CPU cycles).

    data1 = np.ones((N,), np.uint8)
    data2 = data1 + 1

    storage_buffer = device.create_buffer(
        size=N, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )

    yield

    while True:

        encoder = device.create_command_encoder()

        if math == "set":
            tmp_buffer = device.create_buffer(
                size=N, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            tmp_buffer.write_mapped(data1)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)

        elif math == "add":
            tmp_buffer = device.create_buffer(
                size=N, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            tmp_buffer.write_mapped(data1 + data2)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)

        elif math == "chunked":
            tmp_buffer = device.create_buffer(
                size=N, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            n = unaligned_split_size
            for i in range(nchunks):
                tmp_buffer.write_mapped(data1[i * n : (i + 1) * n], i * n)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)

        elif math == "aligned":
            tmp_buffer = device.create_buffer(
                size=N, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            n = aligned_split_size
            for i in range(nchunks):
                tmp_buffer.write_mapped(data1[i * n : (i + 1) * n], i * n)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)

        elif math == "quarter1":
            n = N // 4
            tmp_buffer = device.create_buffer(
                size=n, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            tmp_buffer.write_mapped(data1[:n], 0, n)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, n)

        elif math == "quarter3":
            n = N // 4
            tmp_buffer = device.create_buffer(
                size=n, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
            )
            tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

            tmp_buffer.write_mapped(data1[2 * n : 3 * n], 0, n)

            tmp_buffer.unmap()
            encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 2 * n, n)

        else:
            assert False

        device.queue.submit([encoder.finish()])
        device._poll()  # Wait for GPU to finish queue

        yield


def upload_wgpu_buffer_get_mapped_range(math):

    # Upload by mapping and using the unsafe get_mapped_range().
    # The call to buffer.map() waits for the queue. When we've gone async, this
    # approach might be faster (in terms of CPU cycles).

    data1 = np.ones((N,), np.uint8)
    data2 = data1 + 1
    mask2 = np.zeros_like(data1, bool)
    mask2[::2] = True

    storage_buffer = device.create_buffer(
        size=N, usage=wgpu.BufferUsage.COPY_DST | wgpu.BufferUsage.STORAGE
    )

    yield

    while True:
        tmp_buffer = device.create_buffer(
            size=N, usage=wgpu.BufferUsage.MAP_WRITE | wgpu.BufferUsage.COPY_SRC
        )
        tmp_buffer.map(wgpu.MapMode.WRITE)  # Waits for gpu with _poll()

        if math == "set":
            mapped_array = tmp_buffer._experimental_get_mapped_range()
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            mapped_array[:] = data1
        elif math == "add":
            mapped_array = tmp_buffer._experimental_get_mapped_range()
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            np.add(data1, data2, out=mapped_array)
        elif math == "chunked":
            n = unaligned_split_size
            for i in range(nchunks):
                mapped_array = tmp_buffer._experimental_get_mapped_range(i * n, n)
                mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
                mapped_array[:] = data1[i * n : (i + 1) * n]
        elif math == "aligned":
            n = aligned_split_size
            for i in range(nchunks):
                mapped_array = tmp_buffer._experimental_get_mapped_range(i * n, n)
                mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
                mapped_array[:] = data1[i * n : (i + 1) * n]
        elif math == "quarter1":
            n = N // 4
            mapped_array = tmp_buffer._experimental_get_mapped_range(0, n)
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            mapped_array[:] = data1[:n]
        elif math == "quarter3":
            n = N // 4
            mapped_array = tmp_buffer._experimental_get_mapped_range(2 * n, n)
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            mapped_array[:] = data1[2 * n : 3 * n]
        elif math == "inter2":
            mapped_array = tmp_buffer._experimental_get_mapped_range()
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            mapped_array[::2] = data1[::2]
        elif math == "masked2":
            mapped_array = tmp_buffer._experimental_get_mapped_range()
            mapped_array = np.frombuffer(mapped_array, dtype=np.uint8)
            mapped_array[mask2] = data1[mask2]
        else:
            assert False

        tmp_buffer.unmap()

        encoder = device.create_command_encoder()
        encoder.copy_buffer_to_buffer(tmp_buffer, 0, storage_buffer, 0, N)
        device.queue.submit([encoder.finish()])

        device._poll()  # Wait for GPU to finish queue

        yield


if __name__ == "__main__":
    run_all(globals())
