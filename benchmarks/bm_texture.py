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
def upload_tex1d_half_x(canvas):
    # Emulate updating half of the texture data

    data1 = np.zeros((N1, 4), np.float32)
    data2 = np.ones((N1, 4), np.float32)

    n = N1 // 2

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:n] = data1[:n]
        tex.update_range((0, 0, 0), (n, 1, 1))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex1d_two_quarters_x(canvas):
    # Emulate updating two quarters of texture data

    data1 = np.zeros((N1, 4), np.float32)
    data2 = np.ones((N1, 4), np.float32)

    n = N1 // 4

    tex = gfx.Texture(data1, dim=1)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:n] = data1[:n]
        tex.update_range((0, 0, 0), (n, 1, 1))
        tex.data[3 * n :] = data1[3 * n :]
        tex.update_range((3 * n, 0, 0), (n, 1, 1))

        data1, data2 = data2, data1

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
def upload_tex2d_half_x(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.ones((N2, N2, 4), np.uint8)

    n = N2 // 2
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:, :n] = data1[:, :n]
        tex.update_range((0, 0, 0), (n, N2, 1))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_half_y(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.ones((N2, N2, 4), np.uint8)

    n = N2 // 2
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:n, :] = data1[:n, :]
        tex.update_range((0, 0, 0), (N2, n, 1))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_two_quarters_x(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.ones((N2, N2, 4), np.uint8)

    n = N2 // 4
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:, :n] = data1[:, :n]
        tex.update_range((0, 0, 0), (n, N2, 1))
        tex.data[:, 3 * n :] = data1[:, 3 * n :]
        tex.update_range((3 * n, 0, 0), (n, N2, 1))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex2d_two_quarters_y(canvas):

    data1 = np.zeros((N2, N2, 4), np.uint8)
    data2 = np.ones((N2, N2, 4), np.uint8)

    n = N2 // 4
    tex = gfx.Texture(data1, dim=2)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:n, :] = data1[:n, :]
        tex.update_range((0, 0, 0), (N2, n, 1))
        tex.data[3 * n :, :] = data1[3 * n :, :]
        tex.update_range((0, 3 * n, 0), (N2, n, 1))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def divider2(canvas):
    yield
    while True:
        yield


## 3D

N3 = 500


@benchmark(20)
def upload_tex3d_full_naive(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:] = data2
        tex.update_range((0, 0, 0), (N3, N3, N3))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_full_optimized(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.zeros((N3, N3, N3), np.uint8)

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
            tex.update_range((0, 0, 0), (N3, N3, N3))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_full_noncont(canvas):

    data1 = np.zeros((N3 * 2, N3 * 2, N3 * 2), np.uint8)[::2, ::2,::2]
    data2 = np.ones((N3 * 2, N3 * 2, N3*2), np.uint8)[::2, ::2,::2]

    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        if hasattr(tex, "set_data"):
            tex.set_data(data1)
        else:
            tex.data[:] = data2
            tex.update_range((0, 0, 0), (N3, N3, N3))
        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_half_x(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 2
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:, :, :n] = data1[:, :, :n]
        tex.update_range((0, 0, 0), (n, N3, N3))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_half_y(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 2
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:, :n, :] = data1[:, :n, :]
        tex.update_range((0, 0, 0), (N3, n, N3))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_half_z(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 2
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:

        tex.data[:n, :, :] = data1[:n, :, :]
        tex.update_range((0, 0, 0), (N3, N3, n))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_quarters_x(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:, :, :n] = data1[:, :, :n]
        tex.update_range((0, 0, 0), (n, N3, N3))
        tex.data[:, :, 3 * n :] = data1[:, :, 3 * n :]
        tex.update_range((3 * n, 0, 0), (n, N3, N3))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_quarters_y(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:, :n, :] = data1[:, :n, :]
        tex.update_range((0, 0, 0), (N3, n, N3))
        tex.data[:, 3 * n :, :] = data1[:, 3 * n :, :]
        tex.update_range((0, 3 * n, 0), (N3, n, N3))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


@benchmark(20)
def upload_tex3d_two_quarters_z(canvas):

    data1 = np.zeros((N3, N3, N3), np.uint8)
    data2 = np.ones((N3, N3, N3), np.uint8)

    n = N3 // 4
    tex = gfx.Texture(data1, dim=3)
    ensure_wgpu_object(tex)
    update_resource(tex)

    yield

    while True:
        tex.data[:n, :, :] = data1[:n, :, :]
        tex.update_range((0, 0, 0), (N3, N3, n))
        tex.data[3 * n :, :, :] = data1[3 * n :, :, :]
        tex.update_range((0, 0, 3 * n), (N3, N3, n))

        data1, data2 = data2, data1

        update_resource(tex)
        yield


if __name__ == "__main__":
    run_all(globals())
