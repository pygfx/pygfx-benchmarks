# Scene-graph traversal: incremental index results

> See also [`render_loop_optimizations.md`](render_loop_optimizations.md) for the
> per-commit progression (main → tip) of the render-loop optimizations on both an
> Apple M5 Max and a low-power Intel i7-1180G7 (~15.7× / ~14× for a moving camera).


Benchmark: [`benchmarks/bm_scene_index.py`](../../benchmarks/bm_scene_index.py)

These numbers compare the per-render scene-graph traversal cost in pygfx
**before** and **after** the incremental scene-index change (pygfx issue #1298).

* **baseline** — `pygfx/pygfx@main` (`FlatScene` walks the whole tree every render)
* **work** — the `incremental-scene-index` branch (categorization maintained at
  mutation time; `FlatScene` reads flat lists)

The reported figure is the **median of 200 `FlatScene(scene)` constructions**
(pure CPU, no GPU; GC disabled during sampling, 5 warm-up iterations). Lower is
better; *speedup* = baseline / work. Raw output is in the sibling `*.txt` files.

## Apple M5 Max — macOS 26.4 (dev workstation)

| scene | baseline (µs) | work (µs) | speedup |
|---|---:|---:|---:|
| flat_500 | 319.7 | 282.4 | 1.13× |
| flat_2000 | 1,286.8 | 1,160.7 | 1.11× |
| flat_5000 | 3,405.8 | 2,996.7 | 1.14× |
| flat_10000 | 7,859.5 | 6,900.3 | 1.14× |
| grouped_50x10 | 368.8 | 290.5 | 1.27× |
| grouped_200x10 | 1,447.8 | 1,207.4 | 1.20× |
| grouped_500x10 | 3,888.5 | 3,082.8 | 1.26× |
| deep_50 | 83.2 | 38.1 | 2.18× |
| deep_200 | 528.7 | 141.3 | 3.74× |
| deep_500 | 2,315.4 | 366.4 | 6.32× |

## Intel i7-1180G7 @ 1.30GHz — Ubuntu 26.04 (low-power CPU)

| scene | baseline (µs) | work (µs) | speedup |
|---|---:|---:|---:|
| flat_500 | 1,630.8 | 1,257.0 | 1.30× |
| flat_2000 | 6,596.5 | 5,106.4 | 1.29× |
| flat_5000 | 21,908.5 | 18,124.8 | 1.21× |
| flat_10000 | 51,325.3 | 41,383.0 | 1.24× |
| grouped_50x10 | 1,888.8 | 1,364.8 | 1.38× |
| grouped_200x10 | 7,589.9 | 5,484.6 | 1.38× |
| grouped_500x10 | 24,723.5 | 18,688.8 | 1.32× |
| deep_50 | 355.9 | 153.4 | 2.32× |
| deep_200 | 2,310.9 | 589.7 | 3.92× |
| deep_500 | 11,313.8 | 1,640.1 | 6.90× |

## Takeaways

* The win **scales with scene structure**: flat scenes ~1.1–1.3×, grouped
  scenes ~1.2–1.4×, deeply nested scenes up to **~6.3–6.9×**. Deep graphs benefit
  most because the recursive walk and `group_order` propagation are eliminated.
* The win is **larger on the weaker CPU** across the board (e.g. flat ~1.2–1.3×
  on the i7 vs ~1.1× on the M5; grouped ~1.3–1.4× vs ~1.2–1.3×). On a slow CPU the
  Python scene-walk is a bigger share of frame time, so removing it matters more —
  exactly the embedded / low-power target.
* **Full-render control** (the `@benchmark` functions in the same file) shows no
  measurable change: at realistic sizes a full frame is dominated by GPU
  submission and per-object uniform updates, so the traversal saving is below the
  render noise floor. The optimization pays off for **CPU-bound, scene-graph-heavy
  render loops** (many objects and/or deep hierarchies, weak CPU), not for
  GPU-bound rendering.
