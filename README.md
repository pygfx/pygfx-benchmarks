# pygfx-benchmarks

## Introducion

Benchmarks for wgpu and pygfx

This repository contains a collection of scripts that perform benchmarks on wgpu and pygfx.
Their purpose include:

* To understand best practices for using wgpu.
* To make informed decisions in pygfx and other libraries.
* To track performance of pygfx logic, so that the effect of changes on performance can be measured.

Scripts go into the [benchmarks](benchmarks/) folder. Matching results go into the [results](results/) folder.


## Writing a benchmark

Benchmarks are generator functions (functions that use `yield`). The
function should accept a canvas object, but does not have to use it.
This is so that visual results can be shown to see that the benchmark
actually does what it is meant to do.

The code leading up to the first `yield` is for setting things up. After
that, it should enter an infinite loop to do repeated measurements.
The number of measurements can be set in the `@benchmark`  decorator.

Each yield may contain a dict with additional (time) measurements (e.g. GPU times).


```py
@benchmark(20)
def my_benchmark(canvas):

    foo = "set things up"
    yield  # done setting things up

    while True:
        time.sleep(0.01)  # do something that takes time
        yield  # measurement point

```

See [bm_example.py](benchmarks/bm_example.py) for a functioning example.


## Observations

* [bm_points](results/bm_points.md)