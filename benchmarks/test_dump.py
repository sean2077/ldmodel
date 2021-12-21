"""测试 pydantic.BaseModel 与 LDModel 的 dump 性能
"""

import time
from typing import List

from ldmodel import LDModel
from pydantic import BaseModel


def timeit(f, call_times_cache={}):
    def timed(*args, **kw):

        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        call_times_cache[f.__name__] = call_times_cache.get(f.__name__, 0) + 1

        print(
            f"func: {f.__name__} call times: {call_times_cache[f.__name__]} took: {te - ts:.4f} sec"
        )
        return result

    return timed


class Point(BaseModel):
    x: float
    y: float


class Line(BaseModel):
    __root__: List[Point]


class Point2(LDModel):
    x: float
    y: float


class Line2(LDModel):
    vertices: List[Point]


pd = {"x": 1, "y": 2}
ld = [{"x": 1, "y": 2} for _ in range(10000)]

repeat = 100


@timeit
def _test_case_1():
    p = Point(**pd)
    l = Line(__root__=ld)

    for _ in range(repeat):
        _ = p.json()
        _ = l.json()


@timeit
def _test_case_2():
    p = Point2.from_dict(pd)
    l = Line2.from_dict({"vertices": ld})

    for _ in range(repeat):
        _ = p.to_json()
        _ = l.to_json()


if __name__ == "__main__":
    _test_case_1()
    _test_case_2()


# python 版本： 3.8

# 测试结果:
# func: _test_case_1 call times: 1 took: 3.8477 sec
# func: _test_case_2 call times: 1 took: 5.2301 sec

# 结论: LDMixin 比 pydantic 慢...
