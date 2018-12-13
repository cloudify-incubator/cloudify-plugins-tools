import sys


class InputArgumentResolvingError(Exception):
    pass


class UnreachableApiError(Exception):
    pass


COMMON_NON_RECOVERABLE_EXCEPTIONS = (
    InputArgumentResolvingError,
    UnreachableApiError
)

COMMON_RECOVERABLE_EXCEPTIONS = ()


def reraise(exception_class, message=None):
    original_type, original_message, original_traceback = tuple(
        sys.exc_info()
    )

    if message:
        message = \
            '\nDetails: {0}\n' \
            'Original exception: {1}\n' \
            'Original exception message: {2}\n'\
            .format(message, original_type.__name__, original_message)

    else:
        message = original_message

    raise exception_class, message, original_traceback
