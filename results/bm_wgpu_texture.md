# wgpu texture

[bm_wgpu_texture.py](../benchmarks/bm_wgpu_texture.py)

## Introduction

Textures are a bit different from buffers, since they're multidimensional.
In this benchmark we investigate uploading data to textures specifically.


## Upload method

I compared the `queue.write_texture()` and `buffer.write_mapped()` methods.
Just a small test to check whether queue_write is the faster method, like it was
for buffer uploads.
```
Apple M1 Pro (IntegratedGPU) via Metal

  up_wtex_queue_write_(256, 256, 1) (20x) - cpu:  1.40
  up_wtex_queue_write_(512, 512, 1) (20x) - cpu:  1.34
up_wtex_queue_write_(1024, 1024, 1) (20x) - cpu:  1.57
up_wtex_queue_write_(2048, 2048, 1) (20x) - cpu:  2.07

  up_wtex_write_mapped_(256, 256, 1) (20x) - cpu:  1.40
  up_wtex_write_mapped_(512, 512, 1) (20x) - cpu:  1.40
up_wtex_write_mapped_(1024, 1024, 1) (20x) - cpu:  1.63
up_wtex_write_mapped_(2048, 2048, 1) (20x) - cpu:  2.14
```

It looks like, similar to buffer uploads, the queue_write method has a small
performance advantage.


## Chunking with r8unorm

To investigate chunking, a test was made for each dimension. Firtst the chunksize
is equal for each dimension in the texture. Then the performance was measured
when the chunking happened in only one dimension.


```
Apple M1 Pro (IntegratedGPU) via Metal
-- 1D
up_wtex_queue_write_(2048, 1, 1)_(64, 1, 1) (20x) - cpu:  2.03
up_wtex_queue_write_(2048, 1, 1)_(128, 1, 1) (20x) - cpu:  1.64
up_wtex_queue_write_(2048, 1, 1)_(256, 1, 1) (20x) - cpu:  1.46
up_wtex_queue_write_(2048, 1, 1)_(512, 1, 1) (20x) - cpu:  1.49
up_wtex_queue_write_(2048, 1, 1)_(1024, 1, 1) (20x) - cpu:  1.42
up_wtex_queue_write_(2048, 1, 1)_(2048, 1, 1) (20x) - cpu:  1.35
-- 2D
up_wtex_queue_write_(2048, 2048, 1)_(64, 64, 1) (20x) - cpu: 26.07
up_wtex_queue_write_(2048, 2048, 1)_(128, 128, 1) (20x) - cpu: 11.50
up_wtex_queue_write_(2048, 2048, 1)_(256, 256, 1) (20x) - cpu:  4.68
up_wtex_queue_write_(2048, 2048, 1)_(512, 512, 1) (20x) - cpu:  2.98
up_wtex_queue_write_(2048, 2048, 1)_(1024, 1024, 1) (20x) - cpu:  2.35
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu:  1.99
--
up_wtex_queue_write_(2048, 2048, 1)_(64, 2048, 1) (20x) - cpu:  3.99
up_wtex_queue_write_(2048, 2048, 1)_(128, 2048, 1) (20x) - cpu:  3.13
up_wtex_queue_write_(2048, 2048, 1)_(256, 2048, 1) (20x) - cpu:  2.90
up_wtex_queue_write_(2048, 2048, 1)_(512, 2048, 1) (20x) - cpu:  2.59
up_wtex_queue_write_(2048, 2048, 1)_(1024, 2048, 1) (20x) - cpu:  2.93
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu:  2.04
--
up_wtex_queue_write_(2048, 2048, 1)_(2048, 64, 1) (20x) - cpu:  2.91
up_wtex_queue_write_(2048, 2048, 1)_(2048, 128, 1) (20x) - cpu:  2.68
up_wtex_queue_write_(2048, 2048, 1)_(2048, 256, 1) (20x) - cpu:  2.35
up_wtex_queue_write_(2048, 2048, 1)_(2048, 512, 1) (20x) - cpu:  2.18
up_wtex_queue_write_(2048, 2048, 1)_(2048, 1024, 1) (20x) - cpu:  2.12
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu:  2.07
-- 3D
up_wtex_queue_write_(512, 512, 512)_(64, 64, 64) (20x) - cpu:104.15
up_wtex_queue_write_(512, 512, 512)_(128, 128, 128) (20x) - cpu: 66.37
up_wtex_queue_write_(512, 512, 512)_(256, 256, 256) (20x) - cpu: 43.59
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu: 32.57
--
up_wtex_queue_write_(512, 512, 512)_(32, 512, 512) (20x) - cpu:129.55
up_wtex_queue_write_(512, 512, 512)_(64, 512, 512) (20x) - cpu: 77.98
up_wtex_queue_write_(512, 512, 512)_(128, 512, 512) (20x) - cpu: 61.61
up_wtex_queue_write_(512, 512, 512)_(256, 512, 512) (20x) - cpu: 51.05
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu: 33.29
--
up_wtex_queue_write_(512, 512, 512)_(512, 32, 512) (20x) - cpu: 52.65
up_wtex_queue_write_(512, 512, 512)_(512, 64, 512) (20x) - cpu: 42.16
up_wtex_queue_write_(512, 512, 512)_(512, 128, 512) (20x) - cpu: 47.80
up_wtex_queue_write_(512, 512, 512)_(512, 256, 512) (20x) - cpu: 48.27
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu: 31.75
--
up_wtex_queue_write_(512, 512, 512)_(512, 512, 32) (20x) - cpu: 34.85
up_wtex_queue_write_(512, 512, 512)_(512, 512, 64) (20x) - cpu: 35.39
up_wtex_queue_write_(512, 512, 512)_(512, 512, 128) (20x) - cpu: 33.36
up_wtex_queue_write_(512, 512, 512)_(512, 512, 256) (20x) - cpu: 33.50
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu: 32.96
```


The first observation is that the performance seems to be affected
even for relatively large chunk sizes. E.g. dividing a 2D texture in
16 pieces (4x4 chunks) causes a 50% performance penalty.

For 2D textures, chunking the rows is much more efficient than chunking the
columns. This is somewhat expected due to data layout (C-contiguous arrays).

For 3D textures, chunking in the 3'd dimension seems almost free, and chunking
over the rows is again much cheaper then chunking over the columns.



## Chunking with rgba32float

Repeating the previous benchmarks, but now with a textue format that occupies
16 bytes per pixel.

A 1D texture of 2048 elements is `2**15` bytes. A 2D texture of 2048x2048 elements
is `2**26` bytes. A 3D texture of 512x512x256 elements is `2**30` elements.


```
Apple M1 Pro (IntegratedGPU) via Metal
-- 1D
up_wtex_queue_write_(2048, 1, 1)_(64, 1, 1) (20x) - cpu:  2.05
up_wtex_queue_write_(2048, 1, 1)_(128, 1, 1) (20x) - cpu:  1.62
up_wtex_queue_write_(2048, 1, 1)_(256, 1, 1) (20x) - cpu:  1.50
up_wtex_queue_write_(2048, 1, 1)_(512, 1, 1) (20x) - cpu:  1.46
up_wtex_queue_write_(2048, 1, 1)_(1024, 1, 1) (20x) - cpu:  1.34
up_wtex_queue_write_(2048, 1, 1)_(2048, 1, 1) (20x) - cpu:  1.33
-- 2D
up_wtex_queue_write_(2048, 2048, 1)_(64, 64, 1) (20x) - cpu: 66.50
up_wtex_queue_write_(2048, 2048, 1)_(128, 128, 1) (20x) - cpu: 34.25
up_wtex_queue_write_(2048, 2048, 1)_(256, 256, 1) (20x) - cpu: 23.69
up_wtex_queue_write_(2048, 2048, 1)_(512, 512, 1) (20x) - cpu: 24.06
up_wtex_queue_write_(2048, 2048, 1)_(1024, 1024, 1) (20x) - cpu: 17.79
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu: 13.26
--
up_wtex_queue_write_(2048, 2048, 1)_(64, 2048, 1) (20x) - cpu: 33.66
up_wtex_queue_write_(2048, 2048, 1)_(128, 2048, 1) (20x) - cpu: 28.69
up_wtex_queue_write_(2048, 2048, 1)_(256, 2048, 1) (20x) - cpu: 26.95
up_wtex_queue_write_(2048, 2048, 1)_(512, 2048, 1) (20x) - cpu: 19.64
up_wtex_queue_write_(2048, 2048, 1)_(1024, 2048, 1) (20x) - cpu: 22.79
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu: 12.66
--
up_wtex_queue_write_(2048, 2048, 1)_(2048, 64, 1) (20x) - cpu: 15.02
up_wtex_queue_write_(2048, 2048, 1)_(2048, 128, 1) (20x) - cpu: 14.32
up_wtex_queue_write_(2048, 2048, 1)_(2048, 256, 1) (20x) - cpu: 14.33
up_wtex_queue_write_(2048, 2048, 1)_(2048, 512, 1) (20x) - cpu: 14.04
up_wtex_queue_write_(2048, 2048, 1)_(2048, 1024, 1) (20x) - cpu: 14.02
up_wtex_queue_write_(2048, 2048, 1)_(2048, 2048, 1) (20x) - cpu: 14.35
-- 3D
up_wtex_queue_write_(512, 512, 256)_(64, 64, 64) (20x) - cpu:503.93
up_wtex_queue_write_(512, 512, 256)_(128, 128, 128) (20x) - cpu:445.09
up_wtex_queue_write_(512, 512, 256)_(256, 256, 256) (20x) - cpu:423.14
up_wtex_queue_write_(512, 512, 256)_(512, 512, 256) (20x) - cpu:201.48
--
up_wtex_queue_write_(512, 512, 256)_(32, 512, 256) (20x) - cpu:376.23
up_wtex_queue_write_(512, 512, 256)_(64, 512, 256) (20x) - cpu:442.04
up_wtex_queue_write_(512, 512, 256)_(128, 512, 256) (20x) - cpu:442.52
up_wtex_queue_write_(512, 512, 256)_(256, 512, 256) (20x) - cpu:397.46
up_wtex_queue_write_(512, 512, 256)_(512, 512, 256) (20x) - cpu:188.59
--
up_wtex_queue_write_(512, 512, 256)_(512, 32, 256) (20x) - cpu:293.63
up_wtex_queue_write_(512, 512, 256)_(512, 64, 256) (20x) - cpu:295.94
up_wtex_queue_write_(512, 512, 256)_(512, 128, 256) (20x) - cpu:333.57
up_wtex_queue_write_(512, 512, 256)_(512, 256, 256) (20x) - cpu:393.57
up_wtex_queue_write_(512, 512, 256)_(512, 512, 256) (20x) - cpu:281.93
--
up_wtex_queue_write_(512, 512, 256)_(512, 512, 32) (20x) - cpu:211.56
up_wtex_queue_write_(512, 512, 256)_(512, 512, 64) (20x) - cpu:209.42
up_wtex_queue_write_(512, 512, 256)_(512, 512, 128) (20x) - cpu:205.78
up_wtex_queue_write_(512, 512, 256)_(512, 512, 256) (20x) - cpu:223.85
```


For 2D textures the main difference is that chunking over the columns is
now nearly free. This can be attributed to the overhead that we observed
in the previous benchmark is now very small compared to the total upload time
because the chunks are 16 times larger.

The measurements for 3D become a bit more variable, probably of what we discuss next ...


## Chunking with textures larger than 1GB

We already saw that buffers of about 1GB and larger start to show
unexpected performance characteristics.

With a 2GB texture:

```
Apple M1 Pro (IntegratedGPU) via Metal
-- 3D
up_wtex_queue_write_(512, 512, 512)_(64, 64, 64) (20x) - cpu:1657.80
up_wtex_queue_write_(512, 512, 512)_(128, 128, 128) (20x) - cpu:1455.47
up_wtex_queue_write_(512, 512, 512)_(256, 256, 256) (20x) - cpu:1595.53
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu:1402.06
--
up_wtex_queue_write_(512, 512, 512)_(32, 512, 512) (20x) - cpu:784.08
up_wtex_queue_write_(512, 512, 512)_(64, 512, 512) (20x) - cpu:1138.96
up_wtex_queue_write_(512, 512, 512)_(128, 512, 512) (20x) - cpu:1207.53
up_wtex_queue_write_(512, 512, 512)_(256, 512, 512) (20x) - cpu:1673.58
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu:1318.35
--
up_wtex_queue_write_(512, 512, 512)_(512, 32, 512) (20x) - cpu:621.49
up_wtex_queue_write_(512, 512, 512)_(512, 64, 512) (20x) - cpu:1103.29
up_wtex_queue_write_(512, 512, 512)_(512, 128, 512) (20x) - cpu:1181.93
up_wtex_queue_write_(512, 512, 512)_(512, 256, 512) (20x) - cpu:1555.42
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu:1786.20
--
up_wtex_queue_write_(512, 512, 512)_(512, 512, 32) (20x) - cpu:592.84
up_wtex_queue_write_(512, 512, 512)_(512, 512, 64) (20x) - cpu:464.33
up_wtex_queue_write_(512, 512, 512)_(512, 512, 128) (20x) - cpu:570.66
up_wtex_queue_write_(512, 512, 512)_(512, 512, 256) (20x) - cpu:803.88
up_wtex_queue_write_(512, 512, 512)_(512, 512, 512) (20x) - cpu:1456.46
```

With a 4GB texture:
```
Apple M1 Pro (IntegratedGPU) via Metal
-- 3D
up_wtex_queue_write_(512, 512, 1024)_(64, 64, 64) (20x) - cpu:4143.93
up_wtex_queue_write_(512, 512, 1024)_(128, 128, 128) (20x) - cpu:3722.47
up_wtex_queue_write_(512, 512, 1024)_(256, 256, 256) (20x) - cpu:3915.88
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 512) (20x) - cpu:3039.16
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 1024) (20x) - cpu:3324.94
--
up_wtex_queue_write_(512, 512, 1024)_(32, 512, 1024) (20x) - cpu:4869.50
up_wtex_queue_write_(512, 512, 1024)_(64, 512, 1024) (20x) - cpu:5254.12
up_wtex_queue_write_(512, 512, 1024)_(128, 512, 1024) (20x) - cpu:5024.50
up_wtex_queue_write_(512, 512, 1024)_(256, 512, 1024) (20x) - cpu:5039.43
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 1024) (20x) - cpu:3576.97
--
up_wtex_queue_write_(512, 512, 1024)_(512, 32, 1024) (20x) - cpu:4129.76
up_wtex_queue_write_(512, 512, 1024)_(512, 64, 1024) (20x) - cpu:3792.90
up_wtex_queue_write_(512, 512, 1024)_(512, 128, 1024) (20x) - cpu:3888.27
up_wtex_queue_write_(512, 512, 1024)_(512, 256, 1024) (20x) - cpu:4265.52
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 1024) (20x) - cpu:3085.75
--
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 32) (20x) - cpu:3072.60
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 64) (20x) - cpu:3253.69
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 128) (20x) - cpu:3210.30
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 256) (20x) - cpu:4878.53
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 512) (20x) - cpu:3619.01
up_wtex_queue_write_(512, 512, 1024)_(512, 512, 1024) (20x) - cpu:3923.30
```

This shows that you want to do chunking for large textures, i.e. use a certain maximum chunk size,
though it must be such that the chunks are contiguous, thus applies only in the
last dimension of the texture.


## Overhead for non-contiguous chunks


When a chunk is contiguous, reducing its size, can, for a texture, result in it
not being contiguous anymore, if the reduction is in the x-dim (or y-dim for 3D textures).
This benchmark is to get insight what the costs are, and how much less data
must be synced before it's worth just sending the full size (in that dimension).

```
Apple M1 Pro (IntegratedGPU) via Metal
-- 2D one chunk
up_wtex_one_chunk_(8000, 8000, 1)_(8000, 8000, 1) (20x) - cpu: 14.92 ms
up_wtex_one_chunk_(8000, 8000, 1)_(7000, 8000, 1) (20x) - cpu: 19.51 ms
up_wtex_one_chunk_(8000, 8000, 1)_(4000, 8000, 1) (20x) - cpu: 12.04 ms
up_wtex_one_chunk_(8000, 8000, 1)_(2000, 8000, 1) (20x) - cpu:  6.89 ms
up_wtex_one_chunk_(8000, 8000, 1)_(1000, 8000, 1) (20x) - cpu:  4.13 ms
up_wtex_one_chunk_(8000, 8000, 1)_(8000, 7000, 1) (20x) - cpu: 14.62 ms
up_wtex_one_chunk_(8000, 8000, 1)_(8000, 4000, 1) (20x) - cpu:  7.60 ms
up_wtex_one_chunk_(8000, 8000, 1)_(8000, 2000, 1) (20x) - cpu:  4.70 ms
up_wtex_one_chunk_(8000, 8000, 1)_(8000, 1000, 1) (20x) - cpu:  2.61 ms
-- 3D one chunk
up_wtex_one_chunk_(400, 400, 400)_(400, 400, 400) (20x) - cpu: 15.21 ms
--
up_wtex_one_chunk_(400, 400, 400)_(350, 400, 400) (20x) - cpu: 22.35 ms
up_wtex_one_chunk_(400, 400, 400)_(200, 400, 400) (20x) - cpu: 14.87 ms
up_wtex_one_chunk_(400, 400, 400)_(100, 400, 400) (20x) - cpu: 10.40 ms
up_wtex_one_chunk_(400, 400, 400)_(50, 400, 400) (20x) - cpu:  9.24 ms
up_wtex_one_chunk_(400, 400, 400)_(25, 400, 400) (20x) - cpu:  6.54 ms
--
up_wtex_one_chunk_(400, 400, 400)_(350, 200, 400) (20x) - cpu: 12.24 ms
up_wtex_one_chunk_(400, 400, 400)_(200, 200, 400) (20x) - cpu:  8.44 ms
up_wtex_one_chunk_(400, 400, 400)_(100, 200, 400) (20x) - cpu:  5.44 ms
up_wtex_one_chunk_(400, 400, 400)_(50, 200, 400) (20x) - cpu:  4.55 ms
up_wtex_one_chunk_(400, 400, 400)_(25, 200, 400) (20x) - cpu:  3.37 ms
--
up_wtex_one_chunk_(400, 400, 400)_(400, 350, 400) (20x) - cpu: 19.56 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 200, 400) (20x) - cpu: 12.11 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 100, 400) (20x) - cpu:  6.35 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 50, 400) (20x) - cpu:  3.33 ms
--
up_wtex_one_chunk_(400, 400, 400)_(400, 400, 350) (20x) - cpu: 13.30 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 400, 200) (20x) - cpu:  8.39 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 400, 100) (20x) - cpu:  4.83 ms
up_wtex_one_chunk_(400, 400, 400)_(400, 400, 50) (20x) - cpu:  2.44 ms
```

The results show that the amount of data must be 1/4th or less, compared to a contigous chunk.
For 3D texturses, it's even 1/8th for the x dimension. Though if its already
non-contiguous in y, the extra non-contiguouty for x also follows the 1/4th factor.


## Conclusions

For textures it looks like the `queue.write_texture()` method is the way to go.
Another advantage of this method is that it does not require `bytes_per_row` to
be a multiple of 256.

Using chunks seems to incur an overhead sooner than it does with buffers,
so keeping the uploaded chunks large, e.g. by merging chunks, is important.
In here, it's easily worth to span gaps of 3 chunks, if that makes the chunk contiguous.

Chunking in any but the last dimension causes an extra cost, due to the data
becoming non-contiguous. The non-contiguity at the GPU side is handled much better than what we observed
with buffers (because writing the non-contiguous data to the GPU texture) is optimized)
but it's still slower when any but the slowest changing dimension is chunked.

Beyond a texture size of 1GB, uploading the buffer as a whole becomes slower, and
using chunks actually adds benefit.
