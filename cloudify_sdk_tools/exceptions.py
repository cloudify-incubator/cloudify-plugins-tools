import sys

from cloudify_rest.rest_sdk import exceptions as cloudify_rest_sdk_exceptions
from requests import exceptions as requests_exceptions


class ClientInitializationError(Exception):
    pass


class ResourceProcessingError(Exception):
    pass


class TemplateNotFoundError(Exception):
    pass


class InvalidInputArgumentsError(Exception):

    MESSAGE_TEMPLATE = 'Mandatory input arguments: ' \
                       '{0} missing for "{1} {2}" API method invocation '

    def __init__(self, resource_name, function_name, missing_args):
        super(InvalidInputArgumentsError, self).__init__(
            self.MESSAGE_TEMPLATE.format(
                missing_args,
                function_name,
                resource_name
            )
        )


NON_RECOVERABLE_EXCEPTIONS = (
    cloudify_rest_sdk_exceptions.WrongTemplateDataException,
    cloudify_rest_sdk_exceptions.NonRecoverableResponseException,
    InvalidInputArgumentsError,
    TemplateNotFoundError,
    ResourceProcessingError
)

RECOVERABLE_EXCEPTIONS = (
    cloudify_rest_sdk_exceptions.ExpectationException,
    cloudify_rest_sdk_exceptions.RecoverableResponseException,
    cloudify_rest_sdk_exceptions.RecoverableStatusCodeCodeException,
    cloudify_rest_sdk_exceptions.RestSdkException,
    ClientInitializationError,
    requests_exceptions.HTTPError
)


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
