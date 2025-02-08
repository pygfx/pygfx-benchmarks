from pygfx import Group
from _benchmark import benchmark, run_all


@benchmark(20)
def bm_transforms_100_children(canvas):
    group = Group()
    for i in range(100):
        group.add(Group())

    yield

    while True:
        group.local.x += 1
        yield

@benchmark(20)
def bm_transforms_1000_children(canvas):
    group = Group()
    for i in range(1000):
        group.add(Group())

    yield

    while True:
        group.local.x += 1
        yield

@benchmark(20)
def bm_transforms_1000_children_with_50_grandchildren(canvas):
    group = Group()
    for i in range(1000):
        g = Group()
        group.add(g)
        for _ in range(50):
            g.add(Group())

    yield

    while True:
        group.local.x += 1
        yield


if __name__ == "__main__":
    run_all(globals())
