import sys
from traceback import format_tb
import unittest

from cloudify_sdk_tools import exceptions


class TestReraise(unittest.TestCase):

    def test_reraise_with_message(self):
        # given
        original_exception_message = 'blahblahblah'
        original_exception = RuntimeError(original_exception_message)
        final_exception_message = 'TERRIBLE ERROR !'

        # when
        original_traceback = None

        with self.assertRaises(exceptions.ResourceProcessingError):
            try:
                raise original_exception
            except RuntimeError:
                _, __, original_traceback = sys.exc_info()

                exceptions.reraise(
                    exceptions.ResourceProcessingError,
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

        with self.assertRaises(exceptions.ResourceProcessingError):
            try:
                raise original_exception
            except RuntimeError:
                _, __, original_traceback = sys.exc_info()
                exceptions.reraise(exceptions.ResourceProcessingError)

        # then
        _, exception, traceback = sys.exc_info()
        self.assertEquals(str(exception), original_exception_message)
        self.assertEquals(
            format_tb(traceback)[1:],
            format_tb(original_traceback)
        )


class InvalidInputArgumentsErrorTest(unittest.TestCase):

    def test_raise(self):
        # given
        resource_name = 'SomeResource'
        function_name = 'create'
        missing_args = ['important_parameter']

        # when
        try:
            raise exceptions.InvalidInputArgumentsError(
                resource_name,
                function_name,
                missing_args
            )

        # then
        except exceptions.InvalidInputArgumentsError as e:
            self.assertEquals(
                'Mandatory input arguments: '
                '{0} missing for "{1} {2}" API method invocation '
                .format(missing_args, function_name, resource_name),
                str(e)
            )
