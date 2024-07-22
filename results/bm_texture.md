# pygfx texture

[bm_texture.py](../benchmarks/bm_texture.py)

## Introduction

This series of benchmarks is to test the performance of the pygfx texture for chunking.
It builds on top of the [bm_wgpu_texture.md](bm_wgpu_texture.md) benchmarks, to see
how these results end up in practice in pygfx, and to tweak chunking parameters.


## Full upload

```
Apple M1 Pro (IntegratedGPU) via Metal
       upload_tex1d_full_naive (20x) - cpu:  0.16 ms
   upload_tex1d_full_optimized (20x) - cpu:  0.12 ms
     upload_tex1d_full_noncont (20x) - cpu:  0.20 ms

       upload_tex2d_full_naive (20x) - cpu: 18.68 ms
   upload_tex2d_full_optimized (20x) - cpu: 12.89 ms
     upload_tex2d_full_noncont (20x) - cpu: 93.86 ms

       upload_tex3d_full_naive (20x) - cpu: 27.08 ms
   upload_tex3d_full_optimized (20x) - cpu: 25.98 ms
     upload_tex3d_full_noncont (20x) - cpu: 82.74 ms
```

In these benchmarks we see that the optimized (new) version
that avoids data-copies is indeed faster than the previous naive implementation.
It also shows that when the data is not contiguous, the upload is much slower.


## Partial uploads

```
        upload_tex1d_quarter_x (20x) - cpu:  0.11 ms
     upload_tex1d_two_eights_x (20x) - cpu:  0.18 ms

        upload_tex2d_quarter_x (20x) - cpu: 12.53 ms
        upload_tex2d_quarter_y (20x) - cpu:  2.93 ms
     upload_tex2d_two_eights_x (20x) - cpu: 12.14 ms
     upload_tex2d_two_eights_y (20x) - cpu:  3.00 ms
    upload_tex2d_four_eights_x (20x) - cpu: 11.37 ms
    upload_tex2d_four_eights_y (20x) - cpu:  6.01 ms
  upload_tex2d_chunk_stripes_x (20x) - cpu: 11.49 ms
  upload_tex2d_chunk_stripes_y (20x) - cpu:  6.43 ms

        upload_tex3d_quarter_x (20x) - cpu: 26.37 ms
        upload_tex3d_quarter_y (20x) - cpu: 26.34 ms
        upload_tex3d_quarter_z (20x) - cpu:  6.33 ms
     upload_tex3d_two_eights_x (20x) - cpu: 25.23 ms
     upload_tex3d_two_eights_y (20x) - cpu: 26.50 ms
     upload_tex3d_two_eights_z (20x) - cpu:  7.19 ms
    upload_tex3d_four_eights_x (20x) - cpu: 25.80 ms
    upload_tex3d_four_eights_y (20x) - cpu: 25.34 ms
    upload_tex3d_four_eights_z (20x) - cpu: 14.57 ms
  upload_tex3d_chunk_stripes_x (20x) - cpu: 24.66 ms
  upload_tex3d_chunk_stripes_y (20x) - cpu: 25.65 ms
  upload_tex3d_chunk_stripes_z (20x) - cpu: 12.77 ms
```

Here, we upload part of the texture, for various dimensions.

The results for 1D textures seem a bit off. Perhaps in part due to the small times.

For 2D, we can see that partitioning in the x-dimension (i.e. the non-contiguous dimension)
hurts performance, while in the y-dimension the performance is as expected, similar to buffer chunking.
Note that in these test we don't actually mangle numpy data: this only measures GPU uploading.

For 3D, we see something similar, but not the x and y dimension are both negatively affected, while
the z-dimension behaves as buffers do.

We can also see that the adverserial case of using stripes behaves well.


## Random uploads

```
          upload_tex2d_random8 (20x) - cpu:  0.56 ms
         upload_tex2d_random16 (20x) - cpu:  0.93 ms
         upload_tex2d_random32 (20x) - cpu:  1.53 ms
         upload_tex2d_random64 (20x) - cpu:  2.92 ms
        upload_tex2d_random128 (20x) - cpu:  5.33 ms
        upload_tex2d_random256 (20x) - cpu: 10.16 ms
        upload_tex2d_random512 (20x) - cpu: 13.21 ms
       upload_tex2d_random1024 (20x) - cpu: 12.65 ms
       upload_tex2d_random2048 (20x) - cpu: 11.68 ms

          upload_tex3d_random8 (20x) - cpu:  0.52 ms
         upload_tex3d_random16 (20x) - cpu:  0.96 ms
         upload_tex3d_random32 (20x) - cpu:  2.10 ms
         upload_tex3d_random64 (20x) - cpu:  3.50 ms
        upload_tex3d_random128 (20x) - cpu:  7.23 ms
        upload_tex3d_random256 (20x) - cpu: 19.00 ms
        upload_tex3d_random512 (20x) - cpu: 25.05 ms
       upload_tex3d_random1024 (20x) - cpu: 24.72 ms
       upload_tex3d_random2048 (20x) - cpu: 27.33 ms
       upload_tex3d_random4096 (20x) - cpu: 25.96 ms
```

These tests may represent the most realistic use-case. We don't want any of
these cases to take longer than simply uploading the whole texture.
The chunking/merging algorithm should be such that this does not happen.

The results show that the performance naturally climbs to that of a full chunk
upload.


## Uploading many textures

```
            upload_tex2d_100_textures (20x) - cpu: 19.19 ms
```

Uploading 100 textures that are 1/100 the size shows that there is overhead,
which is expected since chunking for textures is quite a bit more complex that it
is for buffers. The overhead is much smaller for full-texture uploads though
(which is what happens for every texture's first upload).
