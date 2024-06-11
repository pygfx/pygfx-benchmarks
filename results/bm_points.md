# Points

[bm_points.py](../benchmarks/bm_points.py)


### MacOS M1
```

                 points_1_100k (10x) - cpu:  6.46
               points_100_1000 (10x) - cpu:  9.56
               points_1000_100 (10x) - cpu: 18.17

                  points_10_10 (10x) - cpu:  3.35
                   points_1_1m (10x) - cpu: 25.44
```

It can be seen how using 100 objects in the scene does not affect performance too much.
However, for 1000 objects it becomes quite significant.


