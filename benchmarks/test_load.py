"""测试 pydantic.BaseModel 与 LDModel 的 load 性能
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
    for _ in range(repeat):
        p = Point(**pd)
        l = Line(__root__=ld)


@timeit
def _test_case_2():
    for _ in range(repeat):
        p = Point.construct(**pd)
        l = Line.construct(__root__=ld)


@timeit
def _test_case_3():
    ld_ = {"vertices": ld}
    for _ in range(repeat):
        p = Point2.from_dict(pd)
        l = Line2.from_dict(ld_)


if __name__ == "__main__":
    _test_case_1()
    _test_case_2()
    _test_case_3()


# python 版本： 3.8

# 测试结果:
# func: _test_case_1 call times: 1 took: 4.2035 sec
# func: _test_case_2 call times: 1 took: 0.0002 sec
# func: _test_case_3 call times: 1 took: 0.8042 sec

# 结论: LDMixin 比 pydantic 有验证时要快，但比 pydantic 无验证时慢很多...
