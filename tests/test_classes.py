# -*- coding: UTF-8 -*-
"""
Created on 17.02.23

:author:     Martin Dočekal
"""
import unittest
from abc import ABC, abstractmethod

from classconfig.configurable import ConfigurableValue
from classconfig.classes import subclasses, sub_cls_from_its_name, get_configurable_attributes


class A:
    pass


class B(A):
    val = ConfigurableValue()
    pass


class C(A):
    pass


class D(B):
    pass


class E(C):
    pass


class F(D):
    pass


class G(E):
    pass


class H(F):
    val = ConfigurableValue()
    pass


class BAbc(B, ABC):
    @abstractmethod
    def abc_method(self):
        pass


class BaseOfAnotherConfigurableClass:
    c = ConfigurableValue()


class AnotherConfigurableClass(BaseOfAnotherConfigurableClass):
    d = ConfigurableValue(desc="description of d", user_default="abc")

    def __init__(self, c: str, d: str):
        self.c = c
        self.d = d


class TestSubclasses(unittest.TestCase):
    def test_subclasses(self):
        self.assertEqual(set(subclasses(A)), {B, C, D, E, F, G, H})

    def test_subclasses_abstract(self):
        self.assertEqual(set(subclasses(A, abstract_ok=True)), {B, C, D, E, F, G, H, BAbc})

    def test_subclasses_configurable(self):
        self.assertEqual(set(subclasses(A, configurable_only=True)), {B, D, F, H})

    def test_subclasses_configurable_abstract(self):
        self.assertEqual(set(subclasses(A, abstract_ok=True, configurable_only=True)), {B, D, F, H, BAbc})


class TestSubClsFromItsName(unittest.TestCase):

    def test_sub_cls_from_its_name(self):
        self.assertEqual(sub_cls_from_its_name(A, "B"), B)
        self.assertEqual(sub_cls_from_its_name(A, "C"), C)
        self.assertEqual(sub_cls_from_its_name(A, "D"), D)
        self.assertEqual(sub_cls_from_its_name(A, "E"), E)
        self.assertEqual(sub_cls_from_its_name(A, "F"), F)
        self.assertEqual(sub_cls_from_its_name(A, "G"), G)
        self.assertEqual(sub_cls_from_its_name(A, "H"), H)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting")

    def test_sub_cls_from_its_name_abstract(self):
        self.assertEqual(sub_cls_from_its_name(A, "BAbc", abstract_ok=True), BAbc)

        with self.assertRaises(ValueError):
            sub_cls_from_its_name(A, "NotExisting", abstract_ok=True)


class TestGetConfigurableAttributes(unittest.TestCase):
    def test_get_configurable_attributes(self):
        configurables = {"c": AnotherConfigurableClass.c, "d": AnotherConfigurableClass.d}
        res = get_configurable_attributes(AnotherConfigurableClass)
        self.assertSequenceEqual(configurables, res)
