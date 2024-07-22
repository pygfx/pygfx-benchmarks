# pygfx buffer

[bm_buffer.py](../benchmarks/bm_buffer.py)


## Introduction

This series of benchmarks is to test the performance of the pygfx buffer for chunking.
It builds on top of the [bm_wgpu_buffer.md](bm_wgpu_buffer.md) benchmarks, to see
how these results end up in practice in pygfx, and to tweak chunking parameters.


## Full upload

```
Apple M1 Pro (IntegratedGPU) via Metal
      upload_buffer_full_naive (20x) - cpu: 23.14 ms
  upload_buffer_full_optimized (20x) - cpu: 20.11 ms
    upload_buffer_full_noncont (20x) - cpu: 60.22 ms
```

In these benchmarks we see that the optimized (new) version
that avoids data-copies is indeed faster than the previous naive implementation.
It also shows that when the data is not contiguous, the upload is much slower.


## Partial uploads

```
            upload_buffer_half (20x) - cpu: 10.93 ms
    upload_buffer_two_quarters (20x) - cpu: 11.33 ms
   upload_buffer_chunk_stripes (20x) - cpu: 10.78 ms
```

Here, we upload half of the buffer, in a few different ways.
The results are as one might expect. The "chunk_stripes" test shows that
there is no reason for merging chunks over gaps. At least not with 32 chunks.


## Random uploads

```
         upload_buffer_random8 (20x) - cpu:  1.59 ms
        upload_buffer_random16 (20x) - cpu:  3.01 ms
        upload_buffer_random32 (20x) - cpu:  5.59 ms
        upload_buffer_random64 (20x) - cpu:  9.70 ms
       upload_buffer_random128 (20x) - cpu: 15.21 ms
       upload_buffer_random256 (20x) - cpu: 17.93 ms
       upload_buffer_random512 (20x) - cpu: 18.91 ms
           upload_v_random1024 (20x) - cpu: 20.17 ms
      upload_buffer_random2048 (20x) - cpu: 20.05 ms
      upload_buffer_random4096 (20x) - cpu: 22.23 ms
```

These tests may represent the most realistic use-case. We don't want any of
these cases to take longer than simply uploading the whole buffer.
The chunking/merging algorithm should be such that this does not happen.

The results show that the performance naturally climbs to that of a full chunk
upload.


## Uploading many buffers
```
            upload_100_buffers (20x) - cpu: 23.09 ms
```

Uploading 100 buffers that are 1/100 the size shows a more or less
expected time. This illustrates that the overhead for applying chunking is
probably reasonable.