# coding: utf-8
# Created on: 09.02.2017
# Author: Roman Miroshnychenko aka Roman V.M. (romanvm@yandex.ua)

import os
import sys
from unittest import TestCase

workdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(workdir))

import pydocsgen
import foo_module


class PydocsgenTestCase(TestCase):
    def test_analyze_module(self):
        results = pydocsgen.analyze_module(foo_module)
        self.assertEqual(len(results.variables), 1)
        self.assertEqual(results.variables[0], 'my_variable')
        self.assertEqual(len(results.functions), 1)
        self.assertEqual(results.functions[0], 'my_function')
        self.assertEqual(len(results.classes), 1)
        self.assertEqual(results.classes[0], 'MyClass')
