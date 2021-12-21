import codecs
import json
import re
import sys
from typing import Any, Dict, List


def snake_to_camel(s: str) -> str:
    first, *others = s.split("_")
    return first + "".join(word.title() for word in others)


def snake_to_title(s: str) -> str:
    return "".join(word.title() for word in s.split("_"))


pat_camel = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake(s: str) -> str:
    return pat_camel.sub("_", s).lower()


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class LoadModel:
    __ldmodel_udl = {}  # user defined loader

    @staticmethod
    def _load(type_, name, value, cls, **kwargs) -> Any:
        # * forward reference type
        if isinstance(type_, str):
            type_ = sys.modules[cls.__module__].__dict__.get(type_)
        if hasattr(type_, "__forward_arg__"):
            type_ = sys.modules[cls.__module__].__dict__.get(type_.__forward_arg__)

        # * specified generic type
        if not hasattr(type_, "__origin__"):
            if value is None:
                return type_()  # default value of type

            if type_ in cls.__ldmodel_udl:
                f = cls.__ldmodel_udl.get(type_)
                return f(value, **kwargs)

            if issubclass(type_, LoadModel):
                return type_.from_dict(value, **kwargs)

            return value

        # * __origin__ keeps a reference to a type that was subscribed,
        #   e.g., Union[T, int].__origin__ == Union;`
        o_type = type_.__origin__
        g_type = type_.__args__

        if o_type in (list, List):
            if value is None:
                return []
            return [
                LoadModel._load(g_type[0], f"{name}.{i}", v, cls, **kwargs)
                for i, v in enumerate(value)
            ]

        if o_type in (dict, Dict):
            if value is None:
                return {}
            return {
                k: LoadModel._load(g_type[1], f"{name}.{k}", v, cls, **kwargs)
                for k, v in value.items()
            }

        raise RuntimeError(f"This generics is not supported `{o_type}`")

    @classmethod
    def from_dict(cls, d: dict, **kwargs):
        if isinstance(d, cls):
            return d

        instance = cls()

        for n, t in cls.__annotations__.items():
            # 认为字段的snake风格和camel风格等价
            arg_v = d.get(n) or d.get(camel_to_snake(n)) or d.get(snake_to_camel(n))
            def_v = getattr(instance, n, None)
            setattr(instance, n, LoadModel._load(t, n, arg_v or def_v, cls, **kwargs))

        return instance

    @classmethod
    def from_json(cls, s: str, **kwargs):
        return cls.from_dict(json.loads(s), **kwargs)

    @classmethod
    def from_jsonf(cls, fpath: str, **kwargs):
        with codecs.open(fpath, mode="r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f), **kwargs)


class DumpModel:
    __ldmodel_udd = {}  # user defined dumper

    def _dump(self, value, **kwargs):

        if type(value) in self.__ldmodel_udd:
            f = self.__ldmodel_udd.get(type(value))
            return f(value, **kwargs)

        if isinstance(value, DumpModel):
            return value.to_dict(**kwargs)

        if isinstance(value, list):
            return [self._dump(i, **kwargs) for i in value]

        if isinstance(value, dict):
            # 过滤`__`前缀的变量和无法json序列化的成员
            return {
                k: self._dump(v, **kwargs)
                for k, v in value.items()
                if not k.startswith("__")
            }

        # 过滤无法json序列化的成员
        if is_jsonable(value):
            return value

        return None

    def to_dict(self, **kwargs) -> dict:
        return self._dump(self.__dict__, **kwargs)

    def to_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(**kwargs))

    def to_pretty_json(self, **kwargs) -> str:
        return json.dumps(self.to_dict(**kwargs), indent=4)

    def to_jsonf(self, fpath: str, **kwargs):
        with codecs.open(fpath, mode="w", encoding="utf-8") as f:
            json.dump(self.to_dict(**kwargs), f)

    def __repr__(self):
        return self.to_pretty_json()


class LDModel(LoadModel, DumpModel):
    pass
