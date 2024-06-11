import time

from _benchmark import benchmark, run_all


@benchmark(20)
def my_benchmark(canvas):

    foo = "set things up"

    yield  # done setting things up


    while True:

        # Do something that takes time
        time.sleep(0.01)

        yield  # measurement point



if __name__ == "__main__":
    from wgpu.gui.auto import WgpuCanvas

    run_all(globals())
