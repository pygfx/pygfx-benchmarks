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


## 1D


N1 = 16384  # max texture size


@benchmark(20)
def upload_tex1d_full_naive(canvas):
    # Emulate updating a texture in full, but the silly way

    data1 = np.zeros((N1, 4), np.float32)
    data2 = np.ones((N1, 4), np.float32)

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:] = data2
        tex.update_range((0, 0, 0), (N1, 1, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex1d_full_optimized(canvas):
    # Emulate updating a texture im full, the proper way

    data1 = np.zeros((N1, 4), np.float32)
    data2 = np.zeros((N1, 4), np.float32)

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data2)
            tex.update_full()
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), (N1, 1, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex1d_full_noncont(canvas):
    # Emulate updating a texture im full, with non-contiguous data

    data1 = np.zeros((N1 * 2, 4), np.float32)[::2]
    data2 = np.ones((N1 * 2, 4), np.float32)[::2]

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data1)
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), (N1, 1, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex1d_quarter_x(canvas):
    # Emulate updating quarter of the texture data

    data1 = np.zeros((N1, 4), np.float32)

    n = N1 // 4

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:n] = data1[:n]
        tex.update_range((0, 0, 0), (n, 1, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex1d_two_eights_x(canvas):
    # Emulate updating two eights of texture data

    data1 = np.zeros((N1, 4), np.float32)

    n = N1 // 8

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[offset:offset+n] = data1[offset :offset+n]
            tex.update_range((offset, 0, 0), (n, 1, 1))

        update_resource(tex)
        yield


@benchmark(20)
def divider1(canvas):
    yield
    while True:
        yield


## 2D

N2 = 4000


@benchmark(20)
def upload_tex2d_full_naive(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.ones((N2, N2, 4), np.uint8)

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:] = data2
        tex.update_range((0, 0, 0), (N2, N2, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_full_optimized(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.zeros((N2, N2, 4), np.uint8)

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data2)
            tex.update_full()
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), (N2, N2, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_full_noncont(canvas):

    data1 = np.zeros((N2 * 2, N2 * 2, 4), np.uint8)[::2, ::2]
    data2 = np.ones((N2 * 2, N2 * 2, 4), np.uint8)[::2, ::2]

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data1)
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), (N2, N2, 1))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_quarter_x(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 4
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:, :n] = data1[:, :n]
        tex.update_range((0, 0, 0), (n, N2, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_quarter_y(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 4
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:n, :] = data1[:n, :]
        tex.update_range((0, 0, 0), (N2, n, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_two_eights_x(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 8
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[:, offset:offset+n] = data1[:, offset :offset+n]
            tex.update_range((offset, 0, 0), (n, N2, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_two_eights_y(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 8
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[offset:offset+n,:] = data1[offset :offset+n,:]
            tex.update_range((0, offset, 0), (N2, n, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_four_eights_x(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 8
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(4):
            offset = (2 * i) * n
            # tex.data[:, offset:offset+n] = data1[:, offset :offset+n]
            tex.update_range((offset, 0, 0), (n, N2, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_four_eights_y(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    n = N2 // 8
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(4):
            offset = (2 * i) * n
            # tex.data[offset:offset+n,:] = data1[offset :offset+n,:]
            tex.update_range((0, offset, 0), (N2, n, 1))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_chunk_stripes_x(canvas):
    # Emulate the worst-case stripe scenario

    data1 = np.zeros((N2, N2, 4), np.uint8)

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    step = tex._chunk_size[0] * 2  # every other chunk

    yield

    while True:
        tex.update_indices(np.arange(0, N2, step), None, None)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_chunk_stripes_y(canvas):
    # Emulate the worst-case stripe scenario

    data1 = np.zeros((N2, N2, 4), np.uint8)

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    step = tex._chunk_size[1] * 2  # every other chunk

    yield

    while True:
        tex.update_indices(None, np.arange(0, N2, step), None)
        update_resource(tex)
        yield


def upload_tex2d_random(n_random):

    data1 = np.zeros((N2, N2, 4), np.uint8)

    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        xx = np.random.randint(0, N2, n_random)
        yy = np.random.randint(0, N2, n_random)
        # tex.data[yy,xx] = 1
        tex.update_indices(xx, yy, None)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_random8(canvas):
    return upload_tex2d_random(8)


@benchmark(20)
def upload_tex2d_random16(canvas):
    return upload_tex2d_random(16)


@benchmark(20)
def upload_tex2d_random32(canvas):
    return upload_tex2d_random(32)


@benchmark(20)
def upload_tex2d_random64(canvas):
    return upload_tex2d_random(64)


@benchmark(20)
def upload_tex2d_random128(canvas):
    return upload_tex2d_random(128)


@benchmark(20)
def upload_tex2d_random256(canvas):
    return upload_tex2d_random(256)


@benchmark(20)
def upload_tex2d_random512(canvas):
    return upload_tex2d_random(512)


@benchmark(20)
def upload_tex2d_random1024(canvas):
    return upload_tex2d_random(1024)


@benchmark(20)
def upload_tex2d_random2048(canvas):
    return upload_tex2d_random(2048)


@benchmark(20)
def upload_tex2d_100_textures(canvas):
    # This emulates uploading a bunch of small textures.
    # The purpose is to measure chunking overhead.
    n = N2 // 10

    data1 = np.zeros((n, n, 4), np.uint8)

    textures = [gfx.Texture(data1, dim=2) for i in range(100)]

    for tex in textures:
        ensure_wgpu_object(tex)
        update_resource(tex)

    yield

    while True:
        for tex in textures:
            # tex.update_full()  # bypass chunking code
            tex.update_range((0, 0, 0), (n, n, 1))  # force going into chunk code
            update_resource(tex)
        yield


@benchmark(20)
def divider2(canvas):
    yield
    while True:
        yield


## 3D

SHAPE3 = 500, 500, 500


@benchmark(20)
def upload_tex3d_full_naive(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)
    data2 = np.ones(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:] = data2
        tex.update_range((0, 0, 0), SHAPE3)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_full_optimized(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)
    data2 = np.zeros(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data2)
            tex.update_full()
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), SHAPE3)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_full_noncont(canvas):

    data1 = np.zeros((SHAPE3[0] * 2, SHAPE3[1] * 2, SHAPE3[2] * 2), np.uint8)[
        ::2, ::2, ::2
    ]
    data2 = np.ones((SHAPE3[0] * 2, SHAPE3[1] * 2, SHAPE3[2] * 2), np.uint8)[
        ::2, ::2, ::2
    ]

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data1)
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), SHAPE3)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_quarter_x(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[2] // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:, :, :n] = data1[:, :, :n]
        tex.update_range((0, 0, 0), (n, SHAPE3[1], SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_quarter_y(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[1] // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:, :n, :] = data1[:, :n, :]
        tex.update_range((0, 0, 0), (SHAPE3[2], n, SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_quarter_z(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[0] // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        # tex.data[:n, :, :] = data1[:n, :, :]
        tex.update_range((0, 0, 0), (SHAPE3[2], SHAPE3[1], n))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_eights_x(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[2] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[:, :, offset:offset+n] = data1[:, :, offset:offset+n]
            tex.update_range((offset, 0, 0), (n, SHAPE3[1], SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_eights_y(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[1] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[:, offset:offset+n, :] = data1[:, offset:offset+n, :]
            tex.update_range((0, offset, 0), (SHAPE3[2], n, SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_eights_z(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[0] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(2):
            offset = (2 * i) * n
            # tex.data[offset:offset+n, :, :] = data1[offset:offset+n, :, :]
            tex.update_range((0, 0, offset), (SHAPE3[2], SHAPE3[1], n))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_four_eights_x(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[2] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(4):
            offset = (2 * i) * n
            # tex.data[:, :, offset:offset+n] = data1[:, :, offset:offset+n]
            tex.update_range((offset, 0, 0), (n, SHAPE3[1], SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_four_eights_y(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[1] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(4):
            offset = (2 * i) * n
            # tex.data[:, offset:offset+n, :] = data1[:, offset:offset+n, :]
            tex.update_range((0, offset, 0), (SHAPE3[2], n, SHAPE3[0]))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_four_eights_z(canvas):

    data1 = np.zeros(SHAPE3, np.uint8)

    n = SHAPE3[0] // 8
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        for i in range(4):
            offset = (2 * i) * n
            # tex.data[offset:offset+n, :, :] = data1[offset:offset+n, :, :]
            tex.update_range((0, 0, offset), (SHAPE3[2], SHAPE3[1], n))

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_chunk_stripes_x(canvas):
    # Emulate the worst-case stripe scenario

    data1 = np.zeros(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    step = tex._chunk_size[0] * 2  # every other chunk

    yield

    while True:
        tex.update_indices(np.arange(0, SHAPE3[2], step), None, None)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_chunk_stripes_y(canvas):
    # Emulate the worst-case stripe scenario

    data1 = np.zeros(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    step = tex._chunk_size[1] * 2  # every other chunk

    yield

    while True:
        tex.update_indices(None, np.arange(0, SHAPE3[1], step), None)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_chunk_stripes_z(canvas):
    # Emulate the worst-case stripe scenario

    data1 = np.zeros(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    step = tex._chunk_size[2] * 2  # every other chunk

    yield

    while True:
        tex.update_indices(None, None, np.arange(0, SHAPE3[0], step))
        update_resource(tex)
        yield


def upload_tex3d_random(n_random):

    data1 = np.zeros(SHAPE3, np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        xx = np.random.randint(0, SHAPE3[2], n_random)
        yy = np.random.randint(0, SHAPE3[1], n_random)
        zz = np.random.randint(0, SHAPE3[0], n_random)
        # tex.data[zz, yy,xx] = 1
        tex.update_indices(xx, yy, zz)
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_random8(canvas):
    return upload_tex3d_random(8)


@benchmark(20)
def upload_tex3d_random16(canvas):
    return upload_tex3d_random(16)


@benchmark(20)
def upload_tex3d_random32(canvas):
    return upload_tex3d_random(32)


@benchmark(20)
def upload_tex3d_random64(canvas):
    return upload_tex3d_random(64)


@benchmark(20)
def upload_tex3d_random128(canvas):
    return upload_tex3d_random(128)


@benchmark(20)
def upload_tex3d_random256(canvas):
    return upload_tex3d_random(256)


@benchmark(20)
def upload_tex3d_random512(canvas):
    return upload_tex3d_random(512)


@benchmark(20)
def upload_tex3d_random1024(canvas):
    return upload_tex3d_random(1024)


@benchmark(20)
def upload_tex3d_random2048(canvas):
    return upload_tex3d_random(2048)


@benchmark(20)
def upload_tex3d_random4096(canvas):
    return upload_tex3d_random(4096)


if __name__ == "__main__":
    run_all(globals())

    # upload_tex2d_full_optimized(None)
    # upload_tex2d_quarter_x(None)
    # upload_tex2d_quarter_y(None)
    # upload_tex2d_four_eights_x(None)
    # upload_tex2d_four_eights_y(None)
    # upload_tex2d_chunk_stripes_x(None)
    # upload_tex2d_chunk_stripes_y(None)

    # upload_tex2d_random32(None)
    # upload_tex2d_random64(None)
    # upload_tex2d_random128(None)
    # upload_tex2d_random256(None)
    # upload_tex2d_random512(None)
    # upload_tex2d_random1024(None)
    # upload_tex2d_random1024(None)
    # upload_tex2d_random2048(None)
    #
    # print("---")
    #
    # upload_tex3d_full_optimized(None)
    #
    # upload_tex3d_quarter_x(None)
    # upload_tex3d_quarter_y(None)
    # upload_tex3d_quarter_z(None)
    #
    # upload_tex3d_four_eights_x(None)
    # upload_tex3d_four_eights_y(None)
    # upload_tex3d_four_eights_z(None)
    #
    # upload_tex3d_chunk_stripes_x(None)
    # upload_tex3d_chunk_stripes_y(None)
    # upload_tex3d_chunk_stripes_z(None)

    # upload_tex3d_random32(None)
    # upload_tex3d_random64(None)
    # upload_tex3d_random128(None)
    # upload_tex3d_random256(None)
    # upload_tex3d_random512(None)
    # upload_tex3d_random1024(None)
    # upload_tex3d_random2048(None)
    # upload_tex3d_random4096(None)

