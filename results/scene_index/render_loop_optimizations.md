# Render-loop optimizations: per-commit progression

Benchmark: [`benchmarks/bm_render_loop.py`](../../benchmarks/bm_render_loop.py) —
per-frame `FlatScene(scene, view_matrix) + sort()` for a large scene, with a
**moving camera** (the realistic case: the view matrix changes every frame) and
**without a camera** (`sort_objects=False`). This is the CPU work the renderer
does each frame before issuing GPU draws.

**Scene:** 3000 groups × 10 points = 30 000 renderables (~33 000 objects incl.
groups + lights). Figure = median of 30 frames, GC disabled, after warm-up.
Lower is better. `step` = speedup vs the previous commit; `cumulative` = vs `main`.

Each row is a commit on [pygfx#1298 / PR #13](https://github.com/hmaarrfk/pygfx/pull/13):

0. `main` — baseline (per-render scene-graph walk; per-object distance + Python sort)
1. **scene-index** — maintain a categorized index incrementally; render reads flat lists
2. **vectorize** — batched `vec_transform` + `np.lexsort` instead of per-object
3. **cache** — cache the camera-independent renderable structure across frames
4. **skip-id** — assign ids / `_update_object` only for new/moved objects, in one sweep

Raw output: [`render_loop_percommit_apple-m5-max.txt`](render_loop_percommit_apple-m5-max.txt),
[`render_loop_percommit_nano.txt`](render_loop_percommit_nano.txt).

## Apple M5 Max — macOS 26.4

**Moving camera**

| commit | µs | step | cumulative |
|---|---:|---:|---:|
| 0 main | 74,424 | — | 1.00× |
| 1 scene-index | 67,966 | 1.10× | 1.10× |
| 2 vectorize | 35,621 | 1.91× | 2.09× |
| 3 cache | 6,880 | 5.18× | 10.82× |
| 4 skip-id | 4,740 | 1.45× | **15.70×** |

**No camera** (`sort_objects=False`)

| commit | µs | step | cumulative |
|---|---:|---:|---:|
| 0 main | 35,543 | — | 1.00× |
| 1 scene-index | 25,380 | 1.40× | 1.40× |
| 2 vectorize | 26,895 | 0.94× | 1.32× |
| 3 cache | 4,055 | 6.63× | 8.77× |
| 4 skip-id | 4,307 | 0.94× | 8.25× |

## Intel i7-1180G7 @ 1.30GHz — Ubuntu 26.04 (low-power)

**Moving camera**

| commit | µs | step | cumulative |
|---|---:|---:|---:|
| 0 main | 439,336 | — | 1.00× |
| 1 scene-index | 388,941 | 1.13× | 1.13× |
| 2 vectorize | 210,739 | 1.85× | 2.08× |
| 3 cache | 52,549 | 4.01× | 8.36× |
| 4 skip-id | 31,240 | 1.68× | **14.06×** |

**No camera** (`sort_objects=False`)

| commit | µs | step | cumulative |
|---|---:|---:|---:|
| 0 main | 179,203 | — | 1.00× |
| 1 scene-index | 150,986 | 1.19× | 1.19× |
| 2 vectorize | 163,416 | 0.92× | 1.10× |
| 3 cache | 28,998 | 5.64× | 6.18× |
| 4 skip-id | 29,749 | 0.97× | 6.02× |

## What each commit buys (consistent across both machines)

* **scene-index** — modest here (1.1–1.4×): this is a *flat, depth-2* grouped
  scene, so there is little tree to walk. Its large wins are deep hierarchies
  (up to ~7× in the FlatScene micro-benchmark), not this shape.
* **vectorize** — ~1.9× with a moving camera (replaces 30k per-object
  `vec_transform` with one matmul + `lexsort`). No effect without a camera
  (~0.93× = noise) — correct, since there is no distance to compute.
* **cache** — the single biggest lever, **~4–6.6×**, and it helps both paths:
  it eliminates the per-frame gather of materials, positions and wrapper
  allocation.
* **skip-id** — ~1.45–1.68× **only with a moving camera**; flat without one.
  It merges the all-objects id/transform loop *and* the renderable-position
  refresh into one sweep — the moving path had two O(N) scans to collapse, the
  no-camera path only had one.

**Bottom line:** `main` → tip is **~15.7× on the M5** and **~14× on nano** for a
moving camera (~8× / ~6× without one). The win is slightly larger *relative* on
the M5, but the *absolute* saving is far bigger on the low-power CPU:
439 ms → 31 ms per frame — roughly a 2 fps → 32 fps swing in the CPU portion of
the frame for a 33k-object scene.
