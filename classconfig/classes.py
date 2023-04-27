# -*- coding: UTF-8 -*-
"""
Created on 17.02.23
Module with utils for working with classes itself.

:author:     Martin Dočekal
"""
import inspect
from typing import Type, List, TypeVar, Dict

from classconfig.base import ConfigurableAttribute

T = TypeVar("T")


def subclasses(cls_type: Type[T], abstract_ok: bool = False, configurable_only: bool = False) -> List[Type[T]]:
    """
    Returns all subclasses of given class.

    :param cls_type: parent class
    :param abstract_ok: if True also abstract classes will be returned
    :param configurable_only: if True only classes that are configurable will be returned
        configurable class is such that has at least one configurable attribute
    :return: all subclasses of given class
    """
    res = []
    for sub_cls in cls_type.__subclasses__():
        if (abstract_ok or not inspect.isabstract(sub_cls)) and \
                (not configurable_only or len(get_configurable_attributes(sub_cls)) > 0):
            res.append(sub_cls)
        res.extend(subclasses(sub_cls, abstract_ok, configurable_only))
    return res


def sub_cls_from_its_name(parent_cls: Type[T], name: str, abstract_ok: bool = False) -> Type[T]:
    """
    Searches all subclasses of given classes (also the class itself) and returns class with given name.

    :param parent_cls: parent class whose subclasses should be searched
    :param name: name of searched subclass
    :param abstract_ok: if True also abstract classes will be returned
    :return: subclass of given name
    :raise: ValueError when name with given subclass doesn't exist
    """

    if name == parent_cls.__name__ and (abstract_ok or not inspect.isabstract(parent_cls)):
        return parent_cls

    for c in subclasses(parent_cls, abstract_ok=abstract_ok):
        if c.__name__ == name:
            return c

    raise ValueError(f"Invalid subclass name {name} for parent class {parent_cls}")


def get_configurable_attributes(c: Type) -> Dict[str, ConfigurableAttribute]:
    """
    For given class returns all configurable attributes. Also obtains these from parents recursively.

    :param c: class to search the annotations
    :return: dict with name as key, and the configurable attribute as value
    """

    configurables = {}
    for base in c.__bases__:
        configurables.update(get_configurable_attributes(base))

    for v_name in vars(c):
        v = getattr(c, v_name)
        if isinstance(v, ConfigurableAttribute):
            configurables[v_name] = v

    return configurables
