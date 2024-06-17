# wgpu buffer chunksize

[bm_wgpu_buffer_chunksize.py](../benchmarks/bm_wgpu_buffer_chunksize.py)

## Introduction

In the buffer-upload benchmarks we saw that uploads should be done in
contiguous parts, i.e. chunks. The smaller the chunks, the more
"precise" the dirty elements can be uploaded. But smaller chunks also
add more overhead.

The purpose of this benchmark is to gain insight into how the chunksize affects
buffer upload performance.

There are two types of overhead that increase as the chunksize is reduced:

* The Python logic to do per-chunk calculations.
* The wgpu overhead for processing each chunk.

We focus on the latter in this benchmark.


## The problem

The purpose of using chunks, is that time is saved, by only uploading
the chunks that (contain elements that) need to be uploaded. If there
are 10 chunks, and only two need to be uploaded, the upload is (in
theory) 5x faster than doing a full upload. The smaller the chunks, the
more likely it is that there are chunks that don't need an update.

However, the overhead of each upload operation negatively affects
performance. The smaller the chunks, the slower it gets. We need to
find the sweet spot.

Consider the adversarial use-case where there is one element in each
chunk that needs to be uploaded. So effectively the whole buffer is
uploaded, but in chunks. This sounds like the worst case scenario.
However, an easy trick we can do is to combine adjacent trunks, which
would turn this use-case into just uploading the full buffer in one go.

So what would be the worst case scenario then? The scenario where we
cannot use chunk-merging, but still upload a lot of chunks. This means
uploading every other chunk.

We could define the optimal chunk size as the chunk size for which the
every-other-chunk-upload is just a bit faster than the full upload.
Going bigger would reduce the performance in more favourable cases.
Going smaller would improve the performance in more favourable cases, but
can hurt performance in specific other situations.


## Approach

We measure the time it takes to upload a full buffer in chunks.
For smaller chunks sizes, the performance will improve as the chunk size increases.
But at some point it will stabalize, and be as fast as just uploading the buffer.
I.e. the overhead becomes negligable.

We try to find that tipping point. And do so for different buffer sizes.

This is basically finding the optimal chunk-size for the case where
chunk-merging is not allowed. So the optimal chunk size is a bit smaller.
Actually, the optimal chunk size is about half of it, because then you're at the
worst-case scenario where every other chunk is uploaded.

## Measurements


### With a 32 KiB (2**15) byte buffer
```
Apple M1 Pro (IntegratedGPU) via Metal
      up_wbuf_queue_write_15_6 (20x) - cpu:  4.91
      up_wbuf_queue_write_15_7 (20x) - cpu:  2.99
      up_wbuf_queue_write_15_8 (20x) - cpu:  2.06
      up_wbuf_queue_write_15_9 (20x) - cpu:  1.75
     up_wbuf_queue_write_15_10 (20x) - cpu:  1.52
     up_wbuf_queue_write_15_11 (20x) - cpu:  1.42
     up_wbuf_queue_write_15_12 (20x) - cpu:  1.38
     up_wbuf_queue_write_15_13 (20x) - cpu:  1.34
     up_wbuf_queue_write_15_14 (20x) - cpu:  1.39
     up_wbuf_queue_write_15_15 (20x) - cpu:  1.34

     up_wbuf_write_mapped_15_6 (20x) - cpu:  2.28
     up_wbuf_write_mapped_15_7 (20x) - cpu:  1.81
     up_wbuf_write_mapped_15_8 (20x) - cpu:  1.57
     up_wbuf_write_mapped_15_9 (20x) - cpu:  1.53
    up_wbuf_write_mapped_15_10 (20x) - cpu:  1.45
    up_wbuf_write_mapped_15_11 (20x) - cpu:  1.36
    up_wbuf_write_mapped_15_12 (20x) - cpu:  1.36
    up_wbuf_write_mapped_15_13 (20x) - cpu:  1.44
    up_wbuf_write_mapped_15_14 (20x) - cpu:  1.69
    up_wbuf_write_mapped_15_15 (20x) - cpu:  1.36
```

On a Mac, the tipping point is at about 2**12 for queue_write,
and at 2**8 for write_mapped.

### With a 1 MiB (2**20) buffer
```
Apple M1 Pro (IntegratedGPU) via Metal
     up_wbuf_queue_write_20_10 (20x) - cpu:  7.14
     up_wbuf_queue_write_20_11 (20x) - cpu:  4.62
     up_wbuf_queue_write_20_12 (20x) - cpu:  3.27
     up_wbuf_queue_write_20_13 (20x) - cpu:  2.45
     up_wbuf_queue_write_20_14 (20x) - cpu:  2.67
     up_wbuf_queue_write_20_15 (20x) - cpu:  2.11
     up_wbuf_queue_write_20_16 (20x) - cpu:  1.93
     up_wbuf_queue_write_20_17 (20x) - cpu:  1.69
     up_wbuf_queue_write_20_18 (20x) - cpu:  1.58

    up_wbuf_write_mapped_20_10 (20x) - cpu:  3.19
    up_wbuf_write_mapped_20_11 (20x) - cpu:  2.43
    up_wbuf_write_mapped_20_12 (20x) - cpu:  2.04
    up_wbuf_write_mapped_20_13 (20x) - cpu:  1.77
    up_wbuf_write_mapped_20_14 (20x) - cpu:  1.69
    up_wbuf_write_mapped_20_15 (20x) - cpu:  1.60
    up_wbuf_write_mapped_20_16 (20x) - cpu:  1.57
    up_wbuf_write_mapped_20_17 (20x) - cpu:  1.52
    up_wbuf_write_mapped_20_18 (20x) - cpu:  1.59
```

On a Mac, the tipping point is at about 2**18 for queue_write,
and at 2**14 for write_mapped.



### With a 32 MiB (2**25) byte buffer
```
Apple M1 Pro (IntegratedGPU) via Metal
     up_wbuf_queue_write_25_12 (20x) - cpu: 66.52
     up_wbuf_queue_write_25_13 (20x) - cpu: 41.25
     up_wbuf_queue_write_25_14 (20x) - cpu: 55.54
     up_wbuf_queue_write_25_15 (20x) - cpu: 30.84
     up_wbuf_queue_write_25_16 (20x) - cpu: 17.81
     up_wbuf_queue_write_25_17 (20x) - cpu: 13.14
     up_wbuf_queue_write_25_18 (20x) - cpu: 10.87
     up_wbuf_queue_write_25_19 (20x) - cpu: 10.43
     up_wbuf_queue_write_25_20 (20x) - cpu:  9.91
     up_wbuf_queue_write_25_21 (20x) - cpu:  9.00

    up_wbuf_write_mapped_25_12 (20x) - cpu: 22.84
    up_wbuf_write_mapped_25_13 (20x) - cpu: 15.75
    up_wbuf_write_mapped_25_14 (20x) - cpu: 11.71
    up_wbuf_write_mapped_25_15 (20x) - cpu:  9.97
    up_wbuf_write_mapped_25_16 (20x) - cpu:  9.25
    up_wbuf_write_mapped_25_17 (20x) - cpu:  8.75
    up_wbuf_write_mapped_25_18 (20x) - cpu:  8.59
    up_wbuf_write_mapped_25_19 (20x) - cpu:  8.30
    up_wbuf_write_mapped_25_20 (20x) - cpu:  8.40
    up_wbuf_write_mapped_25_21 (20x) - cpu:  8.33
```


On a Mac, the tipping point is at about 2**20 for queue_write,
and at 2**16 for write_mapped.



### With a 256 MiB (2**28) byte buffer

```
Apple M1 Pro (IntegratedGPU) via Metal
     up_wbuf_queue_write_28_14 (20x) - cpu:389.03
     up_wbuf_queue_write_28_15 (20x) - cpu:224.61
     up_wbuf_queue_write_28_16 (20x) - cpu:139.97
     up_wbuf_queue_write_28_17 (20x) - cpu: 96.65
     up_wbuf_queue_write_28_18 (20x) - cpu: 74.94
     up_wbuf_queue_write_28_19 (20x) - cpu: 64.49
     up_wbuf_queue_write_28_20 (20x) - cpu: 56.75
     up_wbuf_queue_write_28_21 (20x) - cpu: 54.35
     up_wbuf_queue_write_28_22 (20x) - cpu: 49.76
     up_wbuf_queue_write_28_23 (20x) - cpu: 50.31

    up_wbuf_write_mapped_28_14 (20x) - cpu: 90.82
    up_wbuf_write_mapped_28_15 (20x) - cpu: 74.95
    up_wbuf_write_mapped_28_16 (20x) - cpu: 63.75
    up_wbuf_write_mapped_28_17 (20x) - cpu: 61.57
    up_wbuf_write_mapped_28_18 (20x) - cpu: 59.40
    up_wbuf_write_mapped_28_19 (20x) - cpu: 58.21
    up_wbuf_write_mapped_28_20 (20x) - cpu: 54.45
    up_wbuf_write_mapped_28_21 (20x) - cpu: 59.63
    up_wbuf_write_mapped_28_22 (20x) - cpu: 58.18
    up_wbuf_write_mapped_28_23 (20x) - cpu: 56.93
```

Similar results.


### With a 1GiB (2**30) byte buffer
```
Apple M1 Pro (IntegratedGPU) via Metal
     up_wbuf_queue_write_30_17 (20x) - cpu:452.85
     up_wbuf_queue_write_30_18 (20x) - cpu:312.94
     up_wbuf_queue_write_30_19 (20x) - cpu:262.84
     up_wbuf_queue_write_30_20 (20x) - cpu:254.42
     up_wbuf_queue_write_30_21 (20x) - cpu:222.75
     up_wbuf_queue_write_30_22 (20x) - cpu:220.64
     up_wbuf_queue_write_30_23 (20x) - cpu:210.47
     up_wbuf_queue_write_30_24 (20x) - cpu:213.65
     up_wbuf_queue_write_30_25 (20x) - cpu:209.93
     up_wbuf_queue_write_30_26 (20x) - cpu:208.37
     up_wbuf_queue_write_30_27 (20x) - cpu:219.17
     up_wbuf_queue_write_30_28 (20x) - cpu:220.32
     up_wbuf_queue_write_30_29 (20x) - cpu:235.77
     up_wbuf_queue_write_30_30 (20x) - cpu:255.31

    up_wbuf_write_mapped_30_17 (20x) - cpu:438.43
    up_wbuf_write_mapped_30_18 (20x) - cpu:499.46
    up_wbuf_write_mapped_30_19 (20x) - cpu:432.62
    up_wbuf_write_mapped_30_20 (20x) - cpu:323.31
    up_wbuf_write_mapped_30_21 (20x) - cpu:348.84
    up_wbuf_write_mapped_30_22 (20x) - cpu:298.18
    up_wbuf_write_mapped_30_23 (20x) - cpu:311.70
    up_wbuf_write_mapped_30_24 (20x) - cpu:289.96
    up_wbuf_write_mapped_30_25 (20x) - cpu:336.02
    up_wbuf_write_mapped_30_26 (20x) - cpu:313.62
    up_wbuf_write_mapped_30_27 (20x) - cpu:300.95
    up_wbuf_write_mapped_30_28 (20x) - cpu:311.04
    up_wbuf_write_mapped_30_29 (20x) - cpu:300.43
    up_wbuf_write_mapped_30_30 (20x) - cpu:274.61
```

On a Mac, the tipping point is at about 2**21 for queue_write,
and at 2**19 for write_mapped.

Also interesting is that with the 1GB buffer, uploading the full buffer
takes longer (consistently) for queue_write. So chunking, even if not needed, can be beneficial as well!

Another observation is that queue_write outperforms write_mapped, for a buffer
of this size.


## Conclusion

It seems safe to use a chunksize that is about 1/16th of the buffer size,
capped by a size of about 1MB.