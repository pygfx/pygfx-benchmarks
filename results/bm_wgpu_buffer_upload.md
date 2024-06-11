# wgpu buffer upload

[bm_wgpu_buffer_upload.py](../benchmarks/bm_wgpu_buffer_upload.py)


## Introduction

The purpose of this benchmark is to gain insight into how different approaches for
uploading data compare.

It's not possible to directly upload data to a buffer that has storage
or uniform usage. An intermediate mappable buffer is needed to move the
data.

We look into chunking a little bit, to get a first impression, but investigate it in detail in a separate benchmark.


## The different upload methods

### queue_write

The `device.queue.write_buffer()` method is probbaly the easiest way
to upload data. It's a higher level API than the buffer mapping
approaches. Under water it likely uses a temporary mappable buffer,
similar to the other approaches, but wgpu-core can make optimizations
where possible. It is not very flexible though.


### with_data

When creating a new buffer, it can be marked as mapped from the start.
In wgpu-py we added an extra convenience method
`device.create_buffer_with_data()` that creates a mapped buffer, writes
data to it, and then unmaps it. This is expected to be fast, because
there is no need to wait for the buffer to become mapped.


### write_mapped

This is wgpu-py's safe approach to writing buffer data.


### mapped_range

This is an experimental implementation of mapped arrays. We avoided this approach
because when unmapped, the array becomes invalid and using it can cause a segfault.
But in some situations it may be beneficial. We want to know when, and how much it matters.

When simply writing an array that already exists, it has no benefit over write_mapped.
This is why we leave this approach out of most tests.



## Simply setting the data

In this benchmark, the whole buffer data is simply replaced.

MacOS M1:
```
       up_wbuf_queue_write_set (20x) - cpu: 19.30
         up_wbuf_with_data_set (20x) - cpu: 28.38
      up_wbuf_write_mapped_set (20x) - cpu: 21.08
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
       up_wbuf_queue_write_set (20x) - cpu: 21.99
         up_wbuf_with_data_set (20x) - cpu: 29.82
      up_wbuf_write_mapped_set (20x) - cpu: 37.04
```

Interestingly, the `with_data` approach performs significantly worse.
The `queue_write` method performs the best. On the M1 this is only a bit,
but with a GeForce `write_mapped` performs quite bad. Would this be
because the GPU has its own memory?


## Chunked

In this benchmark, the whole buffer data is replaced, but in chunks (1000 pieces).

MacOS M1:
```
   up_wbuf_queue_write_chunked (20x) - cpu: 42.56
    up_wbuf_with_data_chuncked (20x) - cpu: 91.85
  up_wbuf_write_mapped_chunked (20x) - cpu: 24.46
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
```
   up_wbuf_queue_write_chunked (20x) - cpu: 46.45
    up_wbuf_with_data_chuncked (20x) - cpu:102.97
  up_wbuf_write_mapped_chunked (20x) - cpu: 52.69
```

We see the same bad performance of `with_data`. The `queue_write` approach is affected
by looping over the chunks, processing them one by one. On the M1 The `write_mapped` is definetly the fastest,
because the buffer is still mapped/unmapped, and then copied as a whole.
On the GeForce, just writing/copying data in chunks shows significant overhead, and the `queue_write` approach is still the fastest. With UHD Graphics the `write_mapped` is the fastest approach.


## Chuncked aligned

Same as the above, but with pieces of `n` times the Unix page size.
MacOS M1:
```
   up_wbuf_queue_write_aligned (20x) - cpu: 42.08
     up_wbuf_with_data_aligned (20x) - cpu: 97.67
  up_wbuf_write_mapped_aligned (20x) - cpu: 24.93
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
```
   up_wbuf_queue_write_aligned (20x) - cpu: 51.66
     up_wbuf_with_data_aligned (20x) - cpu:106.20
  up_wbuf_write_mapped_aligned (20x) - cpu: 54.40
```


This shows that aligning by page size does not seem to affect performance.

## Quarter

Im this benchmark, a quarter of the data is uploaded. It is repeated for the 1st and 3d quarter, just in case.

For the `with_data` and `write_mapped`
approachs, the temp buffer is one quarted of the full size.

MacOS M1:
```
  up_wbuf_queue_write_quarter1 (20x) - cpu:  6.06
    up_wbuf_with_data_quarter1 (20x) - cpu:  7.75
 up_wbuf_write_mapped_quarter1 (20x) - cpu:  6.88
  up_wbuf_queue_write_quarter3 (20x) - cpu:  6.01
    up_wbuf_with_data_quarter3 (20x) - cpu:  8.04
 up_wbuf_write_mapped_quarter3 (20x) - cpu:  6.78
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
```
  up_wbuf_queue_write_quarter1 (20x) - cpu:  8.53
    up_wbuf_with_data_quarter1 (20x) - cpu: 12.33
 up_wbuf_write_mapped_quarter1 (20x) - cpu: 10.31
  up_wbuf_queue_write_quarter3 (20x) - cpu:  8.49
    up_wbuf_with_data_quarter3 (20x) - cpu: 11.21
 up_wbuf_write_mapped_quarter3 (20x) - cpu:  9.76
```


We can see that the performance increases about 4x, as can be expected.


## Setting data to a computation result

If the data is a result of a computation, then being able to write the result
directly to the mapped array can safe time. In this benchmark we use
`np.add(data1, data2, out=mapped_array)` in the `mapped_range`  approach.

MacOS M1:
```
       up_wbuf_queue_write_add (20x) - cpu: 31.01
      up_wbuf_write_mapped_add (20x) - cpu: 34.13
      up_wbuf_mapped_range_add (20x) - cpu: 23.74
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
```
       up_wbuf_queue_write_add (20x) - cpu:108.55
      up_wbuf_write_mapped_add (20x) - cpu:124.42
      up_wbuf_mapped_range_add (20x) - cpu: 94.66
```

It can be seen that adding the data affects the performance of the `queue_write`  and `write_mapped` approaches.
The performance of `mapped_range` is significantly better because it avoids a data copy.

This case is somewhat of a niche, but people in this niche probably care about performance to
be able to want to apply this approach ...


## Setting data using step or mask

The `mapped_range` approach allows for more flexible setting of the data, like
`mapped_array[::2] = data[::2]` and `mapped_array[mask] = data[mask]`

MacOS M1:
```
   up_wbuf_mapped_range_inter2 (20x) - cpu: 36.71
  up_wbuf_mapped_range_masked2 (20x) - cpu:481.81
```

Win 11 laptop with NVIDIA GeForce RTX 2070:
```
   up_wbuf_mapped_range_inter2 (20x) - cpu: 75.49
  up_wbuf_mapped_range_masked2 (20x) - cpu:731.32
```

This shows that tricks like this don't help at all. We're much better off by
just uploading the whole array. Very good to know though!


## Summary

NEEDS MORE TESTS ON OTHER MACHINES

The `device.create_buffer_with_data()` method, and its sibling
`device.create_buffer(.., mapped_at_creation=True)` are somehow quite slow.

The `buffer._experimental_get_mapped_range()` method does not help, except for the
niche case of using it for the target of a computation: `np.something(out=mapped_array)`.
Maybe enough to pubicly expose it in wgpu, but no use in pygfx.

The `queue.write_buffer()` is the fastest approach to set a whole buffer,
but takes a hit when chunking is applied.

The `queue.write_mapped()` provides a flexible approach that - on some devices - performs better when chunking is applied.


