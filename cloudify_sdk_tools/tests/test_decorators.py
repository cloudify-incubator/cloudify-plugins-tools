# pylint: disable=no-value-for-parameter

import unittest

from mock import Mock

from cloudify_sdk_tools.decorators import with_arguments
from cloudify_sdk_tools.exceptions import InvalidInputArgumentsError


class TestDecorators(unittest.TestCase):

    def setUp(self):
        # given
        self.a = 1
        self.b = 2
        self.c = 3
        self.d = 4
        self.dd = 44

        class MockCls(object):
            def __init__(self):
                self.log = Mock()
                self.type = 'mocked_type'

            @with_arguments('a', 'b', 'c', d=self.d)
            def func(self, a, b, c, d):
                return a, b, c, d

        self.instance = MockCls()

    def test_with_arguments_ok(self):
        # when
        result = self.instance.func(
            a=self.a,
            b=self.b,
            c=self.c
        )

        # then
        self.assertEquals(len(result), 4)
        self.assertEquals(result[0], self.a)
        self.assertEquals(result[1], self.b)
        self.assertEquals(result[2], self.c)
        self.assertEquals(result[3], self.d)

    def test_with_arguments_ok_duplicated_value(self):
        # when
        result = self.instance.func(
            a=self.a,
            b=self.b,
            c=self.c,
            d=self.dd
        )

        # then
        self.assertEquals(len(result), 4)
        self.assertEquals(result[0], self.a)
        self.assertEquals(result[1], self.b)
        self.assertEquals(result[2], self.c)
        self.assertEquals(result[3], self.dd)

    def test_with_arguments_nok_missing_param(self):
        # then
        with self.assertRaises(InvalidInputArgumentsError):
            # when
            self.instance.func(
                a=self.a,
                b=self.b
            )
