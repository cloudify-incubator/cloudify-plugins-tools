import sys
from traceback import format_tb
import unittest

from cloudify_plugin_tools import exceptions


class TestReraise(unittest.TestCase):

    def test_reraise_with_message(self):
        # given
        original_exception_message = 'blahblahblah'
        original_exception = RuntimeError(original_exception_message)
        final_exception_message = 'TERRIBLE ERROR !'

        # when
        original_traceback = None

        with self.assertRaises(exceptions.UnreachableApiError):
            try:
                raise original_exception
            except RuntimeError:
                _, __, original_traceback = sys.exc_info()

                exceptions.reraise(
                    exceptions.UnreachableApiError,
                    final_exception_message
                )

        # then
        _, exception, traceback = sys.exc_info()
        message = str(exception)
        self.assertTrue(
            'Details: {0}'.format(final_exception_message)
            in message
        )
        self.assertTrue('Original exception: RuntimeError' in message)
        self.assertTrue(
            'Original exception message: {0}'
            .format(original_exception_message)
            in message
        )

        self.assertEquals(
            format_tb(traceback)[1:],
            format_tb(original_traceback)
        )

    def test_reraise_no_message(self):
        # given
        original_exception_message = 'blahblahblah'
        original_exception = RuntimeError(original_exception_message)

        # when
        original_traceback = None

        with self.assertRaises(exceptions.UnreachableApiError):
            try:
                raise original_exception
            except RuntimeError:
                _, __, original_traceback = sys.exc_info()
                exceptions.reraise(exceptions.UnreachableApiError)

        # then
        _, exception, traceback = sys.exc_info()
        self.assertEquals(str(exception), original_exception_message)
        self.assertEquals(
            format_tb(traceback)[1:],
            format_tb(original_traceback)
        )
