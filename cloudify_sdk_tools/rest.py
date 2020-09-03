import copy
import os
import sys

from cloudify_rest_sdk.utility import process as send_rest_request

from .exceptions import TemplateNotFoundError


# Fix for flake 8
try:
    basestring
except NameError:
    basestring = str


class RestSDKClient(object):

    TEMPLATES_PATH = '{0}/templates/{1}/{2}.yaml'

    def __init__(self,
                 logger,
                 ip,
                 port=80,
                 user=None,
                 password=None,
                 ssl=False,
                 verify=False,
                 common_parameters=None,
                 module_name=__name__):

        def _str_to_bool(some_value):
            if isinstance(some_value, bool):
                return some_value
            elif isinstance(some_value, basestring):
                return some_value.lower() == 'true'
            else:
                return False

        self.logger = logger
        self.templates_path = os.path.dirname(
            sys.modules[module_name].__file__
        )
        self.common_parameters = common_parameters or {}

        self.hosts = ip if isinstance(ip, list) else [ip]
        self.port = port
        self.user = user
        self.password = password
        self.ssl = _str_to_bool(ssl)
        self.verify = _str_to_bool(verify)

    def _combine_parameters(self, parameters):
        result = copy.deepcopy(parameters)

        for k, v in self.common_parameters.iteritems():
            if k not in result:
                result[k] = v

        return result

    def _get_template(self, object_name, method_name):
        path = self.TEMPLATES_PATH.format(
            self.templates_path,
            object_name,
            method_name
        )

        if not os.path.isfile(path):
            raise TemplateNotFoundError(
                'REST request template supposed to be located in: '
                '"{0}" not found. '
                'Probably your plugin distribution is broken'
                .format(path)
            )

        with open(path, 'r') as f:
            return f.read()

    def _get_request(self, object_name, method_name, parameters):
        return {
            'params': self._combine_parameters(parameters),
            'template': self._get_template(object_name, method_name),
            'request_props': {
                'port': self.port,
                'ssl': self.ssl,
                'verify': self.verify,
                'hosts': self.hosts
            }
        }

    def _call(self, object_name, method_name, params):
        self.logger.info(
            'Sending {0} request for {1}'
            .format(method_name, object_name)
        )

        result = send_rest_request(
            **self._get_request(object_name, method_name, params)
        )['result_properties']

        self.logger.debug(
            'Received response for {0}.{1} request: {2}'.format(
                object_name,
                method_name,
                result
            )
        )

        return result

    def call(self, object_name, method_name, params):
        result = self._call(object_name, method_name, params)

        return result
